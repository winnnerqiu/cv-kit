#!/usr/bin/env python3
"""W2 补充练习：三维索引，从二维一步步推到三维。

用法:
    cd ~/cv-kit
    python 练习/W02/w2_ndim_practice.py

设计：每个实验都存一张小图到 out/ndim/ 里，你可以用眼睛验证理解对不对。
"""
import os
import numpy as np
from PIL import Image

os.makedirs("out/ndim", exist_ok=True)

# 造一张 3 行 4 列 3 通道的迷你"图片"
# 每个像素的颜色都是 (R, G, B)，值刻意做成好认的规律
arr = np.zeros((3, 4, 3), dtype=np.uint8)
for y in range(3):
    for x in range(4):
        arr[y, x] = [y * 100, x * 80, 50]     # 红随行变、绿随列变、蓝固定

print("=" * 64)
print("实验 0：先看清这张迷你图的 shape 和内容")
print("=" * 64)
print(f"  arr.shape = {arr.shape}   →  (行=3, 列=4, 通道=3)")
print(f"  arr[0, 0] = {arr[0, 0]}   ← 左上角像素")
print(f"  arr[2, 3] = {arr[2, 3]}   ← 右下角像素")
print(f"  arr[1, 2] = {arr[1, 2]}   ← 中间某点")
Image.fromarray(arr).save("out/ndim/00_原图.png")
print("  已存 out/ndim/00_原图.png（3x4 的小图，放大看是一个 3x4 的色块阵）")
print()

print("=" * 64)
print("实验 1：arr[行, 列] —— 一个像素（3 个数）")
print("=" * 64)
print(f"  arr[1, 2]      = {arr[1, 2]}   shape = {arr[1, 2].shape}")
print(f"  arr[1][2]      = {arr[1][2]}   ← 完全等价，两种写法")
print("  ★ 少写一个下标 = 那一维全都要（这里通道全要，所以是 3 个数）")
print()

print("=" * 64)
print("实验 2：arr[行] —— 一整行")
print("=" * 64)
row = arr[1]
print(f"  arr[1].shape   = {row.shape}   ← (列数, 通道数)，二维！")
print(f"  arr[1] =")
print(f"    {row.tolist()}")
print("  ★ 写了一个具体数字(1) + 一个隐含的'全都要' → 维度从 3 降到 2")
print()

print("=" * 64)
print("实验 3：arr[:, :, 通道] —— 整张单通道图（二维）")
print("=" * 64)
for c, name in enumerate(["红 R", "绿 G", "蓝 B"]):
    ch = arr[:, :, c]
    print(f"  arr[:, :, {c}] ({name}).shape = {ch.shape}   二维！")
    print(f"    {ch.tolist()}")
    Image.fromarray(ch).save(f"out/ndim/03_通道{c}_{name[0]}.png")
print("  ★ 已存 out/ndim/03_通道*.png —— 打开看，三张都是灰度的二维图")
print("  ★ 这就是灰度公式的素材：r = arr[:, :, 0] 等等")
print()

print("=" * 64)
print("实验 4：arr[:, 列, :] —— 一整列（保留所有通道）")
print("=" * 64)
col = arr[:, 2, :]
print(f"  arr[:, 2, :].shape = {col.shape}   ← (行数, 通道数)")
print(f"    {col.tolist()}")
print("  ★ 对比：实验 2 取的是【一整行】，实验 4 取的是【一整列】")
print()

print("=" * 64)
print("实验 5：塌陷规律总结（做一遍，就记住了）")
print("=" * 64)
tests = [
    ("arr[1, 2]",       arr[1, 2]),
    ("arr[1]",          arr[1]),
    ("arr[:, :, 0]",    arr[:, :, 0]),
    ("arr[:, 2, :]",    arr[:, 2, :]),
    ("arr[:, :, :]",    arr[:, :, :]),
]
for expr, result in tests:
    print(f"  {expr:16s} → shape = {str(result.shape):10s}  {result.shape and ''}")
print()
print("  规律：写几个具体数字，就塌掉几个维度")
print("    3 个数字 → 0 维（一个数） / 2 个数字 → 1 维 / 1 个数字 → 2 维 / 0 个 → 3 维")
print()

print("=" * 64)
print("现在轮到你了（python -i w2_ndim_practice.py）")
print("=" * 64)
print("""
【预测 1】arr[0].shape        → ?
【预测 2】arr[:, 1].shape     → ?   （注意：这和 arr[:, 1, :] 是不是一回事？）
【预测 3】arr[2, 3].shape     → ?
【预测 4】arr[:, :, 2].shape  → ?

【思考】为什么 arr[:, :, 0] 出来是二维的，而 arr[0, :, :] 也是二维的？
       两者取的东区域有什么不同？（一个是"一整张红色图"，一个是"最上面一行"）

【实战】把三个通道按不同权重合成灰度（这就是任务 3！）
    y = (0.299 * arr[:, :, 0].astype(float)
       + 0.587 * arr[:, :, 1].astype(float)
       + 0.114 * arr[:, :, 2].astype(float))
    y.shape      → ?
    Image.fromarray(y.astype(np.uint8)).save("out/ndim/99_我的第一张向量化灰度.png")
""")
