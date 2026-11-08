# Release 附件说明

成片体积约 44 MB，不进 Git 仓库，走 GitHub Release 附件。

## 已发布的附件（已实测）

| 下载名 | 字节数 | 说明 |
|---|---|---|
| `_.v2.1_1080p.mp4` | 46,189,262 | 正式展示版，93.916667s，1920×1080 |

直链：

```
https://github.com/zhengtian0055-debug/seaside-summer-ai-short-film/releases/download/seaside-v2.1/_.v2.1_1080p.mp4
```

HTTP HEAD 实测：`Content-Length: 46,189,262`、`Content-Type: application/octet-stream`、`Content-Disposition: attachment; filename=_.v2.1_1080p.mp4`。字节数与本地成片一致。

关于文件名：本地交付名是 `我在海边打暑假工的那年_精修v2.1_1080p.mp4`，经网页上传后 GitHub 把中文段压成了下划线，最终落盘名为 `_.v2.1_1080p.mp4`。体积与内容未受影响；只影响文件名可读性。

## Release 信息

- 页面：https://github.com/zhengtian0055-debug/seaside-summer-ai-short-film/releases/tag/seaside-v2.1
- 标签：`seaside-v2.1`（发布时新建，指向 `main`）
- 标题：`seaside-v2.1 精修版成片（1080p）`
- 标注：`Latest`，非 Pre-release
- 资产：`Assets 3`（成片 mp4 + Source code zip ×2）

## 已知不一致（待改）

- Release 正文写的是计划名 `seaside_refined_v21_1080p.mp4`，实际下载名见上表；需在网页 Edit release 里改一行。
- 正文末尾三条列表因编辑器自动续行，渲染成了子级项目符号；同样需在 Edit release 里重写。

## 不放进 Release 的文件

| 文件 | 原因 |
|---|---|
| 四段源视频 S1–S4 | 含基于作者本人形象生成的角色，不公开 |
| v1 / v2 旧版成片 | 仅用文字说明版本变化（见 `docs/03`） |
| 克隆配音版 | 音色不满意，不发布 |
| 配乐 wav 单独文件 | 版权待确认，只以成片音轨形式存在 |

## 上传前的核对

1. `ffprobe` 确认：`1920x1080`、`24` fps、`2254` 帧、约 `93.917` 秒、约 `46.2 MB`
2. 抽帧确认开头（0.5s）、结尾（93.8s）正常，无黑屏异常
3. 附件字节数与本地成片一致（发布后已核对：46,189,262）
