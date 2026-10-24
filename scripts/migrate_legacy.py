#!/usr/bin/env python3
"""Explicit, planned, byte-backed-up migration. Never infer a project close from a new task."""
from collections import Counter
import argparse
import json
import os
from pathlib import Path
import re
import sys

import experience as db


def code_blocks(value):
    return re.findall(r'^```[^\n]*\n.*?^```[^\n]*$', value, re.M | re.S)


def rebase(value, original, destination, owners, source_map, root):
    def rewrite(part):
        for a, b, raw in reversed(list(db.nav_spans(part))):
            href = raw.strip('<>')
            if re.match(r'^(https?|app|codex|mailto):', href):
                continue
            path, sep, anchor = href.partition('#')
            if not path and anchor in owners:
                target = root / owners[anchor]
            elif path:
                source = (original.parent / path).resolve()
                target = source_map.get(str(source), source)
                if source == original.resolve() and anchor in owners:
                    target = root / owners[anchor]
            else:
                target = destination
            try:
                new = Path(os.path.relpath(target, destination.parent)).as_posix()
            except ValueError:
                new = target.as_posix()  # Private C:/ assets remain absolute when the library is on D:/.
            if target == destination and not path:
                new = ''
            new += sep + anchor
            part = part[:a] + new + part[b:]
        return part
    pieces = re.split(r'(^```[^\n]*\n.*?^```[^\n]*$)', value, flags=re.M | re.S)
    result = ''.join(piece if i % 2 else rewrite(piece) for i, piece in enumerate(pieces))
    if code_blocks(result) != code_blocks(value):
        raise ValueError('Migration changed literal fenced history')
    return result


def prepare(legacy, root, plan):
    backup = root / 'archives/original-backup.md'
    raw = backup.read_bytes() if backup.exists() else legacy.read_bytes()
    if db.MARKER.encode() in raw[:200]:
        raise ValueError('Raw original backup required; refusing to migrate a generated navigation file')
    value = raw.decode('utf-8-sig'); lines = value.splitlines(keepends=True)
    segments = sorted(plan['segments'], key=lambda x: x['start'])
    cursor = 1; grouped = {}; owners = {}; ranges = []
    for segment in segments:
        first, last, relative = segment['start'], segment['end'], segment['target']
        db.inside(root, relative)
        if first != cursor or last < first or last > len(lines):
            raise ValueError('Segments must cover every original line exactly once, without gaps or overlap')
        chunk = ''.join(lines[first - 1:last]); cursor = last + 1
        grouped.setdefault(relative, []).append(chunk)
        ranges.append({**segment, 'source_sha256': db.digest(chunk.encode('utf-8'))})
        for anchor in re.findall(r'<a\s+id=[\"\x27]([^\"\x27]+)', chunk):
            if anchor in owners and owners[anchor] != relative:
                raise ValueError('Ambiguous original anchor: ' + anchor)
            owners[anchor] = relative
    if cursor != len(lines) + 1:
        raise ValueError('Original history has uncovered lines')
    source_map = {str(legacy.resolve()): root / 'INDEX.md'}
    inputs = []
    for n, item in enumerate(plan.get('imports', []) + plan.get('prompt_imports', [])):
        original = Path(item['source']).resolve()
        cache = root / f'archives/migration-inputs/{n:03d}{original.suffix}'
        data = cache.read_bytes() if cache.exists() else original.read_bytes()
        target = item.get('target') or f'cases/{item["project_id"]}/prompts/{item["version"]}.md'
        source_map[str(original)] = db.inside(root, target)
        inputs.append((item, original, cache, data))
    for item in plan.get('redirects', []):
        source_map[str(Path(item['source']).resolve())] = db.inside(root, item['target'])
    contents = {}
    for relative, chunks in grouped.items():
        target = db.inside(root, relative)
        body = rebase('\n\n'.join(chunks), legacy, target, owners, source_map, root)
        contents[relative] = ('> 只读历史导入；当前需求与状态以本案例 CASE.md 或总索引为准。原始逐字备份在 archives/original-backup.md。\n\n' + body).encode('utf-8')
    for item, original, cache, data in inputs:
        if item in plan.get('imports', []):
            target = db.inside(root, item['target'])
            if item.get('kind', 'markdown') == 'markdown':
                contents[item['target']] = rebase(data.decode('utf-8-sig'), original, target, owners, source_map, root).encode('utf-8')
            else:
                contents[item['target']] = data
    return raw, lines, ranges, owners, contents, inputs


def migrate(legacy, root, plan, dry_run=False, revise_plan=False):
    raw, lines, ranges, owners, contents, inputs = prepare(legacy, root, plan)
    plan_hash = db.digest(db.encoded(plan))
    old_manifest = root / 'archives/migration-manifest.json'
    previous = db.load(old_manifest) if old_manifest.exists() else None
    changing_plan = previous and previous['plan_sha256'] != plan_hash
    if changing_plan and not revise_plan:
        raise ValueError('Migration plan changed; use explicit --revise-plan to preserve and supersede the prior migration')
    if dry_run:
        return {'dry_run': True, 'original_bytes': len(raw), 'coverage_lines': len(lines),
                'partition_count': len(ranges), 'history_files': list(contents), 'projects': [x['id'] for x in plan['projects']]}
    previous_files = {x['path']: x for x in previous['files']} if previous else {}
    if changing_plan:
        snapshot = root / 'archives/migration-revisions' / previous['plan_sha256'][:16]
        for relative, item in previous_files.items():
            source = db.inside(root, relative)
            expected_new = contents.get(relative)
            if db.digest(source.read_bytes()) != item['sha256'] and source.read_bytes() != expected_new:
                raise ValueError('Cannot revise user-modified history: ' + relative)
            target = snapshot / relative
            if not target.exists():
                db.atomic(target, source.read_bytes())
        db.atomic(snapshot / 'migration-manifest.json', old_manifest.read_bytes())
        db.atomic(snapshot / 'migration-plan.json', (root / 'archives/migration-plan.json').read_bytes())
    root.mkdir(parents=True, exist_ok=True)
    backup = root / 'archives/original-backup.md'
    if backup.exists() and backup.read_bytes() != raw:
        raise ValueError('Original backup conflict')
    db.atomic(backup, raw)
    for item, original, cache, data in inputs:
        if cache.exists() and cache.read_bytes() != data:
            raise ValueError('Original input cache conflict')
        db.atomic(cache, data)
    for relative, content in contents.items():
        target = db.inside(root, relative)
        if target.exists() and target.read_bytes() != content and not (changing_plan and relative in previous_files):
            raise ValueError('Existing immutable migration file differs: ' + relative)
        db.atomic(target, content)
    db.atomic(root / 'archives/compatibility-anchors.json', db.encoded({a: f'{p}#{a}' for a, p in owners.items()}))
    db.atomic(root / 'archives/migration-plan.json', db.encoded(plan))
    db.initialize(root, legacy)
    if list((root / 'transactions').glob('*.json')) or (root / '.write-lock.json').exists():
        with db.locked(root, recover=True):
            for journal in sorted((root / 'transactions').glob('*.json')):
                db.finish(root, db.load(journal), allow_interrupt=False)
    for project in plan['projects']:
        ident = db.identifier(project['id'])
        db.apply(root, {'event_id': 'migration-create-' + ident, 'project_id': ident,
                        'kind': 'create', 'data': {'metadata': project['metadata']}})
        for item, original, cache, data in inputs:
            if item not in plan.get('prompt_imports', []) or item['project_id'] != ident:
                continue
            body = data.decode('utf-8-sig')
            if item.get('fenced_text'):
                match = re.search(r'^```text\r?\n(.*?)\r?\n```', body, re.M | re.S)
                if not match:
                    raise ValueError('Full prompt text block not found: ' + str(original))
                body = match.group(1)
            db.apply(root, {'event_id': item['event_id'], 'project_id': ident, 'kind': 'iterate',
                            'data': {'version': item['version'], 'prompt_text': body,
                                     'submission_status': 'unconfirmed', 'changes': item.get('changes', []),
                                     'validation_goals': item.get('validation_goals', [])}})
        for event in project.get('events', []):
            db.apply(root, {**event, 'project_id': ident})
    files = [{'path': p, 'sha256': db.digest(c), 'bytes': len(c)} for p, c in sorted(contents.items())]
    for p in (root / 'cases').glob('*/prompts/*.md'):
        files.append({'path': p.relative_to(root).as_posix(), 'sha256': db.digest(p.read_bytes()), 'bytes': p.stat().st_size})
    manifest = {'schema_version': 1, 'original_sha256': db.digest(raw), 'original_bytes': len(raw),
                'coverage_lines': len(lines), 'segments': ranges, 'plan_sha256': plan_hash, 'files': files,
                'literal_blocks_in_original': len(code_blocks(raw.decode('utf-8-sig'))),
                'history_fenced_blocks_preserved': True, 'explicit_anchors_forwarded': len(owners)}
    db.atomic(old_manifest, db.encoded(manifest))
    with db.locked(root):
        db.rebuild(root)
    for item in plan.get('redirects', []):
        source = Path(item['source']).resolve()
        target = db.inside(root, item['target'])
        if not source.is_relative_to(legacy.parent.resolve()) or source == legacy.resolve():
            raise ValueError('Redirect outside the explicitly migrated workspace')
        relative = Path(os.path.relpath(target, source.parent)).as_posix()
        db.atomic(source, db.generated('档案已迁移', f'完整内容的唯一维护位置：[打开档案]({relative})。\n\n旧原文已完整备份到经验库 archives；此文件只作原路径导航，不继续保存另一份完整提示词。'))
    result = db.check(root)
    return {**result, 'migration': manifest}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--legacy', required=True); parser.add_argument('--library', required=True)
    parser.add_argument('--plan', required=True); parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--revise-plan', action='store_true', help='Archive and supersede a prior partition plan; never overwrite user-modified history')
    args = parser.parse_args()
    result = migrate(Path(args.legacy).resolve(), Path(args.library).resolve(), db.load(args.plan), args.dry_run, args.revise_plan)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get('ok') is False else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
