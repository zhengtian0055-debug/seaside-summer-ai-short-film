# -*- coding: utf-8 -*-
"""渲染 7 个字幕层 PNG（1920×1080 透明底）。

用法：
    python make_subs_v21.py          # 输出到 config.json 里的 work_dir/sub
"""
import os

from PIL import Image, ImageDraw, ImageFont, ImageFilter

import config
import timeline

W, H = 1920, 1080


def render(out_dir, name, text, size, y, font_path, color, align="center",
           x=110, spacing=0, sh_alpha=190, sh_blur=7, plate=False):
    f = ImageFont.truetype(font_path, size)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def draw_text(target, fill):
        bbox = target.textbbox((0, 0), text, font=f)
        tw = bbox[2] - bbox[0]
        if spacing:
            widths = [target.textlength(c, font=f) for c in text]
            tw = sum(widths) + spacing * (len(text) - 1)
        tx = (W - tw) / 2 if align == "center" else x
        if spacing:
            for ch, wch in zip(text, widths):
                target.text((tx, y), ch, font=f, fill=fill)
                tx += wch + spacing
        else:
            target.text((tx, y), text, font=f, fill=fill)

    if plate:
        bbox = ImageDraw.Draw(layer).textbbox((0, 0), text, font=f)
        ImageDraw.Draw(layer).rounded_rectangle(
            (x - 30, y - 16, x + (bbox[2] - bbox[0]) + 30, y + (bbox[3] - bbox[1]) + 18),
            radius=12, fill=(0, 0, 0, 130))

    # 先画阴影层再合成，最后必须重新 ImageDraw.Draw 才能画正字。
    # 直接用旧 draw 对象画，正字会静默丢失（字幕整层不见，但脚本仍打印成功）。
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_text(ImageDraw.Draw(sh), (0, 0, 0, sh_alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(sh_blur))
    layer = Image.alpha_composite(layer, sh)
    draw_text(ImageDraw.Draw(layer), color + (255,))

    p = os.path.join(out_dir, name + ".png")
    layer.save(p)
    print("SUB %-3s %8d B alpha_max=%d"
          % (name, os.path.getsize(p), layer.getextrema()[3][1]))


def main():
    cfg = config.load()
    out_dir = os.path.join(cfg["work_dir"], "sub")
    os.makedirs(out_dir, exist_ok=True)
    reg = cfg.get("font_regular")
    bld = cfg.get("font_bold")
    for p, what in ((reg, "常规字体"), (bld, "粗体字体")):
        config.need(p, what)

    for tag, text, size, y, align in timeline.SUBTITLES:
        font = bld if tag == "t6" else reg
        render(out_dir, tag, text, size, y, font, (255, 252, 245), align,
               x=110, spacing=8 if tag == "t6" else 0,
               plate=(tag == "t7"))
    print("DONE", out_dir)


if __name__ == "__main__":
    main()
