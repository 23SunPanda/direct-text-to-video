#!/usr/bin/env python3
"""Private video experience library. Standard library only; immutable events + rebuildable Markdown."""
import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import unquote
import uuid

MARKER = '<!-- direct-text-to-video:managed-v1 -->'
VALIDATION = {'hypothesis', 'recommendation', 'observed_once', 'repeated_observation',
              'user_preference', 'verified_repeated'}


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')


def digest(value):
    return hashlib.sha256(value).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() == data:
        return
    name = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.dtv-', suffix='.tmp', delete=False) as f:
            name = f.name
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
    finally:
        if name and Path(name).exists():
            Path(name).unlink()


def identifier(value, label='ID'):
    if not isinstance(value, str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}', value):
        raise ValueError(label + ' must be a stable ASCII identifier, without paths')
    return value


def nav_spans(value):
    """Yield inline Markdown link destinations, allowing balanced filename parentheses."""
    for start in re.finditer(r'\]\(', value):
        begin = start.end(); i = begin; depth = 1; escaped = False
        while i < len(value):
            c = value[i]
            if escaped:
                escaped = False
            elif c == '\\':
                escaped = True
            elif c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    yield begin, i, value[begin:i]
                    break
            i += 1


def inside(root, relative):
    if not isinstance(relative, str) or Path(relative).is_absolute() or '\\' in relative:
        raise ValueError('Managed path must be relative with forward slashes')
    p = (root / relative).resolve()
    if not p.is_relative_to(root.resolve()) or p == root.resolve():
        raise ValueError('Path escapes library: ' + relative)
    return p


def config(root):
    p = root / 'library.json'
    if not p.is_file():
        raise ValueError('Experience library not found: ' + str(root) + '; use an existing path or explicit init')
    c = load(p)
    if c.get('schema_version') != 1:
        raise ValueError('Unsupported library schema')
    return c


def discover(workspace, explicit=None):
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if p.is_file():
            if (p.parent / 'library.json').is_file():
                p = p.parent
            else:
                candidates = [p] if p.name == '.video-experience.json' else [folder / '.video-experience.json' for folder in [p.parent, *p.parent.parents]]
                bound = next((x for x in candidates if x.is_file()), None)
                p = (bound.parent / load(bound)['library']).resolve() if bound else p.parent / 'video-experience'
        config(p)
        return p
    here = Path(workspace).resolve()
    if here.is_file():
        here = here.parent
    for folder in [here, *here.parents]:
        p = folder / '.video-experience.json'
        if p.exists():
            value = load(p).get('library')
            if not value:
                raise ValueError('Missing library in ' + str(p))
            root = (folder / value).resolve()
            config(root)
            return root
        if (folder / 'library.json').is_file():
            config(folder)
            return folder
    if os.environ.get('VIDEO_EXPERIENCE_ROOT'):
        root = Path(os.environ['VIDEO_EXPERIENCE_ROOT']).expanduser().resolve()
        config(root)
        return root
    raise ValueError('No configured experience library; supply --library or a .video-experience.json path')


def pid_alive(pid):
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x1000, False, int(pid))
        if not handle:
            return ctypes.get_last_error() == 5
        code = wintypes.DWORD()
        try:
            return not kernel.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value == 259
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(int(pid), 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


@contextmanager
def locked(root, recover=False):
    # ponytail: one writer for hundreds of projects; shard only if measured contention requires it.
    path = root / '.write-lock.json'
    if path.exists():
        owner = load(path)
        if not recover or pid_alive(owner['pid']):
            raise ValueError('Library locked; inspect owner before recover: ' + str(owner))
        path.unlink()  # Only this known, dead-owner lock; never recursive deletion.
    try:
        with path.open('x', encoding='utf-8') as f:
            json.dump({'pid': os.getpid(), 'created_at': now()}, f)
    except FileExistsError:
        raise ValueError('Another writer acquired the library lock')
    try:
        yield
    finally:
        if path.exists() and load(path).get('pid') == os.getpid():
            path.unlink()


def classify(text):
    if re.search(r'(暂时|先|这次|本次).{0,8}(不要|别|不必).{0,8}(更新|写|归档)|不要更新文档', text):
        return 'defer'
    if re.search(r'如果|假如|举例|例如|还没|尚未|未完成|不是最终|不是说|并非|不代表|不算结束|不要结案|[?？]|了吗|只是提示词|仅.{0,3}提示词', text):
        return 'not_close'
    if re.search(r'本视频制作到此结束|本视频.{0,5}结束|这个视频完成了|这版就是最终版|'
                 r'定稿了.{0,6}不再修改|这个作品结束了|视频.{0,4}制作结束|本片.{0,4}结案', text):
        return 'close'
    return 'ambiguous'


def event_files(root):
    return sorted((root / 'events').glob('*.json'))


def replay(root):
    projects, lessons, events = {}, {}, []
    for p in event_files(root):
        event = load(p)
        if event.get('request_hash') != digest(encoded(event['request'])):
            raise ValueError('Event checksum mismatch: ' + str(p))
        r = event['request']; ident = r['project_id']; d = r['data']; kind = r['kind']
        events.append(event)
        if kind == 'create':
            if ident in projects:
                raise ValueError('Duplicate project create')
            projects[ident] = {'id': ident, 'metadata': deepcopy(d['metadata']), 'status': 'active',
                               'created_at': d['metadata'].get('created_at', event['recorded_at']),
                               'iterations': [], 'reviews': [], 'closures': [], 'reopens': [],
                               'event_ids': []}
        state = projects[ident]
        state['updated_at'] = event['recorded_at']; state['event_ids'].append(r['event_id'])
        if kind == 'iterate':
            state['iterations'].append(deepcopy(d))
        elif kind == 'review':
            state['reviews'].append(deepcopy(d))
        elif kind == 'close':
            state['status'] = 'closed'
            state['closures'].append({'event_id': r['event_id'], 'closed_at': event['recorded_at'], **deepcopy(d)})
        elif kind == 'reopen':
            state['status'] = 'active'
            state['reopens'].append({'event_id': r['event_id'], 'reopened_at': event['recorded_at'], **deepcopy(d)})
        if kind != 'create' and d.get('metadata'):
            state['metadata'].update(deepcopy(d['metadata']))
        for lesson in d.get('learnings', []):
            lessons[lesson['id']] = {**deepcopy(lesson), 'source_project': ident, 'source_event': r['event_id']}
    return projects, lessons, events


def text(value):
    if value is None or value == '':
        return '未核实'
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value).replace('|', '\\|').replace('\n', ' ')


def generated(title, body):
    return (MARKER + '\n# ' + title + '\n\n' + body.rstrip() + '\n').encode('utf-8')


def render(root):
    c = config(root); projects, lessons, events = replay(root)
    output = {}; count_closed = sum(x['status'] == 'closed' for x in projects.values())
    intro = ('本页由不可变事件重建；完整提示词以各案例 prompts/ 或导入历史文件为唯一来源。\n\n'
             '[通用经验](LEARNINGS.md) · [待验证](PENDING.md) · [使用说明](README.md)\n\n'
             '检索维度：题材、风格、运镜、角色一致性、节奏、转场、音频、形态变化；使用标签或 CLI read。\n\n')
    index = intro
    pending = '用户结案与技术验证分开；项目已结束也可以保留未核实项。\n\n'
    for ident, s in sorted(projects.items()):
        m = s['metadata']; final = s['closures'][-1].get('final_version') if s['closures'] else None
        index += (f'## {ident} · {text(m.get("title"))}\n\n'
                  f'- 制作日期：{text(m.get("production_date", s["created_at"]))}；最后更新：{s["updated_at"]}\n'
                  f'- 状态：{s["status"]}；最终版本：{text(final)}；当前修订：{text(s["iterations"][-1].get("version") if s["iterations"] else m.get("current_version"))}\n'
                  f'- 题材：{text(m.get("subject"))}；风格：{text(m.get("style"))}；时长：{text(m.get("duration"))}；画幅：{text(m.get("aspect"))}\n'
                  f'- 参考类型：{text(m.get("reference_type"))}；平台：{text(m.get("platform"))}；模型：{text(m.get("model"))}\n'
                  f'- 已观察或用户认可：{text(m.get("verified_summary"))}；待验证：{text(m.get("pending"))}\n'
                  f'- 标签：{text(m.get("tags", []))}\n'
                  f'- [案例档案](cases/{ident}/CASE.md)\n\n')
        case = ('项目状态由事件重建，历史结案与后续重开均保留。完整正文只在提示词链接内，不在索引重复。\n\n'
                '[总索引](../../INDEX.md)\n\n## 当前需求与已知信息\n\n```json\n' +
                json.dumps(m, ensure_ascii=False, indent=2) + '\n```\n\n## 版本\n\n')
        for iteration in s['iterations']:
            if iteration.get('prompt_path'):
                target = Path(iteration['prompt_path']).relative_to(Path('cases') / ident).as_posix()
                case += f'- [{iteration["version"]} 完整输入]({target})；提交状态：{text(iteration.get("submission_status"))}；改动：{text(iteration.get("changes"))}；验证目标：{text(iteration.get("validation_goals"))}\n'
        for source in m.get('sources', []):
            case += f'- [历史来源]({source})\n'
        case += '\n## 复盘、结案与重开记录\n\n'
        for label, records in [('复盘', s['reviews']), ('结案', s['closures']), ('重开', s['reopens'])]:
            for record in records:
                case += f'### {label}\n\n```json\n{json.dumps(record, ensure_ascii=False, indent=2)}\n```\n\n'
        case += '## 证据解释\n\n用户验收不等于所有镜头独立验证；无最终文件不编造画面与音频观察。仅交付的提示词不等于实际提交。\n'
        output[root / 'cases' / ident / 'CASE.md'] = generated(m.get('title', ident), case)
        output[root / 'cases' / ident / 'project.json'] = encoded(s)
        unresolved = list(m.get('pending', [])) if isinstance(m.get('pending'), list) else ([m['pending']] if m.get('pending') else [])
        if s['closures']:
            unresolved += s['closures'][-1].get('unresolved', [])
            if not s['closures'][-1].get('final_video_verified'):
                unresolved.append('最终视频未独立核实，用户结案已另行记录')
        if unresolved or s['status'] != 'closed':
            pending += f'## {ident}\n\n- 项目状态：{s["status"]}\n'
            pending += ''.join('- ' + text(x) + '\n' for x in dict.fromkeys(unresolved)) + '\n'
    learning_text = f'项目数：{len(projects)}；用户结案项目数：{count_closed}；事件数：{len(events)}。结案不自动晋升为稳定规律。\n\n'
    for ident, lesson in sorted(lessons.items()):
        if lesson.get('scope') != 'cross_project':
            continue
        learning_text += f'## {ident} · {text(lesson["title"])}\n\n'
        for key, label in [('applies_to', '适用场景'), ('problem', '具体问题'), ('recommendation', '推荐做法'),
                           ('validation', '验证程度'), ('limitations', '不适用条件与限制'), ('counterexamples', '相关反例')]:
            learning_text += f'- {label}：{text(lesson.get(key))}\n'
        learning_text += f'- 来源项目：{lesson["source_project"]}；事件：{lesson["source_event"]}\n'
        learning_text += ''.join(f'- [证据]({p})\n' for p in lesson.get('evidence', [])) + '\n'
        if lesson['validation'] != 'verified_repeated':
            pending += f'- {ident}：{lesson["validation"]}；尚不能当稳定生成保证。\n'
    if not lessons:
        learning_text += '尚无跨项目结论。结案时可以明确记录“未形成新增可复用规律”，不得编造成功经验。\n'
    output[root / 'INDEX.md'] = generated('视频经验库总索引', index)
    output[root / 'LEARNINGS.md'] = generated('通用经验', learning_text)
    output[root / 'PENDING.md'] = generated('待验证与未解决问题', pending)
    entry = (root / c['entry']).resolve()
    relative = Path(os.path.relpath(root / 'INDEX.md', entry.parent)).as_posix()
    entry_body = (f'当前统一入口：[INDEX.md]({relative})。新对话先读索引与通用经验，再按项目与标签读取案例。\n\n'
                  f'[通用经验]({Path(os.path.relpath(root / "LEARNINGS.md", entry.parent)).as_posix()}) · '
                  f'[待验证]({Path(os.path.relpath(root / "PENDING.md", entry.parent)).as_posix()})\n\n'
                  f'项目数：{len(projects)}；用户已结案：{count_closed}；最后事件：{events[-1]["recorded_at"] if events else "尚无事件"}。\n\n')
    entry_body += ''.join(f'- [{s["metadata"].get("title", i)} · {i} · {s["status"]}]({Path(os.path.relpath(root / "cases" / i / "CASE.md", entry.parent)).as_posix()})\n' for i, s in sorted(projects.items()))
    if (root / 'archives/original-backup.md').exists():
        entry_body += '\n[迁移前完整原文](%s)（只读历史；不作为当前制作指令）。\n' % Path(os.path.relpath(root / 'archives/original-backup.md', entry.parent)).as_posix()
    compatibility = root / 'archives/compatibility-anchors.json'
    if compatibility.exists():
        entry_body += '\n## 历史锚点兼容导航\n\n'
        for anchor, target in load(compatibility).items():
            entry_body += f'<a id="{anchor}"></a>\n\n[历史章节：{anchor}]({Path(os.path.relpath(root / target.split("#")[0], entry.parent)).as_posix()}#{target.split("#", 1)[1]})\n\n'
    output[entry] = generated('文生视频较长视频直出', entry_body)
    return output


def rebuild(root):
    expected = render(root)
    for p, data in expected.items():
        atomic(p, data)
    return len(expected)


def interrupt(phase):
    if os.environ.get('DTV_TEST_INTERRUPT') == phase:
        os._exit(86)  # Test subprocess only: real abrupt death leaves a recoverable transaction and lock.


def finish(root, transaction, allow_interrupt=True):
    for item in transaction['files']:
        p = inside(root, item['path']); content = item['content'].encode('utf-8')
        if digest(content) != item['sha256']:
            raise ValueError('Transaction source checksum mismatch')
        if p.exists() and p.read_bytes() != content:
            raise ValueError('Refusing to overwrite immutable source ' + str(p))
        atomic(p, content)
    if allow_interrupt:
        interrupt('source')
    event = transaction['event']; path = inside(root, transaction['event_path'])
    if path.exists() and path.read_bytes() != encoded(event):
        raise ValueError('Event conflict during recovery')
    atomic(path, encoded(event))
    if allow_interrupt:
        interrupt('event')
    rebuild(root)
    if allow_interrupt:
        interrupt('index')
    inside(root, transaction['journal_path']).unlink()


def validate_request(root, request, projects, lessons):
    r = deepcopy(request)
    identifier(r['event_id'], 'event_id'); ident = identifier(r['project_id'], 'project_id')
    kind = r['kind']; d = r.setdefault('data', {}); files = []
    if kind not in {'create', 'iterate', 'review', 'close', 'reopen'}:
        raise ValueError('Unsupported event kind')
    if kind == 'create':
        if ident.casefold() in {x.casefold() for x in projects} or not d.get('metadata', {}).get('title'):
            raise ValueError('Project already exists or missing title')
    else:
        if ident not in projects:
            raise ValueError('Project identity not found; create it explicitly')
        s = projects[ident]
        if s['status'] == 'closed' and kind in {'iterate', 'close'}:
            raise ValueError('Project already closed; reuse the close event ID or explicitly reopen for revisions')
        if kind == 'reopen' and s['status'] != 'closed':
            raise ValueError('Only a closed project can be reopened')
    if kind == 'iterate':
        version = identifier(d['version'], 'version')
        if any(x['version'].casefold() == version.casefold() for x in projects[ident]['iterations']):
            raise ValueError('Version already exists; create a new version')
        content = d.pop('prompt_text', None)
        if not isinstance(content, str) or not content.strip():
            raise ValueError('A complete accessible prompt or explicitly labelled historical patch is required')
        relative = f'cases/{ident}/prompts/{version}.md'
        destination = inside(root, relative)
        if destination.exists():
            raise ValueError('Canonical prompt destination already exists; resolve before preparing a transaction')
        files.append({'path': relative, 'content': content, 'sha256': digest(content.encode('utf-8'))})
        d.update(prompt_path=relative, prompt_sha256=files[-1]['sha256'])
    if kind == 'close':
        quote = d.get('user_statement', '')
        intent = classify(quote)
        weak = re.fullmatch(r'(这版不错|先这样|这个镜头可以|开始下一个视频)[。！!，,\s]*', quote.strip())
        semantic = (intent == 'ambiguous' and quote.strip() and not weak and
                    isinstance(d.get('completion_basis'), str) and d['completion_basis'].strip())
        if d.get('completion_confirmed') is not True or not (intent == 'close' or semantic):
            raise ValueError('No unambiguous project-end signal, or user deferred document updates')
        versions = {x['version'] for x in projects[ident]['iterations']}
        versions.update(x['version'] for x in projects[ident]['metadata'].get('historical_versions', []))
        if d.get('final_version') is not None and d['final_version'] not in versions:
            raise ValueError('Final version does not belong to this project; use null if unknown')
        d.setdefault('final_video_verified', False)
        if d['final_video_verified']:
            path = Path(d.get('final_video', ''))
            actual = d.get('actual_review', {})
            if not path.is_file() or not actual.get('method') or not actual.get('observations'):
                raise ValueError('Verified final video requires an accessible file and actual review evidence')
        d.setdefault('unresolved', [])
    for lesson in d.get('learnings', []):
        identifier(lesson['id'], 'learning ID')
        prior_id = next((x for x in lessons if x.casefold() == lesson['id'].casefold()), None)
        if prior_id:
            prior = lessons[prior_id]
            if prior_id != lesson['id']:
                raise ValueError('Learning ID differs only by case')
            if prior['source_project'] != ident and (lesson.get('revises_event') != prior['source_event'] or
                    not set(prior['evidence']).issubset(set(lesson.get('evidence', [])))):
                raise ValueError('Cross-project learning ID conflict; explicitly revise the prior event and preserve its evidence')
        if lesson.get('validation') not in VALIDATION:
            raise ValueError('Learning requires an explicit evidence level')
        if not lesson.get('title') or not lesson.get('evidence'):
            raise ValueError('Learning requires title and traceable evidence')
        if lesson['validation'] == 'verified_repeated' and len(set(lesson['evidence'])) < 2:
            raise ValueError('Repeated verification requires multiple evidence sources')
    return r, files


def apply(root, request):
    config(root)
    with locked(root):
        if list((root / 'transactions').glob('*.json')):
            raise ValueError('Pending transaction; run recover first')
        projects, lessons, events = replay(root)
        request_hash = digest(encoded(request))
        for event in events:
            if event['request']['event_id'] == request.get('event_id'):
                if event['input_hash'] != request_hash:
                    raise ValueError('Event ID reused with different content')
                rebuild(root)
                return {'status': 'already_applied', 'event_id': request['event_id']}
            if event['request']['event_id'].casefold() == str(request.get('event_id', '')).casefold():
                raise ValueError('Event ID differs only by case')
        normalized, files = validate_request(root, request, projects, lessons)
        seq = len(events) + 1; eid = normalized['event_id']
        event = {'schema_version': 1, 'sequence': seq, 'recorded_at': now(), 'input_hash': request_hash,
                 'request_hash': digest(encoded(normalized)), 'request': normalized}
        transaction = {'event': event, 'files': files, 'event_path': f'events/{seq:08d}-{eid}.json',
                       'journal_path': f'transactions/{eid}.json'}
        atomic(inside(root, transaction['journal_path']), encoded(transaction))
        interrupt('prepared')
        finish(root, transaction)
        return {'status': 'applied', 'event_id': eid, 'project_id': normalized['project_id']}


def initialize(root, entry):
    root = root.resolve(); entry = entry.resolve()
    if not entry.is_relative_to(root.parent) or entry.suffix.lower() != '.md':
        raise ValueError('Entry must be a Markdown file in the library or its parent workspace')
    if (root / 'library.json').exists():
        if (root / config(root)['entry']).resolve() != entry:
            raise ValueError('Existing library is bound to another entry')
        return {'status': 'already_initialized'}
    if entry.exists() and MARKER not in entry.read_text(encoding='utf-8-sig'):
        backup = root / 'archives/original-backup.md'
        if not backup.exists() or backup.read_bytes() != entry.read_bytes():
            raise ValueError('Existing entry requires a byte-identical archives/original-backup.md before init')
    root.mkdir(parents=True, exist_ok=True)
    for name in ('events', 'transactions', 'cases', 'archives', 'templates'):
        (root / name).mkdir(exist_ok=True)
    atomic(root / 'library.json', encoded({'schema_version': 1, 'library_id': str(uuid.uuid4()),
                                          'entry': os.path.relpath(entry, root).replace('\\', '/'), 'created_at': now()}))
    atomic(root / 'README.md', ('# 私人视频经验库\n\n从 [INDEX.md](INDEX.md) 开始，按标签读取案例；'
                              '通用结论见 [LEARNINGS.md](LEARNINGS.md)，未核实项见 [PENDING.md](PENDING.md)。\n\n'
                              'events/ 是不可变记录；cases/*/prompts/ 和导入历史是完整提示词来源；'
                              'INDEX、LEARNINGS、PENDING、CASE、project.json 与旧文档入口可以由脚本重建。\n\n'
                              '明确宣布当前视频结束时，助手执行 close 事件并校验；一般赞许、准备下个视频不自动结案。'
                              '结案不证明所有技术目标已验证。新修订先 reopen，再用新版本号保存，保留旧验收。\n\n'
                              '本库属于私人数据，不随公开Skill分发。详细命令与示例见已安装Skill的 README 和 references/experience-workflow.md。\n').encode('utf-8'))
    atomic(root / 'templates/iteration.md', ('# 项目迭代记录\n\n- 项目ID、版本、基线、日期：\n'
           '- 已确认需求、取消项、角色参考职责：\n- 实际提交状态与平台模型：未知写未核实\n'
           '- 完整提示词的唯一文件：\n- 输出与观察时间点、审查方法：\n- 用户评价原话：\n'
           '- 分析或推测：\n- 修改原因、验证目标：\n- 可复用经验及证据级别：\n'
           '- 是否明确结案、最终版本、未解决事项：\n').encode('utf-8'))
    with locked(root):
        rebuild(root)
    return {'status': 'initialized', 'library': str(root)}


def check(root):
    config(root)
    if list((root / 'transactions').glob('*.json')) or (root / '.write-lock.json').exists():
        raise ValueError('Pending transaction or writer lock; inspect/recover before checking')
    errors, warnings = [], []
    expected = render(root)
    for p, content in expected.items():
        if not p.is_file() or p.read_bytes() != content:
            errors.append('Stale or missing projection: ' + str(p))
    projects, lessons, events = replay(root)
    for s in projects.values():
        for iteration in s['iterations']:
            if iteration.get('prompt_path'):
                p = inside(root, iteration['prompt_path'])
                if not p.is_file() or digest(p.read_bytes()) != iteration['prompt_sha256']:
                    errors.append('Prompt checksum mismatch: ' + str(p))
    for p in root.rglob('*.md'):
        if 'archives' in p.relative_to(root).parts:
            continue  # Raw historical backup has its original link base and is separately checksummed.
        value = p.read_text(encoding='utf-8-sig')
        if '\ufffd' in value:
            errors.append('UTF-8 replacement character: ' + str(p))
        if 'prompts' in p.relative_to(root).parts:
            continue  # Model input is literal data; its integrity is checked by the source SHA256 above.
        if len(re.findall(r'^```', value, re.M)) % 2:
            errors.append('Unbalanced fences: ' + str(p))
        # Links inside literal prompt/code blocks are input data, not navigational Markdown.
        outside_code = re.sub(r'^```[^\n]*\n.*?^```[^\n]*$', '', value, flags=re.M | re.S)
        for _, _, raw in nav_spans(outside_code):
            target = unquote(raw.strip('<>'))
            if re.match(r'^(https?|app|codex|mailto):', target):
                continue
            path, _, anchor = target.partition('#')
            dest = (p.parent / path).resolve() if path else p
            if not dest.exists():
                line = str(p.relative_to(root)) + ': missing ' + target
                (warnings if p.name == 'history.md' else errors).append(line)
            elif anchor and dest.suffix.lower() == '.md':
                content = dest.read_text(encoding='utf-8-sig')
                if not re.search(r'id=[\"\x27]' + re.escape(anchor) + r'[\"\x27]', content):
                    # Historical heading slugs vary by renderer; explicit anchors are checked strictly for managed docs.
                    if p.name != 'history.md' and MARKER in value:
                        warnings.append(str(p.relative_to(root)) + ': heading anchor requires renderer check ' + target)
    migration = root / 'archives/migration-manifest.json'
    if migration.exists():
        record = load(migration)
        original = (root / 'archives/original-backup.md').read_bytes()
        if digest(original) != record['original_sha256']:
            errors.append('Original history backup checksum mismatch')
        for item in record['files']:
            p = inside(root, item['path'])
            if not p.exists() or digest(p.read_bytes()) != item['sha256']:
                errors.append('Migrated immutable history changed: ' + item['path'])
    return {'ok': not errors, 'projects': len(projects), 'events': len(events),
            'errors': errors, 'historical_link_warnings': warnings}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['init', 'discover', 'apply', 'read', 'classify', 'rebuild', 'recover', 'check'])
    parser.add_argument('--library'); parser.add_argument('--workspace', default='.')
    parser.add_argument('--entry'); parser.add_argument('--request'); parser.add_argument('--text', default='')
    parser.add_argument('--project'); parser.add_argument('--query', default=''); parser.add_argument('--limit', type=int, default=5)
    args = parser.parse_args(argv)
    if args.command == 'classify':
        result = {'intent': classify(args.text), 'note': 'Explicit intent remains the assistant responsibility; no background listener.'}
    elif args.command == 'init':
        if not args.library:
            raise ValueError('init requires an explicit --library destination')
        root = Path(args.library).expanduser().resolve()
        result = initialize(root, Path(args.entry).expanduser() if args.entry else root / '文生视频较长视频直出.md')
    else:
        root = discover(args.workspace, args.library)
        if args.command == 'discover':
            result = {'library': str(root), 'index': str(root / 'INDEX.md')}
        elif args.command == 'apply':
            if not args.request:
                raise ValueError('apply requires --request JSON')
            result = apply(root, load(args.request))
        elif args.command == 'check':
            result = check(root)
        elif args.command in {'recover', 'rebuild'}:
            with locked(root, recover=args.command == 'recover'):
                journals = sorted((root / 'transactions').glob('*.json'))
                if journals and args.command != 'recover':
                    raise ValueError('Pending transaction; run recover')
                for journal in journals:
                    finish(root, load(journal), allow_interrupt=False)
                result = {'status': args.command, 'recovered_transactions': len(journals), 'derived_files': rebuild(root)}
        else:
            with locked(root):
                if list((root / 'transactions').glob('*.json')):
                    raise ValueError('Pending transaction; run recover before reading')
                projects, lessons, events = replay(root)
                if args.project:
                    if args.project not in projects:
                        raise ValueError('Project ID not found')
                    result = {'project': projects[args.project]}
                else:
                    words = args.query.casefold().split()
                    def score(item):
                        value = json.dumps(item, ensure_ascii=False).casefold()
                        return sum(w in value for w in words)
                    ranked = sorted(projects.values(), key=score, reverse=True)
                    chosen = [x for x in ranked if not words or score(x)][:max(1, args.limit)]
                    result = {'projects': [{'id': x['id'], 'status': x['status'], 'metadata': x['metadata']} for x in chosen],
                              'learnings': [x for x in lessons.values() if x.get('scope') == 'cross_project' and (not words or score(x))][:max(1, args.limit)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get('ok') is False else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
