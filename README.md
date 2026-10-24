# 文生视频直出导演：安装与经验闭环

本Skill面向约10—30秒、少量角色外观参考加文字的整片直出。保留参考视频分析、镜头导演、完整提示词和成片复盘；不要求分镜参考图或首尾帧，不替用户启动付费生成。

包含剧情讨论与提示词交付的阶段区分，以及交付前的内部教程对照：先认真研读适用正文和示例，草稿符合就直接交付，有实质偏差才修改，不机械重写、不附检查声明。教学入口见[教学文档与阅读顺序](references/teaching-resources.md)。

需要Python 3.10或以上；维护工具只用标准库，无需数据库、第三方服务或API Key。Codex原生工作流已在Windows测试；其他Skill平台与Flova适配尚未验证，不作兼容性承诺。

## 安装

仓库根目录就是一个完整的Skill，包含SKILL.md、references、scripts、agents与examples。Skill可以独立写提示词；希望积累经验时再连接自己的私人库。

在Codex里说：

```text
使用 $skill-installer，从 https://github.com/23SunPanda/direct-text-to-video 安装这个Skill。
```

也可以将完整文件夹放到自己的 `~/.agents/skills/direct-text-to-video`。Windows手动克隆示例：

```powershell
$skillDir = Join-Path $env:USERPROFILE '.agents\skills\direct-text-to-video'
git clone 'https://github.com/23SunPanda/direct-text-to-video.git' $skillDir
```

已安装在其他受支持目录的用户继续使用原路径即可。新对话调用 `$direct-text-to-video`；如果没有识别到，重启Codex。目录结构与本地安装说明见[Codex官方文档](https://developers.openai.com/codex/skills)。

## 新用户建立空白库

在希望保存经验的工作区运行：

```powershell
$skillDir = Join-Path $env:USERPROFILE '.agents\skills\direct-text-to-video'
python -X utf8 "$skillDir\scripts\experience.py" init --library '.\video-experience' --entry '.\文生视频较长视频直出.md'
'{"library":"video-experience"}' | Set-Content -LiteralPath '.\.video-experience.json' -Encoding utf8
python -X utf8 "$skillDir\scripts\experience.py" discover --workspace .
```

已有长文档时，init会要求先有逐字一致备份；不要将空白库覆盖旧经验。旧文档需按[经验工作流](references/experience-workflow.md)明确迁移。

## 新对话怎么用

告诉Codex：“使用direct-text-to-video，经验库在当前工作区配置中。先检索相关经验，再规划一个……的视频。”也可以直接提供经验库INDEX.md或原经验文档路径。

按你的创意先敲定故事、画幅、人物、时间和声音，再交付完整可复制提示词。你在外部平台生成后，把可访问的成片与反馈交回来。每轮保存版本、实际提交是否核实、观察和下一版目标。

明确说“本视频制作到此结束”时，助手必须实际更新案例、经验、索引和原文档导航，无需再补“更新.md”。说“先这样”或“这个镜头可以”不会自动结案。没有最终视频也能记录用户结束，但技术结果保持未核实。要求暂缓文档更新时服从本次要求。

## 可复现演示

只在空的演示目录或临时副本中运行，勿给正式私人库添加示例项目：

```powershell
python -X utf8 "$skillDir\scripts\experience.py" init --library '.\demo-library'
python -X utf8 "$skillDir\scripts\experience.py" apply --library '.\demo-library' --request "$skillDir\examples\create.json"
python -X utf8 "$skillDir\scripts\experience.py" apply --library '.\demo-library' --request "$skillDir\examples\iteration.json"
python -X utf8 "$skillDir\scripts\experience.py" read --library '.\demo-library' --query '日常 节奏'
python -X utf8 "$skillDir\scripts\experience.py" apply --library '.\demo-library' --request "$skillDir\examples\close.json"
python -X utf8 "$skillDir\scripts\experience.py" apply --library '.\demo-library' --request "$skillDir\examples\close.json"
python -X utf8 "$skillDir\scripts\experience.py" check --library '.\demo-library'
```

预期：项目sample从active变为closed；第二次close返回already_applied；V01完整正文仍只有一份；PENDING注明没有最终附件；INDEX、LEARNINGS、CASE和绑定的Markdown入口已更新。示例不需要任何私人图片或视频，不表示实际生成成功。

## 检查与恢复

```powershell
python -X utf8 "$skillDir\scripts\test_experience.py"
python -X utf8 "$skillDir\scripts\test_migration.py"
python -X utf8 "$skillDir\scripts\experience.py" recover --library '.\video-experience'
python -X utf8 "$skillDir\scripts\experience.py" rebuild --library '.\video-experience'
python -X utf8 "$skillDir\scripts\experience.py" check --library '.\video-experience'
```

测试自动创建并清理临时目录。正式库发生中断先recover，再check；索引损坏可rebuild。冲突源文件和活写锁不会被强行覆盖，错误原因直接报告。

## 私人库与公开包

公开分享仅打包此Skill目录。不要包含自己的video-experience、工作区配置、archives备份、角色图片、视频、缓存或账户信息。路径发现不依赖作者电脑目录。演示JSON仅用虚构素材与未知结果。

这套“自动归档”由当前Codex对话遵循Skill并调用本地工具完成，不是后台监听器，也不会自动获知平台实际提交、费用或生成次数。完整字段、事件协议、证据等级及故障处理见[经验工作流](references/experience-workflow.md)。

## 上传到自己的GitHub

1. 在GitHub新建名为 `direct-text-to-video` 的Public仓库；本目录已经有README和.gitignore，创建时不用另生成这两项。
2. 打开仓库的上传文件入口，将本目录内的全部文件和子文件夹上传到仓库根目录。首页应直接能看到 `SKILL.md`，而不是再套一层同名文件夹。
3. 如果发布到自己的仓库，将本README里的 `23SunPanda` 换成自己的GitHub账号，再分享仓库链接供其他人安装。

上传的是解压后的文件，GitHub不会自动把一个ZIP展开为Skill源码。ZIP可另外作为下载附件提供。

如果希望明确允许他人修改和再发布，可在仓库中添加你选择的许可证。本包没有替作者预设许可证。
