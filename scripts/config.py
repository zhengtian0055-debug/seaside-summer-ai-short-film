# -*- coding: utf-8 -*-
"""统一读取 config.json 的路径配置。

所有脚本都通过这里拿路径，源码里不出现任何个人绝对路径。
第一次使用：把 config.example.json 复制成 config.json 再改。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # 仓库根目录
CFG_PATH = os.path.join(ROOT, "config.json")


def load():
    if not os.path.exists(CFG_PATH):
        sys.exit(
            "找不到 config.json。\n"
            "请先复制 config.example.json 为 config.json，"
            "再把 media_root / sources / music / output 改成你自己的路径。"
        )
    with open(CFG_PATH, encoding="utf-8") as f:
        cfg = json.load(f)
    for key in ("sources", "music", "output"):
        if key not in cfg:
            sys.exit("config.json 缺少字段：%s" % key)
    for name in ("S1", "S2", "S3", "S4"):
        if name not in cfg["sources"]:
            sys.exit("config.json 的 sources 缺少 %s" % name)
    return cfg


def ffmpeg_paths(cfg):
    d = cfg.get("ffmpeg_dir") or ""
    ff = os.path.join(d, "ffmpeg.exe") if d else "ffmpeg"
    fp = os.path.join(d, "ffprobe.exe") if d else "ffprobe"
    return ff, fp


def need(path, what):
    if not os.path.exists(path):
        sys.exit("找不到%s：%s" % (what, path))
    return path
