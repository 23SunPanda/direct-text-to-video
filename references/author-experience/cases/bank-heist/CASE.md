# 银行劫案／犯罪群像直出

项目状态由事件重建，历史结案与后续重开均保留。完整正文只在提示词链接内，不在索引重复。

[总索引](../../INDEX.md)

## 当前需求与已知信息

```json
{
  "aspect": "16:9",
  "current_version": "V16",
  "duration": "30秒",
  "historical_versions": [
    {
      "kind": "historical_full_or_patch",
      "source": "history.md#v01",
      "version": "V01"
    },
    {
      "kind": "historical_full_or_patch",
      "source": "history.md#v02",
      "version": "V02"
    },
    {
      "kind": "historical_full_or_patch",
      "source": "history.md#v03",
      "version": "V03"
    },
    {
      "kind": "historical_full_or_patch",
      "source": "history.md#v04",
      "version": "V04"
    },
    {
      "kind": "historical_full_or_patch",
      "source": "history.md#v05",
      "version": "V05"
    },
    {
      "kind": "historical_full_or_patch",
      "source": "history.md#v06",
      "version": "V06"
    },
    {
      "kind": "historical_full_or_patch",
      "source": "history.md#v07",
      "version": "V07"
    },
    {
      "kind": "historical_full_or_patch",
      "source": "history.md#v08",
      "version": "V08"
    },
    {
      "kind": "historical_full_or_patch",
      "source": "history.md#v09",
      "version": "V09"
    },
    {
      "kind": "historical_full_or_patch",
      "source": "history.md#v10",
      "version": "V10"
    },
    {
      "kind": "historical_full_or_patch",
      "source": "history.md#v11",
      "version": "V11"
    },
    {
      "kind": "historical_full_or_patch",
      "source": "history.md#v12",
      "version": "V12"
    },
    {
      "kind": "historical_full_or_patch",
      "source": "history.md#v13",
      "version": "V13"
    },
    {
      "kind": "historical_full_or_patch",
      "source": "history.md#v14",
      "version": "V14"
    },
    {
      "kind": "historical_full_or_patch",
      "source": "history.md#v15",
      "version": "V15"
    },
    {
      "kind": "historical_full_or_patch",
      "source": "history.md#latest-full-prompt",
      "version": "V16"
    }
  ],
  "model": "界面版本未独立核实",
  "pending": [
    "V16整理合并稿未生成验证",
    "平台审核与关键词因果未核实"
  ],
  "platform": "用户称Seedance 2.5 / Dola入口",
  "production_date": "2026-10-09—2026-10-10",
  "reference_type": "角色三视图＋文本",
  "sources": [
    "history.md"
  ],
  "style": "二维手绘日漫",
  "subject": "虚构犯罪群像片头",
  "tags": [
    "群像",
    "空间方向",
    "运镜",
    "转场",
    "节奏",
    "音频"
  ],
  "title": "银行劫案／犯罪群像直出",
  "verified_summary": "保存多轮提示词、拒绝与成片观察；未宣称最终方案验收",
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
        "节奏",
        "时间预算"
      ],
      "counterexamples": [
        "删动作后的四镜头版《关门以后》被评价太空"
      ],
      "evidence": [
        "cases/bank-heist/history.md#iteration-archive",
        "cases/after-door/history.md#after-door-experience"
      ],
      "id": "DTV-L001",
      "limitations": [
        "已有多轮失败观察；未做单变量对照，不能认定某关键词导致",
        "需要表现路线时不可一律取消行走"
      ],
      "problem": "短时段叠加位移、取物、反应会挤压动作",
      "recommendation": "省略无叙事作用的准备与搬运，保留必要接触和反应",
      "scope": "cross_project",
      "title": "按状态变化分配时长，而非只数镜头",
      "validation": "repeated_observation"
    },
    {
      "applies_to": [
        "空间方向",
        "运镜",
        "转场"
      ],
      "counterexamples": [],
      "evidence": [
        "cases/bank-heist/history.md#iteration-archive"
      ],
      "id": "DTV-L002",
      "limitations": [
        "个案方向不能升为所有视频必须向右或不后退"
      ],
      "problem": "笼统转身离开或穿过汽车产生反向撤离、同侧进出",
      "recommendation": "先建立人物、出口、左右和镜头路径，必要时给出经过物",
      "scope": "cross_project",
      "title": "用可见空间和目的地定义方向",
      "validation": "repeated_observation"
    },
    {
      "applies_to": [
        "归档",
        "证据",
        "音频"
      ],
      "counterexamples": [],
      "evidence": [
        "cases/bank-heist/history.md#iteration-archive",
        "cases/rental-op/history.md#bfop-closeout"
      ],
      "id": "DTV-L003",
      "limitations": [
        "这是一条记录方法，不是生成效果承诺"
      ],
      "problem": "收到视频或用户满意后误认所有提示词目标均达标",
      "recommendation": "逐版关联输入状态、输出、用户原话、审查方法；无提交记录标未核实",
      "scope": "cross_project",
      "title": "交付文本、实际提交、用户验收和观察分开",
      "validation": "repeated_observation"
    }
  ],
  "review_method": "导入既有历史记录，未重新播放或试听"
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
