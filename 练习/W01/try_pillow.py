#!/usr/bin/env python3
"""W1 学习过程脚本：循环版灰度化（本地练习用）。

说明：这个文件最初叫 try_pillow.py，是"读一张图看看"的探路脚本，
     后来在里面长出了 to_gray / on_white 两个函数。
     正式交付版见仓库根目录的 grayscale_cli.py（带 CLI、批量处理、错误处理）。
     本文件保留在此作为"循环版基线"，供 W2 向量化对拍参考。

用法（在仓库根目录跑）:
    cd ~/cv-kit
    python 练习/W01/try_pillow.py
"""
from PIL import Image
import os


def on_white(im):
    """把带透明通道的图贴到白底上，返回 RGB 图。"""
    alpha = im.split()[3]                                  # 取 alpha 通道
    canvas = Image.new("RGB", im.size, (255, 255, 255))     # 造白画布
    canvas.paste(im, mask=alpha)                           # 用 alpha 当遮罩合成
    return canvas


def to_gray(img):
    """输入一张图片，返回 'L' 模式的灰度图。"""
    if img.mode == "L":            # 本来就是灰度
        return img
    if img.mode == "RGBA":         # 有透明通道：先贴白底
        img = on_white(img)
    if img.mode != "RGB":          # 其它模式：统一转 RGB
        img = img.convert("RGB")

    w, h = img.size                # ↓ 下面全部回到函数体（4 空格）
    src = img.load()
    out = Image.new("L", (w, h))
    dst = out.load()

    for y in range(h):
        for x in range(w):
            r, g, b = src[x, y]
            Y = 0.299*r + 0.587*g + 0.114*b
            dst[x, y] = int(Y)
    return out


if __name__ == "__main__":
    os.makedirs("out", exist_ok=True)

    for name in ["small_640x480.jpg", "already_gray_800x600.png", "rgba_800x600.png"]:
        img = Image.open("testdata/" + name)
        gray = to_gray(img)
        out_path = "out/" + name.rsplit(".", 1)[0] + "_gray.png"
        gray.save(out_path)
        print(f"{name:26s} {img.mode:5s} → {gray.mode:2s}  {gray.size}  已存 {out_path}")