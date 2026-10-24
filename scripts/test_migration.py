"""Lossless migration checks on disposable Chinese-path fixtures."""
import hashlib
import os
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('migrate_legacy.py')
CLI = Path(__file__).with_name('experience.py')


class Migration(unittest.TestCase):
    @unittest.skipUnless(os.name == 'nt', 'Windows drive semantics')
    def test_cross_drive_private_asset_link_stays_absolute(self):
        import migrate_legacy
        root = Path('D:/library')
        value = '[原始素材](C:/素材/照片.jpg)'
        result = migrate_legacy.rebase(value, Path('D:/原文.md'), root / 'cases/a/history.md', {}, {}, root)
        self.assertEqual(result, value)

    def test_lossless_partition_prompt_preservation_links_and_repeat(self):
        with tempfile.TemporaryDirectory(prefix='中文迁移 test ') as tmp:
            base = Path(tmp); legacy = base / '文生视频较长视频直出.md'; lib = base / 'video-experience'
            original = ('# 历史\r\n\r\n<a id="bank"></a>\r\n## 银行\r\n'
                        '[旧跨章链接](#map)\r\n```text\r\n原始提示词 不得改字。\r\n```\r\n'
                        '<a id="map"></a>\r\n## 地图\r\n[旧文件](missing.mp4)\r\n').encode('utf-8')
            legacy.write_bytes(original)
            plan = {'segments': [{'start': 1, 'end': 8, 'target': 'cases/bank/history.md'},
                                 {'start': 9, 'end': 11, 'target': 'cases/map/history.md'}],
                    'projects': [{'id': 'bank', 'metadata': {'title': '银行', 'sources': ['history.md']}},
                                 {'id': 'map', 'metadata': {'title': '地图', 'sources': ['history.md']}}]}
            pp = base / '计划.json'; pp.write_text(json.dumps(plan, ensure_ascii=False), encoding='utf-8')
            command = [sys.executable, '-X', 'utf8', str(SCRIPT), '--legacy', str(legacy), '--library', str(lib), '--plan', str(pp)]
            for _ in range(2):
                result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual((lib / 'archives/original-backup.md').read_bytes(), original)
            self.assertEqual(len(list((lib / 'events').glob('*.json'))), 2)
            bank = (lib / 'cases/bank/history.md').read_text(encoding='utf-8')
            self.assertIn('原始提示词 不得改字。', bank)
            self.assertIn('../map/history.md#map', bank)
            self.assertIn('id="bank"', legacy.read_text(encoding='utf-8'))
            manifest = json.loads((lib / 'archives/migration-manifest.json').read_text(encoding='utf-8'))
            self.assertEqual(manifest['original_sha256'], hashlib.sha256(original).hexdigest())
            self.assertEqual(manifest['coverage_lines'], 11)
            check = subprocess.run([sys.executable, '-X', 'utf8', str(CLI), 'check', '--library', str(lib)], capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            self.assertTrue(json.loads(check.stdout)['historical_link_warnings'])

    def test_invalid_partition_or_path_does_not_replace_legacy(self):
        with tempfile.TemporaryDirectory(prefix='迁移保护 ') as tmp:
            base = Path(tmp); legacy = base / '原文.md'; legacy.write_text('one\ntwo\n', encoding='utf-8')
            plan = base / 'bad.json'
            plan.write_text(json.dumps({'segments': [{'start': 1, 'end': 1, 'target': '../outside.md'}], 'projects': []}), encoding='utf-8')
            result = subprocess.run([sys.executable, '-X', 'utf8', str(SCRIPT), '--legacy', str(legacy), '--library', str(base / 'lib'), '--plan', str(plan)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(legacy.read_text(encoding='utf-8'), 'one\ntwo\n')
            self.assertFalse((base / 'outside.md').exists())

    def test_revision_requires_explicit_flag_and_preserves_previous_manifest(self):
        import migrate_legacy
        with tempfile.TemporaryDirectory(prefix='迁移修订 ') as tmp:
            base = Path(tmp); legacy = base / '历史.md'; lib = base / 'lib'
            legacy.write_text('# 原文\n内容\n', encoding='utf-8')
            plan = {'segments': [{'start': 1, 'end': 2, 'target': 'cases/a/history.md'}],
                    'projects': [{'id': 'a', 'metadata': {'title': '原始案例'}}]}
            migrate_legacy.migrate(legacy, lib, plan)
            previous = (lib / 'archives/migration-manifest.json').read_bytes()
            revised = {**plan, 'segments': [{'start': 1, 'end': 2, 'target': 'cases/a/history.md'}], 'revision_note': '补充迁移说明'}
            with self.assertRaises(ValueError):
                migrate_legacy.migrate(legacy, lib, revised)
            migrate_legacy.migrate(legacy, lib, revised, revise_plan=True)
            copies = list((lib / 'archives/migration-revisions').glob('*/migration-manifest.json'))
            self.assertEqual(len(copies), 1)
            self.assertEqual(copies[0].read_bytes(), previous)


if __name__ == '__main__':
    unittest.main(verbosity=2)
