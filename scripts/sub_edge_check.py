# -*- coding: utf-8 -*-
"""字幕边界核对：把某一秒附近的帧抽出来拼成一张接触印相表。

用法：
    python sub_edge_check.py 87.35 87.45 87.50 87.55 87.60 87.65 87.67 87.70 87.75 87.80
输出：
    <work_dir>/sub_edge/<秒>_f.png 与整张对照表 sub_edge_sheet.jpg
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

import config

W, H, LBL, COLS = 640, 360, 26, 5


def main():
    cfg = config.load()
    ff, _fp = config.ffmpeg_paths(cfg)
    out_video = config.need(cfg["output"], "成片")
    dirp = os.path.join(cfg["work_dir"], "sub_edge")
    os.makedirs(dirp, exist_ok=True)
    font_p = config.need(cfg.get("font_regular"), "字体")

    ts = [float(x) for x in sys.argv[1:]] or [87.35, 87.45, 87.50, 87.55, 87.60,
                                             87.65, 87.67, 87.70, 87.75, 87.80]
    shots = []
    for t in ts:
        p = os.path.join(dirp, "%07.3f_f.png" % t)
        subprocess.run([ff, "-y", "-v", "error", "-i", out_video,
                        "-ss", "%.4f" % t, "-frames:v", "1", "-update", "1", p],
                       capture_output=True, text=True, timeout=180)
        shots.append((t, p))

    rows = (len(shots) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * (W + 6) + 6, 50 + rows * (H + LBL + 6)), (16, 16, 16))
    d = ImageDraw.Draw(sheet)
    f1 = ImageFont.truetype(font_p, 26)
    f2 = ImageFont.truetype(font_p, 20)
    d.text((8, 8), "subtitle boundary check (frames from the final encode)",
           font=f1, fill=(255, 255, 255))
    for i, (t, p) in enumerate(shots):
        r_, c_ = divmod(i, COLS)
        x, y = 6 + c_ * (W + 6), 50 + r_ * (H + LBL + 6)
        sheet.paste(Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS), (x, y))
        d.text((x + 4, y + H + 2), "%.2fs" % t, font=f2, fill=(255, 214, 90))
    out = os.path.join(dirp, "sub_edge_sheet.jpg")
    sheet.save(out, quality=92)
    print("SAVED", out, sheet.size)


if __name__ == "__main__":
    main()
