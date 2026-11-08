# Release 附件说明

成片体积约 44 MB，不进 Git 仓库，走 GitHub Release 附件。

## 已发布的附件

- 发布页：https://github.com/zhengtian0055-debug/seaside-summer-ai-short-film/releases/tag/seaside-v2.1
- 状态：已发布（Latest，非 Pre-release），tag 指向 `main`
- 页面显示：`Assets 3`（成片 mp4 + Source code zip ×2）

| 文件 | 大小 | 说明 |
|---|---|---|
| `我在海边打暑假工的那年_精修v2.1_1080p.mp4` | 46,189,262 B（页面显示 44 MB） | 正式展示版，93.916667s，1920×1080 |

附件沿用本地交付文件名，未做改名；页面上的 `sha256` 以 `abf2863c` 开头。

## 实际使用的 Release 文案

```
标签：seaside-v2.1
标题：seaside-v2.1 精修版成片（1080p）
标注：Latest，非 Pre-release

正文：虚构说明 / 附件名与字节数 / 配乐授权待确认 / 第三方分发边界指向 LICENSE-NOTICE.md 与 docs/07 / 制作过程指向仓库首页 README。
```

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
3. 附件名与本地交付文件名一致，未带构建编号（发布后已核对）
