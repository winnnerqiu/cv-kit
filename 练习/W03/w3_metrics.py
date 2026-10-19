#!/usr/bin/env python3
"""W3 评估工具：PSNR / SSIM / 一键对拍（这个文件是【完整可用】的，不用填）。

用法（在仓库根目录跑）：

    python 练习/W03/w3_metrics.py                 # 自检：跑一遍 PSNR/SSIM 的定义验证
    python 练习/W03/w3_metrics.py --img scene     # 换大图自检

为什么它不能直接调 skimage：
    你的 vision 环境没装 scikit-image，所以 SSIM 必须自己实现。
    正好——手写一遍 SSIM，比调库里函数更懂它到底在量什么。

对拍时怎么用（你写的每个算子文件都会 import 这里的 psnr / ssim）：

    from w3_metrics import psnr, ssim, check
    check("均值滤波", mine, ref, psnr_min=45)
"""
import argparse
import sys
from pathlib import Path

import numpy as np

# 让脚本在任意工作目录都能找到 testdata/
ROOT = Path(__file__).resolve().parents[2]


def to_u8(x):
    """浮点数组 → 0~255 的 uint8（四舍五入 + 夹紧）。

    为什么必须夹紧：cv2 的滤波输出越界时会饱和到 0/255，
    而 uint8 直接转换是【回绕】（256→0，黑变白），W2 已经踩过这个坑。
    """
    return np.clip(np.rint(x), 0, 255).astype(np.uint8)


def psnr(a, b, data_range=255.0):
    """峰值信噪比，单位 dB。越大越接近。

    公式：PSNR = 10 * log10(MAX^2 / MSE)
        MAX = 255（8 位图像的峰值）
        MSE = 两图差的平方的均值

    读数对照（255 灰阶图像）：
        平均差 1 灰阶 → 约 48 dB
        平均差 2 灰阶 → 约 42 dB
        平均差 5 灰阶 → 约 34 dB
        平均差 10 灰阶 → 约 28 dB
    所以「PSNR > 40dB」大致等于「平均每像素差不到 2.5 个灰阶」。
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.shape != b.shape:
        raise ValueError(f"形状不一致：{a.shape} vs {b.shape}")
    mse = float(np.mean((a - b) ** 2))
    if mse == 0.0:
        return float("inf")
    return 10.0 * np.log10(data_range ** 2 / mse)


def ssim(a, b, win=7, data_range=255.0):
    """结构相似度 SSIM，范围 [-1, 1]，越接近 1 越像。

    和 PSNR 的区别（这是 W3 值得想明白的一个问题）：
        PSNR 只看「每个像素差多少」——位移 1 个像素的图，PSNR 会暴跌，
        但人眼几乎看不出区别。
        SSIM 看「亮度、对比度、结构」三件事有没有一起变，
        所以对「结构是否还在」更敏感，和人的观感相关性更好。

    实现要点（Wang et al. 2004 的思路，用均值窗简化版）：
        在局部窗口里算  均值 mu、方差 sigma^2、协方差 sigma_ab
        SSIM = (2*mu_a*mu_b + C1)(2*sigma_ab + C2)
             / (mu_a^2 + mu_b^2 + C1)(sigma_a^2 + sigma_b^2 + C2)
        C1 = (0.01*L)^2, C2 = (0.03*L)^2   ← 防止分母为 0
        最后对所有局部值取平均。

    注意：这里的窗口是均值窗（7x7），原论文用的是 11x11 高斯窗，
    所以数值和 skimage 的 ssim() 不完全一样，但趋势一致、可用于横向比较。
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.shape != b.shape:
        raise ValueError(f"形状不一致：{a.shape} vs {b.shape}")

    C1 = (0.01 * data_range) ** 2
    C2 = (0.03 * data_range) ** 2
    k = np.ones((win, win), dtype=np.float64) / (win * win)
    p = win // 2

    def local_sum(x):
        """局部窗口内求和（滑窗 + 逐元素乘，然后把窗口两维收缩掉）。"""
        xp = np.pad(x, p, mode="reflect")
        windows = np.lib.stride_tricks.sliding_window_view(xp, (win, win))
        return np.einsum("ijkl,kl->ij", windows, k)

    mu_a = local_sum(a)
    mu_b = local_sum(b)
    mu_aa = local_sum(a * a)
    mu_bb = local_sum(b * b)
    mu_ab = local_sum(a * b)

    var_a = mu_aa - mu_a ** 2
    var_b = mu_bb - mu_b ** 2
    cov_ab = mu_ab - mu_a * mu_b

    num = (2 * mu_a * mu_b + C1) * (2 * cov_ab + C2)
    den = (mu_a ** 2 + mu_b ** 2 + C1) * (var_a + var_b + C2)
    return float(np.mean(num / den))


def load_gray(which="small"):
    """读一张测试灰度图。which: small(640x480) / scene(1920x1080) / gray(L 模式)"""
    import cv2

    names = {
        "small": "testdata/small_640x480.jpg",
        "scene": "testdata/scene_1920x1080.jpg",
        "gray": "testdata/already_gray_800x600.png",
    }
    path = ROOT / names[which]
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"读不到 {path}（请在仓库根目录运行）")
    return img


def check(name, mine, ref, psnr_min=45.0):
    """对拍 + 验收判定，打印一行结果。返回是否通过。"""
    d = np.abs(mine.astype(int) - ref.astype(int))
    p = psnr(mine, ref)
    s = ssim(mine, ref)
    ok = bool(mine.shape == ref.shape and p >= psnr_min)
    mark = "✅" if ok else "❌"
    p_txt = "inf" if p == float("inf") else f"{p:.1f}"
    print(f"  {mark} {name:22s} PSNR {p_txt:>6s} dB  SSIM {s:.4f}  "
          f"最大差 {d.max():>3d}  不一致 {100 * (d != 0).mean():5.2f}%  "
          f"（线 {psnr_min} dB）")
    return ok


def _selftest(which="small"):
    """不依赖你写的任何代码，验证 psnr/ssim 本身是否可信。"""
    img = load_gray(which)
    print(f"自检图：{which}  shape={img.shape}  dtype={img.dtype}")
    print()

    print("① PSNR 定义验证（拿人工噪声算，和公式对一遍）")
    for delta in (1, 2, 5, 10):
        noisy = np.clip(img.astype(int) + delta, 0, 255).astype(np.uint8)
        print(f"   人为加 {delta:2d} 灰阶 → PSNR {psnr(img, noisy):5.1f} dB")

    print()
    print("② 边界情况")
    print(f"   自己和自己比      PSNR = {psnr(img, img)}   （应为 inf）")
    print(f"   自己和自己比      SSIM = {ssim(img, img):.6f}  （应为 1.0）")

    print()
    print("③ SSIM 对结构变化敏感、对整体亮度变化较宽容")
    import cv2

    shifted = np.roll(img, 5, axis=1)                           # 横向平移 5 像素
    blurred = cv2.blur(img, (5, 5))                             # 轻微模糊
    darker = np.clip(img.astype(float) * 0.9, 0, 255).astype(np.uint8)  # 整体变暗 10%
    print(f"   平移 5 像素   PSNR {psnr(img, shifted):5.1f} dB   SSIM {ssim(img, shifted):.4f}")
    print(f"   5x5 模糊      PSNR {psnr(img, blurred):5.1f} dB   SSIM {ssim(img, blurred):.4f}")
    print(f"   整体暗 10%    PSNR {psnr(img, darker):5.1f} dB   SSIM {ssim(img, darker):.4f}")
    print("   ↑ 观察：哪个指标对『平移』更敏感？哪个对『整体变暗』更宽容？")
    print("     这就是 PSNR 和 SSIM 各自量的是什么——写进对标报告的结论里。")

    print()
    print("✅ 自检完成。这套指标可以拿去判断你手写的算子对不对了。")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="W3 评估工具自检")
    ap.add_argument("--img", default="small", choices=["small", "scene", "gray"])
    args = ap.parse_args()
    try:
        _selftest(args.img)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)
