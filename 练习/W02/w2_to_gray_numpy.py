#!/usr/bin/env python3
"""W2 任务 3 骨架：用 NumPy 向量化实现灰度化。

用法（在仓库根目录跑）:
    cd ~/cv-kit
    python 练习/W02/w2_to_gray_numpy.py

注意：这是练习区文件。W1 的正式交付版是根目录的 grayscale_cli.py（循环版），
       本文件是它的向量化版本；W2 结束后两版都保留，用于对拍与性能对比。

=========================== 你的任务 ===========================
把下面 3 个 TODO 填完。参考：
  · 公式  Y = 0.299R + 0.587G + 0.114B   （W1 已经用过）
  · 取通道 arr[:, :, 0] 表示"整张红色图"（三维索引笔记里有）
  · 数组运算不需要循环 —— 直接对整张图做加减乘除

填完跑这个文件，会打印结果。再跑 w2_verify.py 做严格对拍。
===============================================================
"""
import numpy as np
from PIL import Image


def to_gray_numpy(img):
    """把 PIL 图片用 NumPy 向量化方式转成灰度，返回 np.ndarray (uint8, 二维)。

    与循环版 to_gray() 的要求完全一致：
      · 同样的公式 Y = 0.299R + 0.587G + 0.114B
      · 同样的取整方式：截断（int() 和 astype(uint8) 行为一致）
      · 不同的只是：不用循环
    """
    arr = np.array(img)                       # (高, 宽, 3)  uint8

    # ---------- TODO 1：把 uint8 转成浮点 ----------
    # 为什么必须转？uint8 只能存 0~255 的整数，
    # 而 0.299*r 算出来是小数（比如 27.209），直接算会被截断成 27，结果就错了。
    arr = __填这里__                           # 提示：arr.astype(np.float64)

    # ---------- TODO 2：取三个通道并套公式 ----------
    # 这里的每一行都是"一整张图（高, 宽）"，不是单个像素！
    r = __填这里__                             # 提示：arr[:, :, 0]
    g = __填这里__                             # 提示：arr[:, :, 1]
    b = __填这里__                             # 提示：arr[:, :, 2]

    y = __填这里__                             # 提示：0.299*r + 0.587*g + 0.114*b（没有循环！）

    # ---------- TODO 3：转回 0~255 的整数 ----------
    # np.clip 是保险：即使公式算出来理论上在 0~255 内，浮点误差也可能越界一点点，
    #               而 uint8 遇到 256 会"回绕"成 0（黑变白），所以先夹紧再转类型。
    y = np.clip(y, 0, 255)
    return y.astype(np.uint8)                 # 截断（和 int() 行为一致）


if __name__ == "__main__":
    img = Image.open("testdata/small_640x480.jpg")
    result = to_gray_numpy(img)
    print(f"输入 : {img.size} {img.mode}")
    print(f"输出 : shape={result.shape}  dtype={result.dtype}")
    print(f"中心点 (240, 320) = {result[240, 320]}   （循环版的答案是 148）")
    print(f"左上角 (0, 0)     = {result[0, 0]}       （循环版是 0）")

    Image.fromarray(result).save("out/small_numpy_gray.png")
    print("\n已存 out/small_numpy_gray.png，打开和 out/small_640x480_gray.png 对比")
