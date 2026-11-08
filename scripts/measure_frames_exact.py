# -*- coding: utf-8 -*-
"""逐分片计帧，核对成片时间轴的偏差来源。

它回答的问题是：47 个分片按帧累加应该得到多少秒，和 ffmpeg 实际
concat 出来的成片总长差在哪。

用法：
    python measure_frames_exact.py
输出：
    <work_dir>/measure.json
"""
import json
import os
import re
import subprocess
import sys

import config
import timeline


def nframes(ff, src, st, dur):
    vf = "trim=%.3f:%.3f,setpts=PTS-STARTPTS" % (st, st + dur)
    r = subprocess.run([ff, "-hide_banner", "-v", "info", "-i", src, "-vf", vf,
                        "-map", "0:v", "-an", "-f", "null", "-"],
                       capture_output=True, text=True, timeout=300)
    m = re.findall(r"frame=\s*(\d+)", r.stderr or "")
    if r.returncode != 0 or not m:
        with open("measure_err.txt", "w", encoding="utf-8") as f:
            f.write((r.stderr or "")[-4000:])
        sys.exit("计帧失败：%s in=%.3f dur=%.3f rc=%d（stderr 已存 measure_err.txt）"
                 % (os.path.basename(src), st, dur, r.returncode))
    return int(m[-1])


def main():
    cfg = config.load()
    ff, fp = config.ffmpeg_paths(cfg)
    work = cfg["work_dir"]
    os.makedirs(work, exist_ok=True)

    src = {k: config.need(v, "源视频 " + k) for k, v in cfg["sources"].items()}

    rows = []
    for i, (sname, st, dur, kind) in enumerate(timeline.PARTS):
        f = nframes(ff, src[sname], st, dur)
        rows.append({"idx": i, "src": sname, "in": st, "dur": dur,
                     "kind": kind, "frames": f, "v_seconds": round(f / timeline.FPS, 6)})

    sum_v = sum(r["v_seconds"] for r in rows)
    sum_max = sum(max(r["v_seconds"], r["dur"]) for r in rows)

    data = {
        "parts": len(rows),
        "fps": timeline.FPS,
        "total_frames": sum(r["frames"] for r in rows),
        "sum_video_seconds": round(sum_v, 6),
        "sum_max_seconds": round(sum_max, 6),
        "per_part": rows,
        "note": ("sum_video 是按整帧向下取整后的视频段总长（下界）；"
                 "sum_max 是按 max(视频段, 音频段) 占位的估算（上界）。"
                 "两者的差就是 concat 段级占位造成的累计漂移。"),
    }
    out = os.path.join(work, "measure.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    print("PARTS %d  FRAMES %d" % (data["parts"], data["total_frames"]))
    print("sum(video) = %.6fs" % sum_v)
    print("sum(max)   = %.6fs" % sum_max)
    print("diff       = %+.6fs  (%.1f 帧)"
          % (sum_max - sum_v, (sum_max - sum_v) * timeline.FPS))
    print("SAVED", out)

    # 有 ffprobe 就顺手量一下成片实际总长，和上面的推算放在一起对比
    if os.path.exists(cfg["output"]):
        r = subprocess.run([fp, "-v", "error", "-show_entries", "format=duration",
                            "-of", "default=nw=1:nk=1", cfg["output"]],
                           capture_output=True, text=True, timeout=120)
        if r.returncode == 0 and r.stdout.strip():
            print("成片实测总长 = %ss" % r.stdout.strip())


if __name__ == "__main__":
    main()
