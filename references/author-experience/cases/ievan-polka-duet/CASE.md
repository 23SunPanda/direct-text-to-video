# 甩葱歌·Q版双人舞

项目状态由事件重建，历史结案与后续重开均保留。完整正文只在提示词链接内，不在索引重复。

[总索引](../../INDEX.md)

## 当前需求与已知信息

```json
{
  "aspect": "496×864竖屏；方案为9:16，实际比例约0.5741",
  "assistant_assumptions": [
    "会话一段按编排一段理解",
    "人物用参考图1角色A与参考图2角色B映射，尚未指定具体身份",
    "公园石板地为导演提案",
    "约13秒与最后半秒收势为导演提案"
  ],
  "audio_reference": "本地工作区/甩葱歌_双人舞_20261019/音乐参考_01分35秒至01分47秒500.mp3",
  "cost": null,
  "duration": "实际成片10.08秒（视频轨10.041667秒）；方案目标约13秒",
  "generation_count": null,
  "model": "Seedance；用户拼写seedanca，具体版本未核实",
  "pending": [
    "实际提交是否逐字采用V01未核实",
    "具体Seedance模型版本、入口和时长设置未知，不能把10秒结果归因于模型自行压缩",
    "用户实际上传的角色图原文件及右侧角色身份未确认",
    "原录音保留与精确节拍同步未实际试听；波形比对未确认同一录音原样保留",
    "单次首轮验收不能视为跨项目稳定复现"
  ],
  "platform": "用户称Seedance模型入口，当前未确认是否沿用豆包入口",
  "production_date": "2026-10-19",
  "reference_type": "两位Q版角色＋12.5秒音乐参考；实际角色图原文件未提供。成片左蓝发女仆鲸尾，右白发角饰浅色服装",
  "source_video": "本地附件/Downloads/19774926_da3-1-16.mp4",
  "style": "两个二维Q版角色＋实拍摄影质感背景；用户确认",
  "subject": "用户指定现场录音配原创Q版双人舞，十几秒",
  "tags": [
    "双人舞",
    "Q版",
    "音乐",
    "节拍",
    "混合画风",
    "角色一致性"
  ],
  "title": "甩葱歌·Q版双人舞",
  "user_statements": [
    "参考《甩葱歌》的芬兰民歌原曲，挑一段最有活力的片段，会话一段与之相配的双人舞蹈，十几秒就行",
    "两个Q版角色，竖屏，还是seedanca模型，是搭配实拍背景",
    "另一个版本，我提供链接",
    "可以上传音频"
  ],
  "audio": "AAC立体声32000Hz",
  "fps": 24,
  "height": 864,
  "width": 496,
  "acceptance_status": "用户首轮整体验收合格",
  "accepted_video_path": "本地附件/Downloads/wf12026101915260050558451330306.mp4",
  "generation_rounds_user_reported": 1,
  "source_metadata": {
    "audio": "AAC",
    "duration": 157.198435,
    "fps": 15,
    "height": 240,
    "width": 320
  },
  "verified_summary": "用户称一轮效果合格；抽帧可见双人固定左右全身构图、并步、互看笑容、侧踢与末段共同小跳，Q版人物与摄影质感公园共存；音频未实际试听"
}
```

## 版本

- [V01 完整输入](prompts/V01.md)；提交状态：拟提交，角色参考图待指定；未生成；改动：["从用户视频裁取95—107.5秒原速音乐候选", "约13秒，三个约八拍动作组＋半秒收势", "两个Q版角色与实拍公园背景分别限定画风", "使用图1角色A、图2角色B，未擅自指定已有角色"]；验证目标：["选段是否符合用户的最有活力偏好", "原录音旋律与人声是否保留", "动作踏点能否跟随实际音乐", "两个角色身份、左右位置与肢体连续", "双脚落地与实拍背景合成自然"]

## 复盘、结案与重开记录

### 复盘

```json
{
  "analysis": [
    "选取95—107.5秒作为拟声段候选，按约三个八拍设计舞步；选段与卡点仍须听辨和成片验证"
  ],
  "learnings": [],
  "metadata": {
    "audio": "AAC",
    "duration": 157.198435,
    "fps": 15,
    "height": 240,
    "width": 320
  },
  "observations": [
    "画面为四人舞台演唱；不据此确认首次录音或录制年份",
    "约54—106秒的画面字幕标注无意义，并显示拟声音节",
    "55—100秒范围节拍估计约115.65BPM，仅算法估计，未确定小节起拍",
    "对比50—107.5秒附近的12秒窗口，95秒附近起音变化与RMS较高；音量与起音指标不能单独证明主观活力最高"
  ],
  "review_method": {
    "audio_listened": false,
    "audio_signal_analysis": "STFT正向对数谱变化、起音周期自相关、RMS",
    "continuous_playback": false,
    "sparse_frames": true,
    "subtitles_visual": true
  },
  "review_target": "用户提供的音乐参考视频，不是本项目已生成成片",
  "selected_audio": {
    "channels": 2,
    "duration": 12.5,
    "output": "本地工作区/甩葱歌_双人舞_20261019/音乐参考_01分35秒至01分47秒500.mp3",
    "sample_rate": 44100,
    "source_end": 107.5,
    "source_start": 95,
    "time_stretch": false
  },
  "source_path": "本地附件/Downloads/19774926_da3-1-16.mp4",
  "suggestions": [
    "上传裁好的音频作为音乐参考",
    "固定正面全身双人镜头，保持左右站位",
    "用并步、脚跟点地与小跳构成三个动作组"
  ],
  "unresolved": [
    "实际试听未进行",
    "角色参考未指定",
    "无法保证仅参考音频就会原样保留原录音或精确卡点"
  ]
}
```

### 复盘

```json
{
  "acceptance": {
    "generation_count": null,
    "generation_rounds_user_reported": 1,
    "note": "首轮不等同于已核实只生成一条；经验总结获明确授权，未将普通整体验收自动升级为项目关闭",
    "project_end_explicit": false,
    "result": "用户认可",
    "scope": "整支双人舞的本轮效果"
  },
  "actual_submission_confirmed": false,
  "analysis": [
    "首轮成功同时包含音源参考、动作分组、固定构图和混合画风等多个因素，没有对照实验，不能确认哪个单独因素导致成功",
    "时长实测10.08秒与13秒计划不同，实际输入和界面时长未核实；保留差异，不推断模型内部原因",
    "音频参考不等同于最终录音逐样本保留；未试听，不将有音轨或用户整体验收升级为精确卡点证明"
  ],
  "candidate_prompt_version": "V01",
  "failures": [],
  "followup_user_statement": "这是原片",
  "learnings": [
    {
      "applies_to": [
        "十几秒短舞",
        "双人舞",
        "Q版角色",
        "节奏"
      ],
      "counterexamples": [],
      "evidence": [
        "cases/ievan-polka-duet/CASE.md",
        "本地工作区/甩葱歌_双人舞_20261019/成片复盘_01/overview.jpg",
        "本地工作区/甩葱歌_双人舞_20261019/成片复盘_01/ending_detail.jpg"
      ],
      "id": "DTV-DANCE-001",
      "limitations": [
        "用户报告首轮整体合格，只有本例一次成片；不等于重复稳定成功",
        "抽帧可见并步、互看笑容、侧踢与末段小跳，但没有逐拍确认每个脚跟点地和手臂绕圈",
        "实际成片10.08秒；方案约13秒和三个约八拍，不可声称严格按三个八拍执行",
        "实际提交是否逐字使用V01未核实，不能把成功归因于单个提示词"
      ],
      "problem": "短舞需要在有限时间内形成变化，也要让观众读清每组动作",
      "recommendation": "可先采用并步—脚跟点地或摆臂—侧踢与小跳收势的少量动作组，再按具体音乐调整；用互看或镜像动作增加双人关系",
      "scope": "cross_project",
      "title": "短双人舞可先用三个可读动作组组织",
      "validation": "observed_once"
    },
    {
      "applies_to": [
        "双人舞",
        "构图",
        "角色一致性",
        "连续性"
      ],
      "counterexamples": [],
      "evidence": [
        "cases/ievan-polka-duet/CASE.md",
        "本地工作区/甩葱歌_双人舞_20261019/成片复盘_01/overview.jpg",
        "本地工作区/甩葱歌_双人舞_20261019/成片复盘_01/ending_detail.jpg"
      ],
      "id": "DTV-DANCE-002",
      "limitations": [
        "本例抽帧中两人全身可见且左右位置保持；尚未逐帧审查全片所有肢体",
        "没有与移动镜头或换位舞蹈作对照，不能证明固定镜头必然提高成功率",
        "本例不构成所有舞蹈都必须固定机位或禁止换位的规则"
      ],
      "problem": "双人舞需要同时看清两人的脚步、手势与相对位置",
      "recommendation": "可先用固定正面全身镜头、明确左A右B与挥臂空间；通过舞步和表情产生变化，收势时让两人的落地可见",
      "scope": "cross_project",
      "title": "双人短舞可用固定正面全身构图保持动作可读",
      "validation": "observed_once"
    },
    {
      "applies_to": [
        "混合画风",
        "Q版",
        "实拍背景"
      ],
      "counterexamples": [],
      "evidence": [
        "cases/ievan-polka-duet/CASE.md",
        "本地工作区/甩葱歌_双人舞_20261019/成片复盘_01/overview.jpg",
        "本地工作区/甩葱歌_双人舞_20261019/成片复盘_01/ending_detail.jpg"
      ],
      "id": "DTV-DANCE-003",
      "limitations": [
        "只核实成片中Q版角色与摄影质感公园共存，不认定所有细节严格符合二维赛璐璐风格",
        "未取得用户实际上传的两张角色原图，不能独立验收与身份图逐项一致",
        "尚未实际试听原录音是否保留、节奏是否精准同步"
      ],
      "problem": "需要分别维持Q版人物特征与摄影质感场景",
      "recommendation": "保留本例对人物、实拍场景和落地阴影分别描述的完整稿，后续相似项目可参考，不将本例扩展为所有角色都适用的结论",
      "scope": "case_only",
      "title": "Q版双人和实拍公园背景搭配获本轮认可",
      "validation": "observed_once"
    }
  ],
  "metadata": {
    "acceptance_status": "用户首轮整体验收合格",
    "accepted_video_path": "本地附件/Downloads/wf12026101915260050558451330306.mp4",
    "aspect": "496×864竖屏；方案为9:16，实际比例约0.5741",
    "audio": "AAC立体声32000Hz",
    "duration": "实际成片10.08秒（视频轨10.041667秒）；方案目标约13秒",
    "fps": 24,
    "generation_count": null,
    "generation_rounds_user_reported": 1,
    "height": 864,
    "pending": [
      "实际提交是否逐字采用V01未核实",
      "具体Seedance模型版本、入口和时长设置未知，不能把10秒结果归因于模型自行压缩",
      "用户实际上传的角色图原文件及右侧角色身份未确认",
      "原录音保留与精确节拍同步未实际试听；波形比对未确认同一录音原样保留",
      "单次首轮验收不能视为跨项目稳定复现"
    ],
    "reference_type": "两位Q版角色＋12.5秒音乐参考；实际角色图原文件未提供。成片左蓝发女仆鲸尾，右白发角饰浅色服装",
    "source_metadata": {
      "audio": "AAC",
      "duration": 157.198435,
      "fps": 15,
      "height": 240,
      "width": 320
    },
    "source_video": "本地附件/Downloads/19774926_da3-1-16.mp4",
    "verified_summary": "用户称一轮效果合格；抽帧可见双人固定左右全身构图、并步、互看笑容、侧踢与末段共同小跳，Q版人物与摄影质感公园共存；音频未实际试听",
    "width": 496
  },
  "observations": [
    {
      "observation": "左侧蓝发女仆鲸尾角色、右侧白发角饰浅色服装角色持续保持左右站位；公园地面、树木、景深与自然光呈摄影质感",
      "time": "全片抽样"
    },
    {
      "observation": "两人均有左右踏步、单腿支撑和摆臂姿态变化",
      "time": "前段约0—3秒"
    },
    {
      "observation": "两人互相朝向、胸前手臂动作和共同笑容可见",
      "time": "中段约3.5—5秒"
    },
    {
      "observation": "两人各向外侧低位抬腿，构成镜像呼应",
      "time": "约7秒"
    },
    {
      "observation": "双人逐渐起跳，9.125秒两人脚底与地面间均可见空隙",
      "time": "8.875—9.125秒"
    },
    {
      "observation": "两人回到落地站姿并收势",
      "time": "9.250—9.500秒"
    }
  ],
  "output_path": "本地附件/Downloads/wf12026101915260050558451330306.mp4",
  "review_method": {
    "audio_listened": false,
    "audio_signal_comparison": "与原音源94—109秒窗口作归一化波形相关，仅作辅助，未确认一致，不作为听辨结论",
    "continuous_playback": false,
    "dense_frames": "8.500—9.500秒每3帧取样；帧号204—228，24fps，对应真实时间",
    "metadata": true,
    "sparse_frames": "2fps抽样，时间标签为抽样序列近似时间"
  },
  "successes": [
    "用户首轮整体认可",
    "三段动作结构在抽样中可辨识",
    "两人站位和全身动作清楚",
    "摄影质感公园与Q版人物共存",
    "末段同步小跳与落地可辨识"
  ],
  "unresolved": [
    "逐字实际提交稿未核实",
    "音乐保留与逐拍同步未试听",
    "首轮总生成条数和成本未知"
  ],
  "user_evaluation": "用户报告本轮整体效果合格，要求总结经验；首轮验收通过",
  "user_statement": "一轮效果合格，总结经验"
}
```

## 证据解释

用户验收不等于所有镜头独立验证；无最终文件不编造画面与音频观察。仅交付的提示词不等于实际提交。
