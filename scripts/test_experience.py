"""Behavioral CLI checks; all mutations stay in TemporaryDirectory copies."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('experience.py')


class ExperienceFlow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='视频经验 test ')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.lib = self.base / 'video-experience'

    def cli(self, *args, ok=True, env=None):
        result = subprocess.run([sys.executable, '-X', 'utf8', str(SCRIPT), *map(str, args)],
                                capture_output=True, text=True, encoding='utf-8', env=env)
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def init(self):
        self.cli('init', '--library', self.lib, '--entry', self.base / '文生视频较长视频直出.md')

    def event(self, ident, kind, project='test-film', **data):
        req = {'event_id': ident, 'project_id': project, 'kind': kind, 'data': data}
        p = self.base / '事件.json'
        p.write_text(json.dumps(req, ensure_ascii=False), encoding='utf-8')
        return p

    def apply(self, ident, kind, project='test-film', ok=True, env=None, **data):
        return self.cli('apply', '--library', self.lib, '--request',
                        self.event(ident, kind, project, **data), ok=ok, env=env)

    def create(self, ident='create-1', project='test-film', **metadata):
        self.apply(ident, 'create', project, metadata={'title': '中文短片',
                   'tags': ['节奏', '形态变化'], 'constraints': ['仅本片无BGM'], **metadata})

    def state(self, project='test-film'):
        return json.loads((self.lib / 'cases' / project / 'project.json').read_text(encoding='utf-8'))

    def test_new_project_retrieves_relevant_experience_without_copying_constraints(self):
        self.init()
        self.create()
        self.apply('review-1', 'review', observations=['只检查了抽帧'],
                   learnings=[{'id': 'DTV-L001', 'scope': 'cross_project', 'title': '节奏预算',
                               'applies_to': ['节奏'], 'problem': '事件过多', 'recommendation': '省略搬运',
                               'evidence': ['cases/test-film/CASE.md'], 'validation': 'recommendation',
                               'limitations': ['未生成验证'], 'counterexamples': []}])
        self.create('create-2', 'other-film', tags=['音频'], constraints=['本片需要歌曲'])
        out = json.loads(self.cli('read', '--library', self.lib, '--query', '节奏', '--limit', 2).stdout)
        self.assertEqual(out['projects'][0]['id'], 'test-film')
        self.assertIn('DTV-L001', [x['id'] for x in out['learnings']])
        self.assertEqual(self.state('other-film')['metadata']['constraints'], ['本片需要歌曲'])
        self.assertEqual(self.state()['status'], 'active')
        self.cli('check', '--library', self.lib)

    def test_explicit_close_without_final_video_and_repeat_are_idempotent(self):
        self.init(); self.create()
        self.apply('iteration-1', 'iterate', version='V01', prompt_text='完整提示词\n无省略。',
                   submission_status='unconfirmed', changes=['首次'], validation_goals=['核实表演'])
        self.apply('close-1', 'close', user_statement='本视频制作到此结束',
                   completion_confirmed=True, final_version='V01', user_evaluation='用户宣布结束',
                   unresolved=['没有最终视频，画面未核实'], learnings=[])
        state = self.state()
        self.assertEqual(state['status'], 'closed')
        self.assertFalse(state['closures'][0]['final_video_verified'])
        self.assertEqual(state['closures'][0]['unresolved'], ['没有最终视频，画面未核实'])
        before = {p.name: p.read_bytes() for p in (self.lib / 'events').glob('*.json')}
        self.apply('close-1', 'close', user_statement='本视频制作到此结束',
                   completion_confirmed=True, final_version='V01', user_evaluation='用户宣布结束',
                   unresolved=['没有最终视频，画面未核实'], learnings=[])
        after = {p.name: p.read_bytes() for p in (self.lib / 'events').glob('*.json')}
        self.assertEqual(before, after)
        self.assertEqual(len(self.state()['closures']), 1)
        self.assertIn('test-film', (self.base / '文生视频较长视频直出.md').read_text(encoding='utf-8'))
        self.assertIn('结案', (self.lib / 'LEARNINGS.md').read_text(encoding='utf-8'))
        self.cli('check', '--library', self.lib)

    def test_ambiguous_and_deferred_messages_do_not_close(self):
        self.init(); self.create()
        for i, text in enumerate(['这版不错', '先这样', '这个镜头可以', '开始下一个视频',
                                   '如果我说本视频制作到此结束呢', '定稿了，但暂时不要更新文档']):
            self.apply('bad-' + str(i), 'close', ok=False, user_statement=text,
                       completion_confirmed=True, final_version=None)
        self.assertEqual(self.state()['status'], 'active')
        for text in ['这个视频完成了', '本视频制作到此结束', '这版就是最终版',
                     '定稿了，不再修改', '这个作品结束了，开始下一个']:
            self.assertEqual(json.loads(self.cli('classify', '--text', text).stdout)['intent'], 'close')

    def test_reopen_preserves_acceptance_and_prompt_history(self):
        self.init(); self.create()
        self.apply('v1', 'iterate', version='V01', prompt_text='历史原文 中文')
        p = self.lib / 'cases/test-film/prompts/V01.md'
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        self.apply('close-a', 'close', user_statement='这版就是最终版', completion_confirmed=True,
                   final_version='V01')
        self.apply('reopen-a', 'reopen', user_statement='重新修改这个作品', reason='新要求')
        self.apply('v2', 'iterate', version='V02', prompt_text='修改后的完整正文')
        self.assertEqual(self.state()['status'], 'active')
        self.assertEqual(len(self.state()['closures']), 1)
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), digest)
        self.apply('overwrite', 'iterate', ok=False, version='V01', prompt_text='覆盖旧原文')
        self.cli('check', '--library', self.lib)

    def test_interruption_recovery_and_rebuilding_corrupt_index(self):
        for phase in ['prepared', 'source', 'event', 'index']:
            with self.subTest(phase=phase):
                self.lib = self.base / phase
                self.init(); self.create()
                env = dict(os.environ, DTV_TEST_INTERRUPT=phase)
                self.apply('interrupted-' + phase, 'iterate', ok=False, env=env,
                           version='V01', prompt_text='中断也不丢失的正文')
                self.cli('recover', '--library', self.lib)
                self.assertEqual(len(self.state()['iterations']), 1)
                (self.lib / 'INDEX.md').write_text('损坏', encoding='utf-8')
                self.cli('check', '--library', self.lib, ok=False)
                self.cli('rebuild', '--library', self.lib)
                self.assertIn('test-film', (self.lib / 'INDEX.md').read_text(encoding='utf-8'))
                self.cli('check', '--library', self.lib)

    def test_discovery_safe_failure_and_path_traversal(self):
        self.init()
        config = self.base / '.video-experience.json'
        config.write_text(json.dumps({'library': 'video-experience'}), encoding='utf-8')
        child = self.base / '中文 路径'; child.mkdir()
        out = json.loads(self.cli('discover', '--workspace', child).stdout)
        self.assertEqual(Path(out['library']), self.lib.resolve())
        by_index = json.loads(self.cli('discover', '--library', self.lib / 'INDEX.md').stdout)
        self.assertEqual(Path(by_index['library']), self.lib.resolve())
        old_entry = child / '原经验文档.md'; old_entry.write_text('原路径导航', encoding='utf-8')
        by_alias = json.loads(self.cli('discover', '--library', old_entry).stdout)
        self.assertEqual(Path(by_alias['library']), self.lib.resolve())
        self.apply('escape', 'create', '../outside', ok=False, metadata={'title': '错误'})
        missing = self.base / 'missing'
        self.cli('read', '--library', missing, ok=False)
        self.assertFalse(missing.exists())
        self.assertFalse((self.base / 'outside').exists())

    def test_close_rejects_nonexistent_final_version_and_quoted_or_question_intent(self):
        self.init(); self.create()
        self.apply('bad-final', 'close', ok=False, user_statement='本视频制作到此结束',
                   completion_confirmed=True, final_version='V999-absent')
        for message in ['本视频制作到此结束了吗？', '我不是说这版就是最终版。', '只是提示词定稿了，不再修改']:
            self.assertNotEqual(json.loads(self.cli('classify', '--text', message).stdout)['intent'], 'close')
        self.assertEqual(self.state()['status'], 'active')

    def test_cross_project_learning_collision_cannot_silently_replace_evidence(self):
        self.init(); self.create()
        lesson = {'id': 'DTV-L001', 'scope': 'cross_project', 'title': '原始经验',
                  'evidence': ['cases/test-film/CASE.md'], 'validation': 'recommendation'}
        self.apply('learn-1', 'review', learnings=[lesson])
        self.create('other-create', 'other-film')
        self.apply('learn-2', 'review', 'other-film', ok=False,
                   learnings=[{**lesson, 'title': '不能静默覆盖', 'evidence': ['cases/other-film/CASE.md']}])
        self.assertIn('原始经验', (self.lib / 'LEARNINGS.md').read_text(encoding='utf-8'))

    def test_case_collisions_rejected_before_journal_and_literal_prompt_links_allowed(self):
        self.init(); self.create()
        self.create('alias-attempt', 'other-film')
        self.apply('case-project', 'create', 'TEST-FILM', ok=False, metadata={'title': 'alias'})
        self.apply('p1', 'iterate', version='v1', prompt_text='输入原文 [字面链接](not-an-asset.png)')
        self.apply('p2', 'iterate', ok=False, version='V1', prompt_text='不能与小写版本碰撞')
        self.assertEqual(list((self.lib / 'transactions').glob('*.json')), [])
        self.cli('check', '--library', self.lib)

    def test_navigation_links_allow_chinese_spaces_and_parentheses(self):
        self.init()
        (self.lib / '素材 (2).png').write_bytes(b'fixture')
        self.create(sources=['../../素材 (2).png'])
        self.cli('check', '--library', self.lib)

    def test_semantic_equivalent_end_can_record_reason_without_inventing_quote(self):
        self.init(); self.create()
        self.apply('weak-override', 'close', ok=False, user_statement='这个镜头可以',
                   completion_confirmed=True, completion_basis='不能把单镜认可当整片结束')
        quote = '这条片子就收工吧，后面不再做了。'
        self.apply('semantic-end', 'close', user_statement=quote, completion_confirmed=True,
                   completion_basis='用户针对当前整部片子明确表示停止制作，不是单镜认可或暂缓', final_version=None)
        self.assertEqual(self.state()['closures'][0]['user_statement'], quote)
        self.assertEqual(self.state()['status'], 'closed')


if __name__ == '__main__':
    unittest.main(verbosity=2)
