# 关门以后

项目状态由事件重建，历史结案与后续重开均保留。完整正文只在提示词链接内，不在索引重复。

[总索引](../../INDEX.md)

## 当前需求与已知信息

```json
{
  "aspect": "16:9",
  "constraints": [
    "本片无BGM、无对白、旁白、字幕，仅自然声",
    "纯白回忆，外貌代称"
  ],
  "current_version": "V04",
  "duration": "30秒",
  "historical_versions": [
    {
      "kind": "summary_only",
      "source": "source-notes.md",
      "version": "V01"
    },
    {
      "kind": "summary_only",
      "source": "source-notes.md",
      "version": "V02"
    }
  ],
  "model": null,
  "pending": [
    "当前可见变身V04未生成验证",
    "无BGM需要实际试听确认",
    "用户未宣布本片结束"
  ],
  "platform": null,
  "production_date": "2026-10-18",
  "reference_type": "当前正常版、Q版、写实男子三图；V03为两图",
  "sources": [
    "history.md",
    "source-notes.md"
  ],
  "style": "日漫二维女仆与环境＋写实男子",
  "subject": "打工人疲惫与温暖生活回忆",
  "tags": [
    "生活",
    "节奏",
    "形态变化",
    "混合画风",
    "音频",
    "表演"
  ],
  "title": "关门以后",
  "verified_summary": "两支成片元数据与抽帧已检查；横屏与男子写实外观在后片改善；未试听",
  "cost": null,
  "generation_count": null,
  "generation_notes": "未取得平台生成记录，不以提示词版本数量推断生成次数或费用"
}
```

## 版本

- [V03 完整输入](prompts/V03.md)；提交状态：unconfirmed；改动：["历史四镜头稿，用户后来反馈偏空"]；验证目标：["历史输出已抽帧，实际提交未核实"]
- [V04 完整输入](prompts/V04.md)；提交状态：unconfirmed；改动：["恢复正常版可见变Q版、吃一口与表情近景"]；验证目标：["变身落点与尺度", "节奏不赶也不空", "混合画风与无BGM"]
- [历史来源](history.md)
- [历史来源](source-notes.md)

## 复盘、结案与重开记录

### 复盘

```json
{
  "learnings": [
    {
      "applies_to": [
        "节奏",
        "表演",
        "景别"
      ],
      "counterexamples": [
        "四镜头稿虽然少动作，用户仍反馈太空"
      ],
      "evidence": [
        "cases/after-door/history.md#after-door-experience"
      ],
      "id": "DTV-L008",
      "limitations": [
        "当前恢复吃饭、近景和变身的V04尚未验证；抽帧不能替代连续节奏审查"
      ],
      "problem": "删减动作后端碗、呼吸和固定双人景别持续过久",
      "recommendation": "让停顿有目光、回应或表情信息，必要时切近景；可用冷饭与热饭重复动作对照",
      "scope": "cross_project",
      "title": "同时防止过满和过空",
      "validation": "observed_once"
    },
    {
      "applies_to": [
        "形态变化",
        "节奏",
        "空间方向"
      ],
      "counterexamples": [],
      "evidence": [
        "cases/after-door/history.md#after-door-experience"
      ],
      "id": "DTV-L009",
      "limitations": [
        "固定落点可见二维收缩方案尚无对应新成片，不宣称已解决"
      ],
      "problem": "下摇看见Q版结果不能当作看见正常版缩小",
      "recommendation": "按用户意图选择画外揭示或可见变身；后者独立留预算并保持环境尺度",
      "scope": "cross_project",
      "title": "分清变身过程与结果",
      "validation": "recommendation"
    }
  ],
  "review_method": "既有元数据与抽帧，未连续播放或试听",
  "user_evaluation": [
    "首片门段有问题且节奏快，要求横屏",
    "第二片好像又有一些太空了"
  ]
}
```

### 复盘

```json
{
  "metadata": {
    "cost": null,
    "generation_count": null,
    "generation_notes": "未取得平台生成记录，不以提示词版本数量推断生成次数或费用"
  },
  "review_method": "仅补齐档案未知字段，非新增画面审查"
}
```

## 证据解释

用户验收不等于所有镜头独立验证；无最终文件不编造画面与音频观察。仅交付的提示词不等于实际提交。
