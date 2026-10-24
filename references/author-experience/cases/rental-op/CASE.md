# 大肥鱼出租计划 OP

项目状态由事件重建，历史结案与后续重开均保留。完整正文只在提示词链接内，不在索引重复。

[总索引](../../INDEX.md)

## 当前需求与已知信息

```json
{
  "aspect": "16:9",
  "current_version": "V08",
  "duration": "30秒",
  "historical_versions": [
    {
      "kind": "full",
      "source": "history.md#bfop-prompt-v01",
      "version": "V01"
    },
    {
      "kind": "full",
      "source": "history.md#bfop-prompt-v02",
      "version": "V02"
    },
    {
      "kind": "full",
      "source": "history.md#bfop-prompt-v03",
      "version": "V03"
    },
    {
      "kind": "full",
      "source": "history.md#bfop-prompt-v04",
      "version": "V04"
    },
    {
      "kind": "full",
      "source": "history.md#bfop-prompt-v05",
      "version": "V05"
    },
    {
      "kind": "full",
      "source": "history.md#bfop-prompt-v06",
      "version": "V06"
    },
    {
      "kind": "full",
      "source": "history.md#bfop-prompt-v07",
      "version": "V07"
    },
    {
      "kind": "full",
      "source": "history.md#bfop-prompt-v08",
      "version": "V08"
    },
    {
      "kind": "full",
      "source": "history.md#bfop-prompt-v04-appearance",
      "version": "V04-appearance"
    }
  ],
  "model": null,
  "pending": [
    "最终视频路径、实际提交与音频仍未独立核实"
  ],
  "platform": null,
  "production_date": "2026-10-10—2026-10-11",
  "reference_type": "主人、Q版、正常版三张三视图＋文本",
  "sources": [
    "history.md"
  ],
  "style": "手绘日漫＋像素关卡",
  "subject": "动画角色与图形片头",
  "tags": [
    "OP",
    "形态变化",
    "角色一致性",
    "节奏",
    "转场",
    "音频"
  ],
  "title": "大肥鱼出租计划 OP",
  "verified_summary": "用户于2026-10-11明确验收合格并宣布本轮结束；最终文件与V08逐字对应未独立核实",
  "cost": null,
  "generation_count": null,
  "generation_notes": "未取得平台生成记录，不以提示词版本数量推断生成次数或费用"
}
```

## 版本

- [历史来源](history.md)

## 复盘、结案与重开记录

### 复盘

```json
{
  "learnings": [
    {
      "applies_to": [
        "角色一致性",
        "形态变化",
        "混合画风"
      ],
      "counterexamples": [],
      "evidence": [
        "cases/rental-op/history.md#bfop-closeout",
        "cases/after-door/history.md#after-door-experience"
      ],
      "id": "DTV-L004",
      "limitations": [
        "单次外观改善不等于跨镜头稳定；写实例外不得被全局2D覆盖"
      ],
      "problem": "强化色块或简化时正常形态被Q化、头饰丢失",
      "recommendation": "按角色与形态分别约束脸、头饰、服装和比例；背景风格单独处理",
      "scope": "cross_project",
      "title": "角色身份、身体比例和画风分别锁定",
      "validation": "repeated_observation"
    },
    {
      "applies_to": [
        "迭代",
        "节奏",
        "角色一致性"
      ],
      "counterexamples": [],
      "evidence": [
        "cases/rental-op/history.md#bfop-closeout"
      ],
      "id": "DTV-L005",
      "limitations": [
        "本例收敛后用户验收；无法独立核实每项最终目标，也不是单变量实验"
      ],
      "problem": "连续叠补丁后局部改善却整体退步",
      "recommendation": "保留用户选定的较好输出与基线，围绕少数主要问题改写完整稿",
      "scope": "cross_project",
      "title": "回到较好基线定点修改",
      "validation": "recommendation"
    },
    {
      "applies_to": [
        "音频",
        "证据"
      ],
      "counterexamples": [],
      "evidence": [
        "cases/rental-op/history.md#bfop-closeout",
        "cases/after-door/history.md#after-door-experience"
      ],
      "id": "DTV-L006",
      "limitations": [
        "没有音源时不能承诺歌词逐帧同步；无BGM只是具体项目要求"
      ],
      "problem": "有AAC或写了无BGM，就误称音频要求已实现",
      "recommendation": "记录实际试听与否；歌曲统一、接触音同步和无BGM分别检查",
      "scope": "cross_project",
      "title": "音轨存在不能替代实际试听",
      "validation": "recommendation"
    }
  ],
  "review_method": "导入旧结案记录，不重新宣称试听"
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

### 结案

```json
{
  "event_id": "migration-close-rental",
  "closed_at": "2026-10-18T11:42:16+00:00",
  "accepted_at": "2026-10-11",
  "completion_confirmed": true,
  "final_version": "V08",
  "final_video_verified": false,
  "learnings": [],
  "unresolved": [
    "最终文件未随验收消息提供，实际提交对应未核实",
    "声音未可信直接试听"
  ],
  "user_evaluation": "合格",
  "user_statement": "这个视频合格，本视频制作到此结束，把这次制作视频的经验更新到.md文档里，还有各版本提示词全文以及迭代的原因"
}
```

## 证据解释

用户验收不等于所有镜头独立验证；无最终文件不编造画面与音频观察。仅交付的提示词不等于实际提交。
