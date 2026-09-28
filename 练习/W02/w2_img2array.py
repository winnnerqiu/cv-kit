#!/usr/bin/env python3
"""W2 任务 2：图片 <-> NumPy 数组 —— 亲眼看那个"高宽反转"的坑。

用法:
    cd ~/cv-kit
    python 练习/W02/w2_img2array.py
"""
import numpy as np
from PIL import Image

print("=" * 64)
print("① 图片在内存里到底是什么 —— 用肉眼可见的小数组看")
print("=" * 64)

# 造一张只有 2 行 3 列的"迷你灰度图"（4 个像素，肉眼可数）
mini = np.array([
    [  0, 128, 255],
    [ 64, 200,  30],
], dtype=np.uint8)
print(f"  迷你灰度图（2 行 3 列）：\n{mini}")
print(f"  shape = {mini.shape}   dtype = {mini.dtype}")
print()
print("  每个数字就是一个像素的亮度：0=纯黑, 255=纯白, 中间值=灰")
print("  ★ 图片 = 一个数字表格。这就是全部真相。")

# 存成图片，用眼睛验证
Image.fromarray(mini).save("/tmp/mini.png")
print("  已存成 /tmp/mini.png —— 你能在 VS Code 里打开看一眼（3 个像素宽，很小）")
print()

print("=" * 64)
print("② PIL 和 NumPy 读到的像素，是同一份数据吗")
print("=" * 64)

img = Image.open("testdata/small_640x480.jpg")
arr = np.array(img)

print(f"  PIL  的 img.size   = {img.size}")
print(f"  NumPy 的 arr.shape = {arr.shape}")
print()
print("  ★ 陷阱警报：")
print(f"      img.size[0]      = {img.size[0]}          ← 宽")
print(f"      arr.shape[0]     = {arr.shape[0]}          ← 高  ！顺序反了")
print(f"      arr.shape[1]     = {arr.shape[1]}")
print(f"      arr.shape[2]     = {arr.shape[2]}            ← 通道数（RGB 是 3）")
print()
print("  → 记住：图像数组 = (高, 宽, 通道)，取元素写 arr[行, 列, 通道]")
print()

print("=" * 64)
print("③ 同一个像素，两种读法对不对得上")
print("=" * 64)

px = img.load()                    # PIL 的读法
y, x = 240, 320                    # 注意：numpy 是 (行, 列)
print(f"  取坐标 (行={y}, 列={x}) 的像素：")
print(f"    PIL   px[{x}, {y}]      = {px[x, y]}        （PIL 是 x, y）")
print(f"    NumPy arr[{y}, {x}]     = {arr[y, x]}        （NumPy 是 y, x）")
print(f"    两个相等吗？             = {np.array_equal(np.array(px[x, y]), arr[y, x])}")
print("  ★ 同一个数据，两种索引顺序。搞混了不会报错，但会读到别的像素。")
print()

print("=" * 64)
print("④ 通道是可以单独拆出来的")
print("=" * 64)

r = arr[:, :, 0]
g = arr[:, :, 1]
b = arr[:, :, 2]
print(f"  红色通道 r = arr[:, :, 0]   shape = {r.shape}   ← 二维了（没有第三维）")
print(f"  绿色通道 g = arr[:, :, 1]   shape = {g.shape}")
print(f"  蓝色通道 b = arr[:, :, 2]   shape = {b.shape}")
print()
print(f"  三个通道的值（中心点）：R={r[240,320]}, G={g[240,320]}, B={b[240,320]}")
import os
os.makedirs("out", exist_ok=True)
Image.fromarray(r).save("out/channel_R.png")
Image.fromarray(g).save("out/channel_G.png")
Image.fromarray(b).save("out/channel_B.png")
print("  已存 out/channel_R/G/B.png —— 打开看看，是同一张图的三种分色")
print()

print("=" * 64)
print("⑤ 切片：一次改一整块区域（没有循环！）")
print("=" * 64)

flipped = arr[::-1, :, :]              # 行方向倒序 = 上下翻转
Image.fromarray(flipped).save("out/flipped.png")
print("  已存 out/flipped.png   ← 这张图是上下翻转的（arr[::-1, :, :] 一行搞定）")
print("  ★ 提示：切片是'视图'，改它会改到原数组 —— 想安全就用 .copy()")
print()

print("=" * 64)
print("现在做练习（用 python -i w2_img2array.py 进交互模式）")
print("=" * 64)
print("""
【练习 1】预测再验证
    arr.shape
    arr[0, 0]            → 左上角那个像素（3 个数）
    arr[-1, -1]          → 右下角那个像素（想想 -1 是什么）

【练习 2】取一小块区域，看看 shape
    block = arr[100:110, 200:210, :]
    block.shape          → ？
    Image.fromarray(block).save("out/block.png")    → 打开看看，10x10 的小方块

【练习 3】把一块区域涂红，存出来看
    copy = arr.copy()
    copy[100:200, 300:400, :] = [255, 0, 0]
    Image.fromarray(copy).save("out/red_box.png")

【练习 4】交换红蓝通道，猜猜画面会变成什么样
    swap = arr[:, :, ::-1]        # 通道顺序倒过来：BGR 了
    Image.fromarray(swap).save("out/bgr.png")

【练习 5】回答这个问题（用代码验证，不要猜）
    为什么 img.size[0] 是 640，而 arr.shape[0] 是 480？
""")
