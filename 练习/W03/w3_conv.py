#!/usr/bin/env python3
"""W3 任务 1：手写 2D 卷积（滑窗 + im2col 两种向量化方案）。

用法（在仓库根目录跑）：

    python 练习/W03/w3_conv.py            # 跑自测/对拍
    cd 练习/W03 && python w3_conv.py      # 也行（脚本自己会找 testdata）

=========================== 你的任务 ===========================
填完下面 2 个 TODO：
    TODO 1 —— conv2d_sliding：用【滑窗】做卷积（核心，先把这个写对）
    TODO 2 —— conv2d_im2col ：用【im2col 矩阵乘】做卷积（同结果，另种思路）

两个都要和 cv2.filter2D 对齐，验收线 PSNR ≥ 45 dB。
（实测参考实现能做到 inf，即逐像素完全一致——所以 45dB 是宽松的，
  做不到就说明逻辑有 bug，别放过。）
===============================================================

------------------------------------------------------------------------
先想清楚：卷积到底在算什么
------------------------------------------------------------------------

一张图、一个 3x3 的核。对输出图的每个位置 (y, x)：

    输出[y, x] = Σ  Σ  图[y+dy, x+dx] * 核[dy, dx]
                dy dx

也就是「把核盖在图上，对应位置相乘再全部相加，得到一个数」。

朴素写法是两层 for 循环：每个位置重算一遍乘加。
640x480 的图上，3x3 核要做 30 万 × 9 ≈ 270 万次乘加——Python 循环里约 910 ms。

关键问题：**能不能一次算完所有位置？**

能。因为「核盖在某个位置」这个动作，本质上是取原始图的一个【小窗口】。
如果预先构造出一个形状为 (高, 宽, k, k) 的四维数组——
  第 3、4 维 = 每个位置上的那个 k×k 窗口
那么一次乘加运算就是一次数组乘法 + 对最后两维求和。这就是滑窗法。

------------------------------------------------------------------------
四个必须搞清的概念（写完代码回来对照）
------------------------------------------------------------------------

1. padding（边界怎么办）
   核盖在图像最左上角时，左边和上边「没有像素」。
   cv2 默认用 BORDER_REFLECT_101：镜像复制（gfedcb | abcdefgh | gfedcb）
   numpy 里对应 np.pad(..., mode="reflect")，注意 "reflect" 和 "symmetric" 不一样：
       np.pad([a,b,c], 2, mode="reflect")   → c b | a b c | b a   （不含边缘自身）
       np.pad([a,b,c], 2, mode="symmetric") → b a | a b c | c b   （含边缘自身，等于 cv2 的 REFLECT）
   cv2.BORDER_REFLECT_101 == np.pad(mode="reflect"）  ← 默认就用这个

2. 窗口尺寸与输出尺寸
   pad 之后图像变成 (H+2p, W+2p)，滑窗视图有 (H, W) 个位置（stride=1 时）。
   np.lib.stride_tricks.sliding_window_view(padded, (k, k)) 的形状是
       (H+2p-k+1, W+2p-k+1, k, k)
   p = k//2 时，前两维正好是 (H, W) ← 所以输出尺寸和输入一样

3. stride（步长）
   stride=2 表示每隔 2 个像素取一个输出位置，输出尺寸约减半。
   滑窗视图上直接切片 [::stride, ::stride] 即可。

4. 收缩（把窗口两维压掉）
   有两种写法，结果一样，速度不同——这就是 TODO 1 和 TODO 2 的分界：
       np.einsum("ijkl,kl->ij", windows, kernel)      ← 滑窗法
       windows.reshape(h*w, k*k) @ kernel.ravel()     ← im2col 法
"""
import sys
from pathlib import Path

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

sys.path.insert(0, str(Path(__file__).resolve().parent))
from w3_metrics import check, load_gray, psnr  # noqa: E402


# ============================================================
# TODO 1：滑窗法（先把这一版写对）
# ============================================================
def conv2d_sliding(img, kernel, stride=1):
    """用滑窗做 2D 卷积。返回 uint8 图像，形状与输入相同（stride=1 时）。

    参数
    ----
    img    : (H, W) uint8 灰度图
    kernel : (k, k) 浮点核
    stride : 步长，默认 1

    返回
    ----
    (H', W') uint8，其中 H' = (H - k + 2*p)//stride + 1，p = k//2

    步骤（卡住就看这里，别直接抄答案）
    ---------------------------------------------------------------
    ① p = kernel.shape[0] // 2
    ② padded = np.pad(img.astype(np.float64), p, mode="reflect")
       ↑ 注意必须先转 float64：uint8 乘浮点核会溢出/截断（W2 的老坑）
    ③ windows = sliding_window_view(padded, kernel.shape)
       ↑ 得到一个四维数组 (H', W', k, k)
    ④ 如果 stride > 1：windows = windows[::stride, ::stride]
    ⑤ 用 einsum 把最后两维和核收缩掉，得到二维输出：
           out = np.einsum("ijkl,kl->ij", windows, kernel)
       ↑ 读法："i,j 保留，k,l 求和"——正好就是卷积的定义式
    ⑥ 返回 np.clip(np.rint(out), 0, 255).astype(np.uint8)
       ↑ 必须 rint（四舍五入）：直接 astype 是截断，会系统性偏，对拍过不了
    """
    raise NotImplementedError("TODO 1：按上面 6 步实现 conv2d_sliding")


# ============================================================
# TODO 2：im2col 法（同一件事的另一种做法）
# ============================================================
def conv2d_im2col(img, kernel, stride=1):
    """用 im2col（image to column）+ 矩阵乘法做卷积。

    思路：把每个窗口「摊平」成一行，得到矩阵 (像素数, k*k)，
    再和摊平的核 (k*k,) 做一次矩阵乘法 → (像素数,) → reshape 回图像。

        windows (H', W', k, k)  --reshape-->  (H'*W', k*k)   = 列矩阵 X
        X @ kernel.ravel()                                    = 输出 (H'*W',)
        reshape(H', W')

    为什么业界都这么做：
        矩阵乘法是所有 BLAS 库里优化最狠的操作，能直接吃满 CPU 缓存。
        深度学习框架里的卷积，底层基本就是这个思路（或等价的 FFT/Winograd）。

    和滑窗法的关系：
        数学上完全等价；区别在于 einsum 会把窗口「读一遍」再收缩，
        而 reshape + matmul 需要先真正复制出一份 im2col 矩阵——
        代价是**内存翻 k*k 倍**（3x3 核就是 9 倍），换来的是 BLAS 的速度。
        哪个快？在你的机器上实测（任务的最后一步）。
    """
    raise NotImplementedError("TODO 2：按 docstring 里的三步实现 conv2d_im2col")


# ============================================================
# 以下是【不用填】的自测与对拍部分
# ============================================================
def _naive_conv(img, kernel):
    """朴素双重循环版本——只用来证明「向量化版本算的是同一件事」。

    故意保留它：它是你 W2 学到的"对照基线"，也能直观看出慢多少。
    注意它只在缩小的图上跑（640x480 全图要十几秒）。
    """
    h, w = img.shape
    k = kernel.shape[0]
    p = k // 2
    padded = np.pad(img.astype(np.float64), p, mode="reflect")
    out = np.empty((h, w), dtype=np.float64)
    for y in range(h):
        for x in range(w):
            out[y, x] = np.sum(padded[y:y + k, x:x + k] * kernel)
    return np.clip(np.rint(out), 0, 255).astype(np.uint8)


def _kernels():
    """几个有代表性的核：通用 / 模糊 / 边缘。"""
    return {
        "3x3 Sobel_x": np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64),
        "5x5 均值": np.ones((5, 5), dtype=np.float64) / 25.0,
        "3x3 随机": np.random.default_rng(0).standard_normal((3, 3)),
        "5x5 随机": np.random.default_rng(1).standard_normal((5, 5)),
    }


def _timing(fn, *args, repeat=3):
    import time

    best = float("inf")
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn(*args)
        best = min(best, time.perf_counter() - t0)
    return best


def main():
    import cv2

    gray = load_gray("small")
    print("=" * 70)
    print("W3 任务 1 自测：手写卷积 vs cv2.filter2D")
    print("=" * 70)
    print(f"测试图：{gray.shape}  dtype={gray.dtype}")
    print()

    # ---------- ① 先证明"向量化和双层循环算的是同一件事" ----------
    print("① 小图对拍：朴素双循环 vs 滑窗（证明逻辑正确，这是最可信的检查）")
    tiny = gray[100:180, 100:240]      # 80x140 小块，循环跑得动
    kern3 = _kernels()["3x3 Sobel_x"]
    naive = _naive_conv(tiny, kern3)
    try:
        fast = conv2d_sliding(tiny, kern3)
    except NotImplementedError as e:
        print(f"   ⏸  {e}")
        print("   → 先填 TODO 1，再回来跑这个脚本")
        return
    print(f"   朴素循环 vs 滑窗：{'✅ 完全一致' if np.array_equal(naive, fast) else '❌ 不一致'}")
    print()

    # ---------- ② 与 cv2 对拍 ----------
    print("② 与 cv2.filter2D 对拍（全图，各种核）")
    all_ok = True
    for name, kern in _kernels().items():
        ref = cv2.filter2D(gray, cv2.CV_8U, kern, borderType=cv2.BORDER_REFLECT_101)
        all_ok &= check(f"滑窗 {name}", conv2d_sliding(gray, kern), ref, psnr_min=45)
    print()

    print("③ im2col 版对拍（应该和滑窗版结果完全相同）")
    for name, kern in _kernels().items():
        ref = cv2.filter2D(gray, cv2.CV_8U, kern, borderType=cv2.BORDER_REFLECT_101)
        try:
            got = conv2d_im2col(gray, kern)
        except NotImplementedError as e:
            print(f"   ⏸  {e}")
            all_ok = False
            break
        all_ok &= check(f"im2col {name}", got, ref, psnr_min=45)
        if not np.array_equal(got, conv2d_sliding(gray, kern)):
            print("      ⚠️ 和滑窗版不一致——这两种做法数学上必须完全等价")
    print()

    # ---------- ④ stride ----------
    print("④ stride 测试（stride=2 时输出尺寸应减半）")
    kern = _kernels()["3x3 Sobel_x"]
    out1 = conv2d_sliding(gray, kern, stride=1)
    out2 = conv2d_sliding(gray, kern, stride=2)
    print(f"   stride=1 → {out1.shape}     stride=2 → {out2.shape}")
    expected = ((gray.shape[0] - 1) // 2 + 1, (gray.shape[1] - 1) // 2 + 1)
    print(f"   预期 stride=2 → {expected}   {'✅' if out2.shape == expected else '❌'}")
    print()

    # ---------- ⑤ 三种实现的速度 ----------
    print("⑤ 速度对比（640x480，5x5 核，各跑 3 次取最快）")
    kern5 = _kernels()["5x5 均值"]
    t_slide = _timing(conv2d_sliding, gray, kern5)
    print(f"   滑窗 (einsum)  : {t_slide * 1000:8.1f} ms")
    try:
        t_im2col = _timing(conv2d_im2col, gray, kern5)
        print(f"   im2col (matmul): {t_im2col * 1000:8.1f} ms")
        print(f"   → {'im2col' if t_im2col < t_slide else '滑窗'} 更快，"
              f"相差 {max(t_slide, t_im2col) / min(t_slide, t_im2col):.2f} 倍")
    except NotImplementedError:
        print("   im2col (matmul): —（还没填 TODO 2）")
    print()

    # ---------- ⑥ 结论 ----------
    print("=" * 70)
    if all_ok:
        print("✅ 全部通过。任务 1 完成——你手写的卷积已经和 OpenCV 逐像素对齐。")
        print()
        print("   进下一题前，回答三个问题（答不上说明还是抄的）：")
        print("   1. einsum(\"ijkl,kl->ij\") 里 i/j/k/l 各指什么？为什么 k,l 要消掉？")
        print("   2. 为什么必须先 astype(np.float64)？直接 uint8 乘浮点核会怎样？")
        print("   3. np.pad 的 'reflect' 和 'symmetric' 差在哪？换成另一个 PSNR 会掉多少？")
    else:
        print("❌ 还有没通过的项目，看上面的 ❌ 行。")
        print("   排查顺序：padding 模式 → float64 转换 → rint vs astype → einsum 下标")


if __name__ == "__main__":
    main()
