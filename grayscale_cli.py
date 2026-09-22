#!/usr/bin/env python3
"""批量灰度化工具（W1 交付物）。

用法：
    python grayscale_cli.py testdata          # 存到默认的 out/
    python grayscale_cli.py testdata out2     # 自己指定输出目录
    python grayscale_cli.py -h                # 看帮助

设计说明：
    · 灰度为手写公式（不调用 convert("L")），取整用 int() 截断 —— W2/W3 要拿它做性能与
      精度对标，所以这份实现就是"对照组基线"，不允许偷懒。
    · RGBA 先贴白底再算：否则透明区域会被当成黑色，整张图偏暗。
    · 一个坏文件不能中断整批：解码失败只打印警告并跳过。
"""
import argparse
import time
from pathlib import Path

from PIL import Image

# 认得的图片后缀（比较前统一转小写，所以 .JPG 也能处理）
SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp"}


def on_white(im):
    """把带透明通道的图贴到白底上，返回 RGB 图。"""
    alpha = im.split()[3]                                 # 取 alpha 通道
    canvas = Image.new("RGB", im.size, (255, 255, 255))   # 造一张纯白画布
    canvas.paste(im, mask=alpha)                          # 用 alpha 当遮罩合成
    return canvas


def to_gray(img):
    """把任意模式的图片转成 'L'（灰度）模式，返回新的 PIL 图片对象。

    分支说明：
      · L    → 本来就是单通道，直接返回（再套公式是白算，且解包会报错）
      · RGBA → 先贴白底，透明区域才不会变黑
      · 其它 → 统一 convert("RGB") 兜底（P / CMYK 等模式也能跑）
    """
    if img.mode == "L":
        return img
    if img.mode == "RGBA":
        img = on_white(img)
    if img.mode != "RGB":
        img = img.convert("RGB")

    w, h = img.size
    src = img.load()
    out = Image.new("L", (w, h))          # 空白画布，单通道
    dst = out.load()

    for y in range(h):                    # 外层：逐行
        for x in range(w):                # 内层：逐列
            r, g, b = src[x, y]           # 元组解包，正好三个数
            Y = 0.299*r + 0.587*g + 0.114*b   # 人眼亮度加权公式
            dst[x, y] = int(Y)            # 截断取整（W3 对标 OpenCV 时统一用这套）
    return out


def existing_dir(text):
    """给 argparse 用的参数检查：路径必须是一个已存在的目录。"""
    p = Path(text)
    if not p.is_dir():
        raise argparse.ArgumentTypeError(f"不是已存在的目录：{text}")
    return p


def main():
    parser = argparse.ArgumentParser(
        description="批量灰度化：读图片 → 手写公式转灰度 → 存成 PNG")
    parser.add_argument("indir", type=existing_dir, help="输入目录（放图片的地方）")
    parser.add_argument("outdir", nargs="?", default="out",
                        help="输出目录（默认 out，不存在会自动创建）")
    args = parser.parse_args()

    indir = args.indir
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # 安全护栏：输入和输出是同一个目录会互相覆盖 / 无限套娃
    if indir.resolve() == outdir.resolve():
        parser.error("输出目录不能和输入目录相同（会覆盖原图、还会把生成结果再处理一遍）")

    print(f"处理目录: {indir}  →  输出到: {outdir}")

    t0 = time.perf_counter()
    ok = 0
    skipped = 0

    for p in sorted(indir.iterdir()):          # 排序：保证每次跑的顺序一致
        if not p.is_file():                    # 子目录不处理
            continue
        if p.suffix.lower() not in SUFFIXES:   # 后缀不认（如 notes.txt）
            print(f"  ⏭  {p.name:26s} 后缀不符，跳过")
            skipped += 1
            continue

        try:                                   # ← 保险丝：从这里开始出错都不会崩
            img = Image.open(p)                # 注意：open 只读文件头，不读像素
            gray = to_gray(img)                # ← 坏图在这一步（取像素）才会炸
            out_path = outdir / (p.stem + "_gray.png")
            gray.save(out_path)
            print(f"  ✅ {p.name:26s} {img.mode:5s} → L  {gray.size}")
            ok += 1
        except Exception as e:                 # ← 接住异常：打印、继续下一个文件
            print(f"  ❌ {p.name:26s} 解码失败: {type(e).__name__}")
            skipped += 1

    elapsed = time.perf_counter() - t0
    print(f"\n完成：成功 {ok} 张 / 跳过 {skipped} 个 / 用时 {elapsed:.2f} 秒")


if __name__ == "__main__":
    main()