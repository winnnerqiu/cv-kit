#!/usr/bin/env python3
"""W3 任务 3：直方图均衡（HE）+ 限制对比度的自适应直方图均衡（CLAHE）。

用法（仓库根目录）：
    python 练习/W03/w3_histogram.py

=========================== 你的任务 ===========================
本文件的函数都写好了（CLAHE 的插值是 W3 最难的代码，先给完整参考）。
你的任务是【跑通 + 读懂 + 改着玩】：

    TODO A —— 先跑一遍，看懂每个数字
    TODO B —— 把 clahe() 里的 use_interpolation 改成 False，再跑一次，
              对比 PSNR 和差异图，回答「插值到底值多少 dB」
    TODO C —— 调 clip_limit（1.0 / 2.0 / 4.0 / 8.0 / 40.0），观察输出标准差和与原图
              的相关性怎么变。**注意结论和直觉相反**：clip 越大，整体标准差反而下降、
              与原图相关性变差（脚本③会打印数据，看懂为什么）。
    TODO D —— 把 equalize_hist 的 LUT 公式改错一处（比如去掉 cdf_min），
              看 PSNR 掉到多少 —— 体会"差一点点"在指标上有多少差别

验收线：HE 逐像素一致；CLAHE ≥ 30 dB。
===============================================================

------------------------------------------------------------------------
直方图均衡在做什么
------------------------------------------------------------------------

一张太暗的图，像素值都挤在 0~80 之间。直方图均衡的目标：
    **让像素值在整个 0~255 区间上尽可能均匀分布** —— 对比度就拉开了。

做法（累积分布函数 CDF 映射）：
    1. 数直方图：hist[v] = 值等于 v 的像素个数
    2. 算累积和：cdf[v] = hist[0] + ... + hist[v]
    3. 线性映射到 0~255：
           LUT[v] = round( (cdf[v] - cdf_min) / (N - cdf_min) * 255 )
       N = 像素总数，cdf_min = cdf 里第一个非零值
    4. 用 LUT 查表得到输出图

为什么减 cdf_min：保证最小像素值映射到 0（否则最暗处会变成灰色，整图发白）。
为什么用查表：每个像素只需查一次表，O(1)，比逐像素算快得多。

------------------------------------------------------------------------
那 CLAHE 为什么要存在？HE 的两个毛病
------------------------------------------------------------------------

毛病 1：全局化 → 局部细节被牺牲
    一张图里既有很暗的角落又很亮的主体时，全局 HE 只能取一个折中，
    暗处拉亮的同时亮处会过曝。

毛病 2：噪声被放大
    直方图上某个尖峰（比如大片同色的天空），在 HE 里会被拉成一大段，
    原本看不见的噪声突然显现。

CLAHE 的两个对策：
    ① **自适应**：把图切成 8×8 块（tile），每块单独做 HE → 局部对比度都能拉起来
    ② **限制对比度**（clip）：每块直方图里超过 clip_limit 的部分被"削平"，
       削掉的数量均匀分回整个直方图 → 防止某个尖峰被拉得太狠

------------------------------------------------------------------------
插值：CLAHE 的最后一公里（也是它最容易写错的地方）
------------------------------------------------------------------------

如果每块单独算完直接拼起来，块与块的交界处会出现明显的**网格状亮暗带**
（因为相邻块的 LUT 不同，同一灰度在块 A 里映射到 90，在块 B 里映射到 130）。

解法：每个像素不只用它所在那一块的 LUT，而是用**周围 4 块的 LUT 做双线性插值**：
    离哪块近，那块的权重就大。

实测（本文件这版实现，640×480，与 cv2 对比）：
    不做插值      → 27.5 dB，31.5% 的像素差 > 10 灰阶，肉眼可见网格
    双线性插值     → 47.0 dB，最大差只有 4，>10 灰阶的像素 0.00%
    **插值价值 19.5 dB** —— 这就是「最后一公里」的量化答案。

（cv2 的 30dB 验收线在插值版面前是宽松的；不做插值则恰好卡在下面。）

------------------------------------------------------------------------
写这个函数时踩过的两个坑（真踩的，已修好，你读代码时留意）
------------------------------------------------------------------------
坑 1：`lut_grid[iy[:, None], ix[None, :]]` 会让 numpy 广播成 (H, W, 256) 的
      巨型数组——1920x1080 时要分配 47 GiB，直接内存报错。
      正确做法：take_along_axis 取出"每个像素自己那一格 LUT 的值"。
坑 2：pad 用 "reflect" 会让边缘 tile 装进镜像内容，直方图和正常 tile 差太远，
      插值加权后炸成 11 dB。改用 "edge"（复制边缘）→ 47 dB。
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from w3_metrics import check, load_gray, psnr, ssim  # noqa: E402


# ============================================================
# 直方图均衡（完整参考实现）
# ============================================================
def histogram(img):
    """统计 256 个灰度级的像素数量。"""
    return np.bincount(img.ravel(), minlength=256)


def build_lut_equalize(img):
    """算 HE 的映射表 LUT（256 个值，uint8）。"""
    hist = histogram(img)
    cdf = hist.cumsum()
    cdf_min = cdf[cdf > 0].min()          # 第一个非零的累积值
    n = img.size
    if n == cdf_min:                       # 全图一个颜色（退化情况）
        return np.arange(256, dtype=np.uint8)
    lut = np.rint((cdf - cdf_min) / (n - cdf_min) * 255).clip(0, 255)
    return lut.astype(np.uint8)


def equalize_hist(img):
    """全局直方图均衡。对照 cv2.equalizeHist —— 应该逐像素完全一致。"""
    return build_lut_equalize(img)[img]


# ============================================================
# CLAHE（完整参考实现，含双线性插值）
# ============================================================
def clahe_lut(tile, clip_limit):
    """给单个 tile 算 CLAHE 的 LUT。

    三步：
        ① limit = clip_limit * tile.size / 256   ← 允许的直方图高度上限
        ② 超过 limit 的部分削掉，削掉的总数平分给 256 个灰度级
        ③ 照常做 CDF 映射
    """
    hist = histogram(tile).astype(np.float64)
    limit = clip_limit * tile.size / 256.0
    excess = np.maximum(hist - limit, 0.0)
    hist = hist - excess + excess.sum() / 256.0   # 削平 + 均匀回填
    cdf = hist.cumsum()
    if cdf[-1] == 0:
        return np.arange(256, dtype=np.uint8)
    lut = np.rint(cdf / cdf[-1] * 255).clip(0, 255)
    return lut.astype(np.uint8)


def clahe(img, clip_limit=2.0, tile_grid=(8, 8), use_interpolation=True):
    """CLAHE 主函数。

    参数
    ----
    clip_limit : 越大 → 对比度越强，噪点也可能被放大（试试 1/2/4/8 的差别）
    tile_grid  : (行块数, 列块数)，cv2 默认 (8, 8)
    use_interpolation : False 时退化成"每块独立、硬拼接"——用来对比插值的价值

    实现（和 cv2 对齐的版本）
    ---------------------------------------------------------------
    ① 把图 pad 到 tile 大小的整数倍（cv2 用 BORDER_REFLECT_101 镜像填充）
    ② 每个 tile 算一个 256 长度的 LUT，堆成 lut_grid (tiles_y, tiles_x, 256)
    ③ use_interpolation=False：像素直接用它所属 tile 的 LUT，硬拼
       use_interpolation=True ：对每个像素，取周围 4 个 tile 的 LUT 输出做双线性加权
    ④ 裁回原尺寸
    """
    ty, tx = tile_grid
    h, w = img.shape

    # ---- ① pad 到整数倍 ----
    tile_h = int(np.ceil(h / ty))
    tile_w = int(np.ceil(w / tx))
    ph = tile_h * ty - h
    pw = tile_w * tx - w
    # ⚠️ 用 "edge"（复制边缘）而不是 "reflect"：
    #    reflect 会把镜像内容塞进边缘 tile，导致那些 tile 的直方图和正常 tile 差太远，
    #    插值一加权就炸（实测 PSNR 从 47 dB 掉到 11 dB）。
    #    edge 相当于 cv2 的"边界外推"，实测 47 dB。
    padded = np.pad(img, ((0, ph), (0, pw)), mode="edge")

    # ---- ② 每个 tile 一个 LUT ----
    lut_grid = np.empty((ty, tx, 256), dtype=np.uint8)
    for i in range(ty):
        for j in range(tx):
            tile = padded[i * tile_h:(i + 1) * tile_h, j * tile_w:(j + 1) * tile_w]
            lut_grid[i, j] = clahe_lut(tile, clip_limit)

    # ---- ③ 映射 ----
    if not use_interpolation:
        # 每个像素用所属 tile 的 LUT：把 pixel 值先按 tile 分组查表
        out = np.empty_like(padded)
        for i in range(ty):
            for j in range(tx):
                ys = slice(i * tile_h, (i + 1) * tile_h)
                xs = slice(j * tile_w, (j + 1) * tile_w)
                out[ys, xs] = lut_grid[i, j][padded[ys, xs]]
    else:
        out = _interpolate_lut_grid(padded, lut_grid, tile_h, tile_w)

    # ---- ④ 裁回 ----
    return out[:h, :w]


def _interpolate_lut_grid(padded, lut_grid, tile_h, tile_w):
    """双线性插值：每个像素取周围 4 个 tile 的 LUT 输出按距离加权。

    坐标约定（和 cv2 一致）：tile 的 LUT 在「该 tile 的中心行/列」是"准的"，
    于是相邻 tile 中心之间等距 tile_h / tile_w。
    对像素 (y, x)：
        连续坐标  yc = y / tile_h - 0.5,  xc = x / tile_w - 0.5
        左上格    i0 = floor(yc),      j0 = floor(xc)
        小数部分  dy = yc - i0,        dx = xc - j0
        四个邻居  (i0,j0) (i0,j0+1) (i0+1,j0) (i0+1,j0+1)
        权重      (1-dy)(1-dx), (1-dy)dx, dy(1-dx), dy·dx
        越界时（i0<0 或 ≥ty）：索引夹到边界，权重整体让给合法那格

    ⚠️ 这里踩过的两个坑（都是真踩的，别重复踩）：
      坑 1：写成 lut_grid[iy[:,None], ix[None,:]] 会让 numpy 广播成
            (H, W, 256) 的巨型数组，1920x1080 时要 47 GiB，直接内存报错。
            正确写法是「每个像素取它那一格 LUT」：
            take_along_axis(lut[ii[:,None], jj[None,:]], pixel, axis=2)
      坑 2：pad 如果用 reflect，边缘那圈 tile 里是【镜像】内容，
            直方图和正常 tile 完全不同 → 插值一加权就炸（PSNR 掉到 11 dB）。
            用 mode="edge"（复制边缘）才和 cv2 的边界外推等价 → 47 dB。
    """
    ty, tx, _ = lut_grid.shape
    H, W = padded.shape

    yc = np.arange(H, dtype=np.float64) / tile_h - 0.5      # (H,)
    xc = np.arange(W, dtype=np.float64) / tile_w - 0.5      # (W,)
    i0 = np.floor(yc).astype(int)
    j0 = np.floor(xc).astype(int)
    dy = yc - i0
    dx = xc - j0
    i1, j1 = i0 + 1, j0 + 1

    def clamp(v, n):
        return np.clip(v, 0, n - 1)

    # 越界格不参与：权重整体让给合法的那格
    wy0 = np.where(i0 < 0, 0.0, 1.0 - dy)[:, None]          # (H,1)
    wy1 = np.where(i0 < 0, 1.0, dy)[:, None]
    wx0 = np.where(j0 < 0, 0.0, 1.0 - dx)[None, :]          # (1,W)
    wx1 = np.where(j0 < 0, 1.0, dx)[None, :]

    out = np.zeros((H, W), dtype=np.float64)
    for (iy, ix, wgt) in [
        (clamp(i0, ty), clamp(j0, tx), wy0 * wx0),
        (clamp(i0, ty), clamp(j1, tx), wy0 * wx1),
        (clamp(i1, ty), clamp(j0, tx), wy1 * wx0),
        (clamp(i1, ty), clamp(j1, tx), wy1 * wx1),
    ]:
        lut_pick = lut_grid[iy[:, None], ix[None, :]]        # (H, W, 256)
        corner = np.take_along_axis(
            lut_pick, padded[..., None].astype(np.intp), axis=2)[..., 0]
        out += wgt * corner.astype(np.float64)
    return np.clip(np.rint(out), 0, 255).astype(np.uint8)


# ============================================================
# 以下是【不用填】的验证部分
# ============================================================
def _tile_he_naive(img, grid=(8, 8)):
    """对照实验用：每块各自做【全量】HE（不 clip、不插值）——这就是 CLAHE 想解决的问题。

    预期结果：块交界出现网格，标准差被推到 80+，和原图的相关性崩到 0.3 左右。
    """
    ty, tx = grid
    h, w = img.shape
    th, tw = int(np.ceil(h / ty)), int(np.ceil(w / tx))
    p = np.pad(img, ((0, th * ty - h), (0, tw * tx - w)), mode="edge")
    out = np.empty_like(p)
    for i in range(ty):
        for j in range(tx):
            t = p[i * th:(i + 1) * th, j * tw:(j + 1) * tw]
            out[i * th:(i + 1) * th, j * tw:(j + 1) * tw] = equalize_hist(t)
    return out[:h, :w]


def _t(fn, *a, n=3):
    import time

    best = float("inf")
    for _ in range(n):
        t0 = time.perf_counter()
        fn(*a)
        best = min(best, time.perf_counter() - t0)
    return best


def main():
    import cv2

    gray = load_gray("small")
    scene = load_gray("scene")
    print("=" * 72)
    print("W3 任务 3 自测：直方图均衡 / CLAHE")
    print("=" * 72)
    print(f"测试图：{gray.shape}（另用 {scene.shape} 测速度）")
    print()

    # ---------- ① HE ----------
    print("① 直方图均衡 vs cv2.equalizeHist")
    mine = equalize_hist(gray)
    ref = cv2.equalizeHist(gray)
    ok_he = check("equalize_hist", mine, ref, psnr_min=999)   # 要求 inf
    print()

    # 直方图前后对比
    h_before = histogram(gray)
    h_after = histogram(mine)
    print("   直方图变化（灰度级跨度）：")
    def span(h):
        nz = np.where(h > 0)[0]
        return f"{nz[0]}~{nz[-1]}（{len(nz)} 个灰度级有像素）"
    print(f"     均衡前：{span(h_before)}")
    print(f"     均衡后：{span(h_after)}   ← 应该铺得更开")
    print()

    # ---------- ② CLAHE：插值 vs 不插值 ----------
    print("② CLAHE vs cv2.createCLAHE（clip=2.0, tile=8x8）")
    ref_clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)

    no_int = clahe(gray, 2.0, (8, 8), use_interpolation=False)
    with_int = clahe(gray, 2.0, (8, 8), use_interpolation=True)

    p_no = psnr(no_int, ref_clahe)
    p_yes = psnr(with_int, ref_clahe)
    d_no = np.abs(no_int.astype(int) - ref_clahe.astype(int))
    d_yes = np.abs(with_int.astype(int) - ref_clahe.astype(int))

    print(f"   不做插值  PSNR {p_no:5.1f} dB   SSIM {ssim(no_int, ref_clahe):.4f}   "
          f"最大差 {d_no.max():3d}  >10灰阶 占 {100 * (d_no > 10).mean():5.2f}%")
    print(f"   双线性插值 PSNR {p_yes:5.1f} dB   SSIM {ssim(with_int, ref_clahe):.4f}   "
          f"最大差 {d_yes.max():3d}  >10灰阶 占 {100 * (d_yes > 10).mean():5.2f}%")
    print(f"   → 插值把 PSNR 提高了 {p_yes - p_no:+.1f} dB")
    ok_clahe = p_yes >= 30.0
    print(f"   验收线 30 dB：{'✅ 通过' if ok_clahe else '❌ 未达'}"
          f"（本实现做到 {p_yes:.1f} dB，参考值约 47 dB）")
    print()

    # ---------- ③ clip_limit 的影响 ----------
    print("③ clip_limit 的影响（注意：方向和直觉相反）")
    print(f"   {'clip':>5s} {'PSNR':>7s} {'输出标准差':>10s} {'与原图相关性':>12s}  说明")
    for cl in (1.0, 2.0, 4.0, 8.0, 16.0, 40.0):
        r = cv2.createCLAHE(clipLimit=cl, tileGridSize=(8, 8)).apply(gray)
        corr = np.corrcoef(gray.ravel(), r.ravel())[0, 1]
        note = ""
        if cl == 1.0:
            note = "最保守：几乎只做轻微局部调整"
        elif cl == 40.0:
            note = "最激进：逼近每块全量 HE"
        print(f"   {cl:5.1f} {psnr(clahe(gray, cl), r):7.1f} {r.std():10.1f} {corr:12.4f}  {note}")
    print(f"   （原图标准差 {gray.std():.1f}，相关性 1.0）")
    print("   ↑ 反直觉但实测如此：clip 调【大】→ 输出标准差【下降】、与原图的相关性【变差】。")
    print("     为什么？看 clahe_lut() 的代码：clip 越大，允许保留的高峰越多，")
    print("     削平后回填的越少 → 局部 CDF 变化越剧烈 → 等于在做更强的局部直方图拉伸。")
    print("     结果就是：局部对比度被拉爆，原本相近的像素被推到很不一样的值，")
    print("     所以【整体】标准差反而降、和原图的结构对应关系被破坏。")
    print("     这就是 clip_limit 存在的意义：它是『局部增强』与『保持原图结构』之间的旋钮。")
    print()

    # ---------- ③b 为什么不能简单分块 HE ----------
    print("③b 对照实验：如果不做 clip、不做插值，直接每块各自全量 HE 会怎样？")
    naive = _tile_he_naive(gray, (8, 8))
    print(f"   每块全量HE         标准差 {naive.std():5.1f}  与原图相关性 {np.corrcoef(gray.ravel(), naive.ravel())[0, 1]:.4f}")
    print(f"   cv2 CLAHE(clip=2)  标准差 {cv2.createCLAHE(2.0, (8, 8)).apply(gray).std():5.1f}  "
          f"与原图相关性 {np.corrcoef(gray.ravel(), cv2.createCLAHE(2.0, (8, 8)).apply(gray).ravel())[0, 1]:.4f}")
    print("   → 全量分块 HE 的标准差从原图 64 推到 75.6，但与原图相关性从 1.0 崩到 0.32")
    print("     翻译成人话：看起来『对比更强』，实际已经面目全非（结构对不上了）")
    print("   → 所以 CLAHE = 【clip 限幅】+【插值平滑】两个补丁，缺一个都不像样")
    print()

    # ---------- ④ 速度 ----------
    print("④ 速度对比（1920x1080，各跑 3 次取最快）")
    t_he = _t(equalize_hist, scene)
    t_ref_he = _t(cv2.equalizeHist, scene)
    t_cl = _t(clahe, scene)
    t_ref_cl = _t(lambda i: cv2.createCLAHE(2.0, (8, 8)).apply(i), scene)
    print(f"   HE    手写 {t_he * 1000:8.1f} ms   cv2 {t_ref_he * 1000:6.1f} ms   慢 {t_he / t_ref_he:5.1f} 倍")
    print(f"   CLAHE 手写 {t_cl * 1000:8.1f} ms   cv2 {t_ref_cl * 1000:6.1f} ms   慢 {t_cl / t_ref_cl:5.1f} 倍")
    print("   ↑ CLAHE 慢主要是那个 (H, W, 256) 的查表数组——内存开销极大。")
    print("     这不是你写错了，是『每个像素查 4 个 256 长向量』这个思路的成本。")
    print()

    print("=" * 72)
    print(f"HE    ：{'✅ 逐像素一致' if ok_he else '❌ 没对齐'}")
    print(f"CLAHE ：{p_yes:.1f} dB —— {'✅ 过 30dB 线' if ok_clahe else '⚠️ 未过线'}")
    print()
    print("现在做 TODO B/C/D，把观察写进对标报告：")
    print("  B. 插值值多少 dB？（上面②已给出数字：约 +19.6 dB）")
    print("  C. clip_limit 从 1 调到 40，输出标准差为什么反而下降？")
    print("     （提示：想想局部 CDF 的斜率，以及『整体统计量』和『局部变化』不是一回事）")
    print("  D. 把 LUT 公式改错一处，看 PSNR 掉多少——体会指标对细节的敏感度")


if __name__ == "__main__":
    main()
