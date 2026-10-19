#!/usr/bin/env python3
"""W3 任务 2：均值滤波 / 高斯滤波 / 中值滤波。

用法（仓库根目录）：
    python 练习/W03/w3_filters.py

=========================== 你的任务 ===========================
    TODO 1 —— mean_blur    ：均值滤波（最简单，先把卷积那套用熟）
    TODO 2 —— gaussian_blur：高斯滤波（难点在于核怎么算，尤其 sigma 的自动取值）
    TODO 3 —— median_blur  ：中值滤波（不是卷积！聚合方式不同）

验收线：均值/中值 ≥ 50 dB，高斯 ≥ 55 dB（对拍 cv2）。
===============================================================

------------------------------------------------------------------------
三种滤波的差别（这张表是 W3 面试题的原型）
------------------------------------------------------------------------

| 滤波器 | 核心运算 | 擅长 | 代价 |
| --- | --- | --- | --- |
| 均值 | 窗口内求【平均】 | 快、简单 | 糊边缘；脉冲噪声只是被"摊薄" |
| 高斯 | 窗口内【加权】平均，中心权重最大 | 平滑还保结构 | 需要算核；对脉冲噪声无能为力 |
| 中值 | 窗口内取【中位数】 | 专杀椒盐噪声，几乎不糊边 | 排序开销大（比卷积慢） |

一句话记法：
    均值 = 大家一起平均，边缘也被平均掉
    高斯 = 离得越近越重要，所以边缘能保住一点
    中值 = 排个队取中间那个，孤立的噪点直接被投票投死

------------------------------------------------------------------------
高斯滤波的两个坑（不踩这两个坑，PSNR 上不去）
------------------------------------------------------------------------

坑 1：核必须【归一化】
    二维高斯：G(x,y) = exp(-(x²+y²) / (2σ²))
    但这样算出来的矩阵总和不是 1（比如 5x5、σ=1.1 时总和约 16）。
    不除以总和，卷积后整张图会被放大十几倍 → 一片白 → PSNR 只有 6 dB。
    正确做法：kernel /= kernel.sum()

坑 2：σ 和 ksize 的对应关系
    你写 gaussian_blur(img, ksize=5)，sigma 从哪来？
    cv2 的规则是：sigma=0 时自动按 ksize 推算
        σ = 0.3 × ((ksize - 1) × 0.5 - 1) + 0.8
    代入：ksize=3 → σ=0.8；ksize=5 → σ=1.1；ksize=7 → σ=1.4；ksize=9 → σ=1.7
    用错这个公式，PSNR 会掉到 5~6 dB（核形状不对，整张图就糊崩了）。
    ⚠️ 这是 W3 最容易被忽略的一个知识点——面试常问「你高斯核的 sigma 怎么定的」。

------------------------------------------------------------------------
中值滤波为什么不能套卷积
------------------------------------------------------------------------
卷积是【乘加】，可以写成矩阵乘法、可以用 einsum 收缩、可以吃 BLAS。
中位数不是线性运算——它要求排序，没法表达成一次矩阵乘。
所以中值滤波只能"取窗口 + 排序"：
    windows = sliding_window_view(padded, (k,k))     # (H, W, k, k)
    np.median(windows, axis=(-1, -2))                # 每窗口取中位数
np.median 内部会对 k*k 个数做 partition（部分排序，比全排序快）。
仍然比卷积慢——这正是"不是所有图像操作都能用矩阵乘法加速"的例子。
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from w3_conv import conv2d_sliding  # noqa: E402  ← 卷积写好了，滤波直接复用
from w3_metrics import check, load_gray  # noqa: E402


# ============================================================
# TODO 1：均值滤波
# ============================================================
def mean_blur(img, ksize=5):
    """均值滤波：窗口内像素求平均。

    实现提示（3 行就够）
    ---------------------------------------------------------------
    · 均值滤波 = 用「全 1 的核除以 ksize²」做卷积
    · 直接复用 w3_conv.conv2d_sliding，不用重写滑窗逻辑
    · 核构造：np.ones((ksize, ksize)) / (ksize * ksize)

    对照：cv2.blur(img, (ksize, ksize))
    """
    raise NotImplementedError("TODO 1：用全 1 归一化核调用 conv2d_sliding")


# ============================================================
# TODO 2：高斯滤波（这题是重点）
# ============================================================
def gaussian_kernel_1d(ksize, sigma=None):
    """生成一维高斯核（长度 ksize，已归一化）。

    σ 的规则（cv2 的约定）：
        sigma 为 None 或 <= 0 时，σ = 0.3 * ((ksize - 1) * 0.5 - 1) + 0.8

    一维高斯：g(x) = exp(-x² / (2σ²))，x 取 -(ksize-1)/2 ... +(ksize-1)/2
    例：ksize=5 → x = [-2,-1,0,1,2]
    最后 g /= g.sum()   ← 归一化，别忘

    自己验一下：ksize=5, σ=1.1 时，
        g ≈ [0.0709, 0.2444, 0.3693, 0.2444, 0.0709]   （g.sum() 应为 1）
    """
    raise NotImplementedError("TODO 2a：实现一维高斯核生成")


def gaussian_blur(img, ksize=5, sigma=None):
    """高斯滤波：用 separable 的思路，但这里先用二维核直接卷积。

    实现提示
    ---------------------------------------------------------------
    · 二维核 = 一维核的【外积】：k2d = np.outer(g, g)
      为什么外积就对？因为二维高斯本身就是可分离的：
          exp(-(x²+y²)/2σ²) = exp(-x²/2σ²) × exp(-y²/2σ²)
      两个一维核都已归一化，外积的总和也正好是 1。
    · 然后 conv2d_sliding(img, k2d)

    进阶思考（不用写进代码，但要想明白）：
        直接把二维核卷积，是 ksize² 次乘法/像素；
        而 separable 做法是「先横向卷积一次，再纵向卷积一次」，
        只需 2×ksize 次乘法/像素。ksize=5 时 25 → 10，快 2.5 倍。
        cv2 内部就是这么做的。

    对照：cv2.GaussianBlur(img, (ksize, ksize), sigma or 0)
    ⚠️ cv2 的 sigma 参数传 0 表示"按 ksize 自动算"，和上面的公式一致。
    """
    raise NotImplementedError("TODO 2b：用外积构造二维核后卷积")


# ============================================================
# TODO 3：中值滤波
# ============================================================
def median_blur(img, ksize=3):
    """中值滤波：每个窗口取中位数（不是平均值！）。

    实现提示
    ---------------------------------------------------------------
    ① p = ksize // 2
    ② padded = np.pad(img, p, mode=?)     ← 边界模式要选对，见下
    ③ windows = sliding_window_view(padded, (ksize, ksize))   # (H, W, k, k)
    ④ return np.median(windows, axis=(-1, -2)).astype(np.uint8)

    边界模式是个坑：
        cv2.medianBlur 用的是 BORDER_REPLICATE（复制边缘像素），
        numpy 里对应 np.pad(..., mode="edge")。
        如果你用 'reflect'，形状没错但边缘那一圈会和 cv2 差一点
        （实测最大差 1 灰阶、约 0.1% 像素，PSNR 仍有 78~81 dB，能过线但不够完美）。
        **想拿满分就试出正确的 mode。** 这是一个很值得记的"边界处理差异"案例。

    为什么不能对中值用卷积：中位数不是线性运算，没法写成矩阵乘法。
    """
    raise NotImplementedError("TODO 3：取窗口后对 (k,k) 两维求中位数")


# ============================================================
# 以下是【不用填】的对拍部分
# ============================================================
def _kernels():
    return {
        "3x3 Sobel_x": np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64),
        "5x5 均值": np.ones((5, 5), dtype=np.float64) / 25.0,
        "3x3 随机": np.random.default_rng(0).standard_normal((3, 3)),
        "5x5 随机": np.random.default_rng(1).standard_normal((5, 5)),
    }


def main():
    import cv2

    gray = load_gray("small")
    gray_big = load_gray("scene")
    print("=" * 70)
    print("W3 任务 2 自测：手写滤波 vs cv2")
    print("=" * 70)
    print(f"测试图：{gray.shape}")
    print()

    done = 0

    # ---------- 均值 ----------
    print("① 均值滤波 vs cv2.blur")
    for k in (3, 5, 7):
        try:
            mine = mean_blur(gray, k)
        except NotImplementedError as e:
            print(f"   ⏸  {e}")
            break
        check(f"mean_blur k={k}", mine, cv2.blur(gray, (k, k)), psnr_min=50)
        done += 1
    print()

    # ---------- 高斯 ----------
    print("② 高斯滤波 vs cv2.GaussianBlur（sigma=0 自动）")
    for k in (3, 5, 7, 9):
        try:
            mine = gaussian_blur(gray, k)
        except NotImplementedError as e:
            print(f"   ⏸  {e}")
            break
        sigma = 0.3 * ((k - 1) * 0.5 - 1) + 0.8
        print(f"   （ksize={k} → σ={sigma:.2f}）")
        check(f"gaussian k={k}", mine, cv2.GaussianBlur(gray, (k, k), 0), psnr_min=55)
        done += 1

    # 单独验核长什么样
    try:
        g = gaussian_kernel_1d(5)
        print(f"   一维核 ksize=5：{np.array2string(g, precision=4)}  总和={g.sum():.6f}")
        print(f"   期望约 [0.0709 0.2444 0.3693 0.2444 0.0709]，总和应=1.0")
    except NotImplementedError:
        pass
    print()

    # ---------- 中值 ----------
    print("③ 中值滤波 vs cv2.medianBlur")
    for k in (3, 5):
        try:
            mine = median_blur(gray, k)
        except NotImplementedError as e:
            print(f"   ⏸  {e}")
            break
        ref = cv2.medianBlur(gray, k)
        check(f"median k={k}", mine, ref, psnr_min=50)
        d = np.abs(mine.astype(int) - ref.astype(int))
        if (d != 0).sum() > 0:
            ys, xs = np.where(d != 0)
            edge = ((ys < k) | (ys > gray.shape[0] - k - 1)
                    | (xs < k) | (xs > gray.shape[1] - k - 1))
            print(f"      不一致像素中，位于边缘一圈的占 {100 * edge.mean():.1f}% "
                  f"→ 说明是【边界模式】没对上，不是算法错")
        done += 1
    print()

    # ---------- 中值 vs 均值：椒盐噪声实验 ----------
    print("④ 为什么要有中值滤波（椒盐噪声对比实验）")
    rng = np.random.default_rng(42)
    noisy = gray.copy()
    n_salt = 3000
    ys = rng.integers(0, gray.shape[0], n_salt)
    xs = rng.integers(0, gray.shape[1], n_salt)
    noisy[ys[::2], xs[::2]] = 255      # 盐噪声（白点）
    noisy[ys[1::2], xs[1::2]] = 0      # 椒噪声（黑点，取隔一个位置避免覆盖）
    print(f"   加了 {n_salt} 个椒盐噪点到干净图")
    from w3_metrics import psnr as _p
    print(f"   噪声图      vs 干净图 : {_p(noisy, gray):5.1f} dB   ← 基线，越低越脏")
    for label, fn in (("均值 k=3", lambda: mean_blur(noisy, 3)),
                      ("中值 k=3", lambda: median_blur(noisy, 3))):
        try:
            print(f"   {label}    vs 干净图 : {_p(fn(), gray):5.1f} dB")
        except NotImplementedError as e:
            print(f"   {label}    vs 干净图 : —（{e}）")
    print("   ↑ 中值应该明显高于是均值——这就是中值滤波存在的理由，写进对标报告")
    print()

    # ---------- 速度 ----------
    print("⑤ 速度对比（1920x1080，各跑 3 次取最快）")
    import time

    def _t(fn, *a, n=3):
        best = float("inf")
        for _ in range(n):
            t0 = time.perf_counter()
            fn(*a)
            best = min(best, time.perf_counter() - t0)
        return best

    for name, mine_fn, ref_fn in [
        ("均值 k=5", lambda i: mean_blur(i, 5), lambda i: cv2.blur(i, (5, 5))),
        ("高斯 k=5", lambda i: gaussian_blur(i, 5), lambda i: cv2.GaussianBlur(i, (5, 5), 0)),
        ("中值 k=5", lambda i: median_blur(i, 5), lambda i: cv2.medianBlur(i, 5)),
    ]:
        try:
            t_mine = _t(mine_fn, gray_big)
            t_ref = _t(ref_fn, gray_big)
            print(f"   {name:10s} 手写 {t_mine * 1000:7.1f} ms   cv2 {t_ref * 1000:6.1f} ms   "
                  f"慢 {t_mine / t_ref:5.1f} 倍")
        except NotImplementedError:
            print(f"   {name:10s} —（还没填）")
    print("   ↑ 慢是正常的。cv2 是 C++ + SIMD + 定点优化。要问的是「慢多少、为什么」。")
    print()

    print("=" * 70)
    print(f"{'✅ 任务 2 完成' if done >= 9 else '⏸ 还有 TODO 没填'}"
          f"（已通过 {done} 项检查）")
    print()
    print("答得上这三个问题才算真会：")
    print("  1. 高斯核为什么要归一化？不归一会发生什么（用你踩的坑回答）？")
    print("  2. σ 和 ksize 是什么关系？如果 σ 变小，图像会变模糊还是变锐利？")
    print("  3. 中值滤波为什么不能用卷积做？它凭什么能杀掉椒盐噪声？")


if __name__ == "__main__":
    main()
