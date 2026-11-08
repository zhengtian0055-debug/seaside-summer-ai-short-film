# -*- coding: utf-8 -*-
"""合成《我在海边打暑假工的那年》精修 v2.1（帧精确计时版）。

用法：
    1) 复制 config.example.json -> config.json，填好 4 段源视频、配乐、输出路径
    2) python make_subs_v21.py     # 先生成 7 个字幕层 PNG
    3) python build_refine_v21_final.py

设计要点（踩过的坑，详见 docs/04-复盘-问题与修复.md）：
- 每个分片先 trim 再 concat，且 concat 时视频段和音频段各自成对，
  否则段级占位会按 max(视频, 音频) 拉长，产生累计时间漂移。
- 片尾渐黑挂在"最后那个海面分片自己的时间线"上（fade=t=out:st=0.75:d=1.15），
  不用"总长 - 1.40s"倒推——倒推会把整个 1.95s 海面段吃掉。
"""
import json
import os
import re
import subprocess
import sys

import config
import timeline


def nframes(ff, src, st, dur):
    """测量 trim 后到底有多少帧。失败就报错退出，绝不返回估计值。"""
    vf = "trim=%.3f:%.3f,setpts=PTS-STARTPTS" % (st, st + dur)
    r = subprocess.run([ff, "-hide_banner", "-v", "info", "-i", src, "-vf", vf,
                        "-map", "0:v", "-an", "-f", "null", "-"],
                       capture_output=True, text=True, timeout=300)
    m = re.findall(r"frame=\s*(\d+)", r.stderr or "")
    if r.returncode != 0 or not m:
        raise SystemExit("计帧失败：%s in=%.3f dur=%.3f rc=%d"
                         % (os.path.basename(src), st, dur, r.returncode))
    return int(m[-1])


def main():
    cfg = config.load()
    ff, _fp = config.ffmpeg_paths(cfg)
    work = cfg["work_dir"]
    sub_dir = os.path.join(work, "sub")
    out_path = cfg["output"]
    for p in (work, sub_dir, os.path.dirname(out_path)):
        os.makedirs(p, exist_ok=True)

    src = {}
    for k, v in cfg["sources"].items():
        src[k] = config.need(v, "源视频 " + k)
    music = config.need(cfg["music"], "配乐")
    for tag, _t, _s, _y, _a in timeline.SUBTITLES:
        config.need(os.path.join(sub_dir, tag + ".png"), "字幕层 " + tag)

    src_order = ["S1", "S2", "S3", "S4"]
    idx = {k: i for i, k in enumerate(src_order)}

    parts = timeline.PARTS
    frm = [nframes(ff, src[p[0]], p[1], p[2]) for p in parts]
    pic_f = sum(frm)
    group_f, k = [], 0
    for g in timeline.GROUPS:
        group_f.append(sum(frm[k:k + len(g)]))
        k += len(g)
    print("PARTS", len(parts), "PICTURE", round(pic_f / timeline.FPS, 3))

    fc, vl, al = [], [], []
    for i, (sname, st, dur, kind) in enumerate(parts):
        chain = ["trim=%.3f:%.3f" % (st, st + dur), "setpts=PTS-STARTPTS"]
        if kind == "eye":
            chain.append(timeline.EYE)
            chain.append(timeline.GRADE["base"])
        else:
            chain.append(timeline.GRADE["base"] if kind == "sea" else timeline.GRADE[kind])
        if kind == "sea":
            chain.append("scale=1280:720:flags=lanczos,setsar=1,fade=t=out:st=0.75:d=1.15")
        else:
            chain.append("scale=1280:720:flags=lanczos,setsar=1")
        fc.append("[%d:v]%s[v%d]" % (idx[sname], ",".join(chain), i))
        fc.append("[%d:a]atrim=%.3f:%.3f,asetpts=PTS-STARTPTS,aresample=48000:async=1[a%d]"
                  % (idx[sname], st, st + dur, i))
        vl.append("[v%d]" % i)
        al.append("[a%d]" % i)

    fc.append("%sconcat=n=%d:v=1:a=1[cv][ca]"
              % ("".join(v + a for v, a in zip(vl, al)), len(parts)))
    fc.append("[cv]scale=1920:1080:flags=lanczos,unsharp=5:5:0.15:5:5:0.0,"
              "eq=contrast=1.02:saturation=1.01[g]")
    fc.append("[g]tpad=stop_duration=%.2f:stop_mode=add:color=black[gf]" % timeline.TAIL)

    starts, acc = [], 0
    for gf in group_f:
        starts.append(acc / timeline.FPS)
        acc += gf
    s1, s2, s3, s4, s5, s6 = starts

    # 字幕窗：前四条按组起点算；末尾两条用成片实测切点锚定
    # （84.792s 人物->海面，87.667s 起海面），不按帧累计推算，因为累计值会漂。
    win = [
        ("t1", s1 + 0.90, s1 + 4.80),
        ("t2", s4 + 0.40, s4 + 3.30),
        ("t3", s4 + 8.30, s4 + 12.10),
        ("t7", s5 + 0.45, s5 + 2.55),
        ("t4", 84.85, 87.45),
        ("t5", 87.45, 90.45),
    ]

    prev = "gf"
    for i, (tag, ti, to) in enumerate(win):
        fc.append("[%d:v]format=rgba,fade=in:st=%.3f:d=0.35:alpha=1,"
                  "fade=out:st=%.3f:d=0.35:alpha=1[%s]" % (5 + i, ti, to - 0.35, tag))
        fc.append("[%s][%s]overlay=0:0[ov%d]" % (prev, tag, i))
        prev = "ov%d" % i

    fc.append("[%d:v]format=rgba,fade=in:st=%.3f:d=0.55:alpha=1,"
              "fade=out:st=%.3f:d=0.45:alpha=1[ti]"
              % (11, timeline.TOTAL - 2.40, timeline.TOTAL - 0.65))
    fc.append("[%s][ti]overlay=0:0[vfinal]" % prev)

    fc.append("[ca]loudnorm=I=-16.0:TP=-1.5:LRA=11:print_format=none,apad=pad_dur=%.2f,"
              "atrim=0:%.3f,asetpts=PTS-STARTPTS[an]" % (timeline.TAIL, timeline.TOTAL))
    fc.append("[4:a]aresample=48000,atrim=0:%.3f,asetpts=PTS-STARTPTS,volume=0.22,"
              "afade=t=in:st=0:d=2.2,afade=t=out:st=%.3f:d=3.4[mus]"
              % (89.70, 86.00))
    fc.append("[an][mus]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
              "apad=pad_dur=%.2f,atrim=0:%.3f[afinal]" % (timeline.TAIL, timeline.TOTAL))

    cmd = [ff, "-y", "-v", "info", "-stats"]
    for k2 in src_order:
        cmd += ["-i", src[k2]]
    cmd += ["-i", music]
    for tag in ("t1", "t2", "t3", "t7", "t4", "t5", "t6"):
        cmd += ["-loop", "1", "-framerate", "24", "-t", "%.3f" % timeline.TOTAL,
                "-i", os.path.join(sub_dir, tag + ".png")]
    cmd += ["-filter_complex", ";".join(fc),
            "-map", "[vfinal]", "-map", "[afinal]",
            "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
            "-r", "24", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-movflags", "+faststart", "-t", "%.3f" % timeline.TOTAL, out_path]

    cut = {
        "version": "v2.1",
        "fps": timeline.FPS,
        "target_total": timeline.TOTAL,
        "tail_black": timeline.TAIL,
        "picture_total": round(pic_f / timeline.FPS, 3),
        "segments": [],
        "subtitles": [{"layer": t, "in": round(a, 3), "out": round(b, 3)} for t, a, b in win],
    }
    for name, g, st in zip(timeline.GROUPS_NAME, timeline.GROUPS, starts):
        cut["segments"].append({
            "name": name,
            "start": round(st, 3),
            "dur": round(sum(p[2] for p in g), 3),
            "parts": [{"src": p[0], "in": p[1], "dur": p[2], "grade": p[3]} for p in g],
        })
    with open(os.path.join(work, "cutlist_v21.json"), "w", encoding="utf-8") as f:
        json.dump(cut, f, ensure_ascii=False, indent=2)

    with open(os.path.join(work, "filtergraph.txt"), "w", encoding="utf-8") as f:
        f.write(";\n".join(fc))

    print("ENCODING ->", out_path)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
    with open(os.path.join(work, "ffmpeg_stderr.txt"), "w", encoding="utf-8") as f:
        f.write(r.stderr or "")
    if r.returncode != 0:
        print((r.stderr or "")[-8000:])
        sys.exit(1)
    print("OUT", out_path, os.path.getsize(out_path), "B")


if __name__ == "__main__":
    main()
