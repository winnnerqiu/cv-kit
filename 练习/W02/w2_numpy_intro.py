#!/usr/bin/env python3
"""W2 任务 1：NumPy 探索（交互模式专用）。

用法:
    cd ~/cv-kit
    python -i 练习/W02/w2_numpy_intro.py

跑完会停在 >>> 提示符，变量都还在。然后照下面的【练习】一条条敲，验证你的理解。
"""
import numpy as np

print("=" * 62)
print("第一部分：列表 vs 数组 —— NumPy 凭什么能取消循环")
print("=" * 62)

py_list = [1, 2, 3]
np_arr = np.array([1, 2, 3])

print(f"  Python 列表 : {py_list}")
print(f"  NumPy  数组 : {np_arr}")
print()
print("  试试让它们各自乘 2：")
print(f"    py_list * 2        → {py_list * 2}")
print(r"    （列表变成 6 个元素：内容重复两遍 —— Python 不懂数学）")
print(f"    np_arr * 2         → {np_arr * 2}")
print("    （每个元素都乘了 2 —— 这就是向量化）")
print()
print("  加一个数：")
print("    py_list + 2        → 会直接报 TypeError（注释掉的那行可以自己试）")
print(f"    np_arr + 2         → {np_arr + 2}")
print()

print("=" * 62)
print("第二部分：数组的形状 shape —— 一维、二维、三维")
print("=" * 62)

vec = np.array([10, 20, 30])                       # 一维：一串
mat = np.array([[1, 2, 3], [4, 5, 6]])             # 二维：表格（2 行 3 列）
cube = np.zeros((2, 3, 4))                         # 三维：一堆表格

print(f"  一维 vec   = {vec}          shape = {vec.shape}")
print(f"  二维 mat   = 见下            shape = {mat.shape}")
print(f"      {mat}")
print(f"  三维 cube  shape = {cube.shape}   （2 张 3 行 4 列的表）")
print()
print("  ★ shape 读法：(2, 3) = 2 行 3 列；(2, 3, 4) = 2 个、每个 3 行 4 列")
print("  ★ 图片就是三维数组：(高, 宽, 通道数) —— 稍后验证")
print()

print("=" * 62)
print("第三部分：取值和切片 —— 一个括号 + 逗号")
print("=" * 62)

print(f"  mat = {mat.tolist()}")
print()
print(f"  mat[0]        → {mat[0]}        取第 0 行（一整行）")
print(f"  mat[1]        → {mat[1]}        取第 1 行")
print(f"  mat[1, 2]     → {mat[1, 2]}           第 1 行第 2 列（注意是【一个】括号）")
print(f"  mat[1][2]     → {mat[1][2]}           这样写也行，效果一样")
print(f"  mat[:, 0]     → {mat[:, 0]}        所有行、第 0 列（一整列）")
print(f"  mat[:, 2]     → {mat[:, 2]}        所有行、第 2 列")
print(f"  mat[:, 1:]    → 见下")
print(f"      {mat[:, 1:]}")
print("      ↑ 所有行、从第 1 列到末尾（切片：起点含、终点不含）")
print()

print("=" * 62)
print("第四部分：轴 axis —— 沿哪个方向算")
print("=" * 62)

print(f"  mat = {mat.tolist()}")
print(f"  mat.sum()            → {mat.sum()}       （全部加起来）")
print(f"  mat.sum(axis=0)      → {mat.sum(axis=0)}       （每列求和：1+4, 2+5, 3+6）")
print(f"  mat.sum(axis=1)      → {mat.sum(axis=1)}       （每行求和：1+2+3, 4+5+6）")
print(f"  mat.mean(axis=0)     → {mat.mean(axis=0)}     （每列平均）")
print()
print("  ★ 口诀：axis=0 是【把行压扁】（竖着加），axis=1 是【把列压扁】（横着加）")
print("  ★ 拿不准就记结果：axis=0 得到 3 个数（列数），axis=1 得到 2 个数（行数）")
print()

print("=" * 62)
print("第五部分：类型 dtype —— 图片为什么用 uint8")
print("=" * 62)

d = mat.mean(axis=0)
print(f"  整数数组 mat.dtype          = {mat.dtype}")
print(f"  平均之后 d.dtype            = {d.dtype}      ← 变成小数了！")
print(f"  d.astype(np.uint8)          = {d.astype(np.uint8)}    ← 转回 0~255 整数")
print(f"  0.9 转 uint8                = {np.array([0.9]).astype(np.uint8)}       ← 是截断，不是四舍五入！")
print(f"  -1 转 uint8                 = {np.array([-1]).astype(np.uint8)}     ← 负数会回绕！（这是个坑）")
print()
print("  ★ uint8 = 无符号 8 位整数，范围 0~255 —— 正好是图片像素的取值范围")
print()

print("=" * 62)
print("现在停在交互模式，变量都在。照下面的练习自己敲：")
print("=" * 62)
print("""
【练习 1】预测再验证（先想答案，再敲）
    mat.shape                    → 应该是啥？
    mat[0, 0]                    → ？
    mat[:, 1]                    → ？

【练习 2】自己造一个 3 行 4 列的数组（用 np.arange 或直接写列表）
    a = np.arange(12).reshape(3, 4)
    a                            → 长什么样？
    a.shape                      → ？
    a[2, 3]                      → ？
    a[:, 0]                      → 第 0 列
    a.mean(axis=1)               → 每行平均

【练习 3】列表 vs 数组的对比实验
    L = [1, 2, 3]
    A = np.array([1, 2, 3])
    L * 3                        → ？
    A * 3                        → ？
    L + L                        → ？
    A + A                        → ？ （和 L + L 有什么不同？）

【练习 4】造图片形状的数组
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    img.shape                    → (480, 640, 3)
    img[0, 0]                    → 左上角那个像素（三个数）
    img[:, :, 0].shape           → ？ （只取红色通道）
    img[100:110, 200:210].shape  → ？ （取一小块）

【练习 5】把这块小区域涂白
    img[100:110, 200:210] = 255
    img[105, 205]                → 验证是不是变成 [255 255 255] 了

想退出：exit()
""")
