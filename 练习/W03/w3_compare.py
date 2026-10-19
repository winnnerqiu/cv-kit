#!/usr/bin/env python3
"""W3 任务 4：一键对标 —— 把你手写的算子与 OpenCV 全面比一遍，出报告。

用法（仓库根目录）：
    python 练习/W03/w3_compare.py

它会：
    ① 跑遍所有算子，算 PSNR / SSIM / 最大差值 / 不一致像素比例
    ② 每张图存一张三联图：OpenCV 原版 | 你写的 | 差异热力图（放大 4 倍）
    ③ 打印验收表（过/不过），并把 Markdown 报告写到 out/w3/对标结果.md
    ④ 顺带测速度，算「比 cv2 慢几倍」

这个文件【不用填】。它的作用是：把「我写完了」变成「我有数据证明写对了」。
W3 的核心产出——对标报告——就是从这里的输出整理出来的。
"""
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from w3_metrics import load_gray, psnr, ssim  # noqa: E402

OUT = ROOT / "out" / "w3"


# ----------------------------------------------------------------------
# 待对标的算子清单：(名字, 你的实现, OpenCV 参照, 说明)
# ----------------------------------------------------------------------
def build_cases():
    """动态构造用例：某个算子还没实现时给出提示而不是直接崩。"""
    import cv2

    from w3_conv import conv2d_im2col, conv2d_sliding
    from w3_filters import gaussian_blur, mean_blur, median_blur
    from w3_histogram import clahe, equalize_hist

    sobel = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
    mean5 = np.ones((5, 5), dtype=np.float64) / 25.0
    g1 = cv2.getGaussianKernel(3, 0)
    g3 = g1 @ g1.T

    cases = [
        ("卷积 Sobel_X",
         lambda im: conv2d_sliding(im, sobel),
         lambda im: cv2.filter2D(im, cv2.CV_8U, sobel, borderType=cv2.BORDER_REFLECT_101),
         "PSNR≥45", "边缘检测核，检验任意核的通用性"),

        ("卷积 5x5 均值核",
         lambda im: conv2d_sliding(im, mean5),
         lambda im: cv2.filter2D(im, cv2.CV_8U, mean5, borderType=cv2.BORDER_REFLECT_101),
         "PSNR≥45", "模糊核，检验核归一化"),

        ("卷积 3x3 高斯核",
         lambda im: conv2d_sliding(im, g3),
         lambda im: cv2.filter2D(im, cv2.CV_8U, g3, borderType=cv2.BORDER_REFLECT_101),
         "PSNR≥45", "平滑核"),

        ("卷积 im2col k=5",
         lambda im: conv2d_im2col(im, mean5),
         lambda im: cv2.filter2D(im, cv2.CV_8U, mean5, borderType=cv2.BORDER_REFLECT_101),
         "PSNR≥45", "im2col + matmul 应与滑窗法完全等价"),

        ("均值滤波 k=5",
         lambda im: mean_blur(im, 5),
         lambda im: cv2.blur(im, (5, 5)),
         "PSNR≥50", "边界：reflect101"),

        ("高斯滤波 k=5",
         lambda im: gaussian_blur(im, 5),
         lambda im: cv2.GaussianBlur(im, (5, 5), 0),
         "PSNR≥55", "检验 sigma↔ksize 的自动公式"),

        ("中值滤波 k=3",
         lambda im: median_blur(im, 3),
         lambda im: cv2.medianBlur(im, 3),
         "PSNR≥50", "边界：cv2 用 REPLICATE"),

        ("直方图均衡",
         lambda im: equalize_hist(im),
         lambda im: cv2.equalizeHist(im),
         "逐像素一致", "基础版 CDF 映射"),

        ("CLAHE clip=2 tile=8x8",
         lambda im: clahe(im, 2.0, (8, 8), use_interpolation=True),
         lambda im: cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(im),
         "PSNR≥30", "完整版：clip 限幅 + 双线性插值"),

        ("CLAHE 无插值（对照）",
         lambda im: clahe(im, 2.0, (8, 8), use_interpolation=False),
         lambda im: cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(im),
         "仅参考", "故意不插值——用来看插值值多少 dB"),
    ]
    return cases


MIN_PSNR = {"PSNR≥45": 45.0, "PSNR≥50": 50.0, "PSNR≥55": 55.0, "PSNR≥30": 30.0}


# ----------------------------------------------------------------------
# 差异可视化
# ----------------------------------------------------------------------
def stack_compare(ref, mine, name, scale=4):
    """三联图：OpenCV | 手写 | 差异热力图（差值放大 scale 倍看细节）。"""
    import cv2

    diff = np.abs(mine.astype(np.int16) - ref.astype(np.int16))
    amp = np.clip(diff.astype(np.float64) * scale, 0, 255).astype(np.uint8)
    heat = cv2.applyColorMap(amp, cv2.COLORMAP_JET)

    panels = [
        ("OpenCV", cv2.cvtColor(ref, cv2.COLOR_GRAY2BGR)),
        ("手写", cv2.cvtColor(mine, cv2.COLOR_GRAY2BGR)),
        (f"|diff| x{scale}", heat),
    ]
    h, w = ref.shape
    canvas = np.zeros((h + 28, w * 3, 3), dtype=np.uint8)
    for i, (label, panel) in enumerate(panels):
        canvas[28:, i * w:(i + 1) * w] = panel
        cv2.putText(canvas, label, (i * w + 8, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    return canvas


# ----------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------
def main():
    import cv2

    img = load_gray("small")
    big = load_gray("scene")
    OUT.mkdir(parents=True, exist_ok=True)

    print("=" * 78)
    print("W3 对标：手写算子 vs OpenCV")
    print("=" * 78)
    print(f"测试图：{img.shape}（速度用 {big.shape}）")
    print(f"产物目录：{OUT}")
    print()

    rows = []
    skipped = []
    header = f"{'算子':22s} {'PSNR':>7s} {'SSIM':>7s} {'最大差':>6s} {'不一致%':>8s} {'判定':>12s}"

    print(header)
    print("-" * 78)
    for name, mine_fn, ref_fn, rule, note in build_cases():
        try:
            ref = ref_fn(img)
            mine = mine_fn(img)
        except NotImplementedError as e:
            skipped.append((name, str(e)))
            print(f"{name:22s} {'—':>7s} {'—':>7s} {'—':>6s} {'—':>8s} {'⏸ 未实现':>12s}")
            continue
        except Exception as e:                                    # noqa: BLE001
            skipped.append((name, f"{type(e).__name__}: {e}"))
            print(f"{name:22s} {'—':>7s} {'—':>7s} {'—':>6s} {'—':>8s} {'💥 报错':>12s}")
            continue

        if mine.shape != ref.shape:
            print(f"{name:22s} 形状不符 {mine.shape} vs {ref.shape}")
            skipped.append((name, f"形状不符 {mine.shape} vs {ref.shape}"))
            continue

        d = np.abs(mine.astype(int) - ref.astype(int))
        p, s = psnr(mine, ref), ssim(mine, ref)
        thr = MIN_PSNR.get(rule)
        if thr is None:
            ok = True
            verdict = "✅ 通过" if p == float("inf") else "参考"
        else:
            ok = p >= thr
            verdict = "✅ 通过" if ok else "❌ 未过"
        print(f"{name:22s} {p:7.1f} {s:7.4f} {d.max():6d} {100 * (d != 0).mean():7.2f}% "
              f"{verdict:>12s}")

        # 存三联图
        fname = name.replace(" ", "_").replace("=", "").replace("(", "").replace(")", "")
        cv2.imwrite(str(OUT / f"{fname}.png"), stack_compare(ref, mine, name))

        rows.append({
            "name": name, "psnr": p, "ssim": s, "maxdiff": int(d.max()),
            "pct": float(100 * (d != 0).mean()), "rule": rule,
            "ok": bool(ok), "note": note,
            "file": f"{fname}.png",
        })

    print("-" * 78)
    print()

    # ---------- 速度 ----------
    print("速度对比（1920x1080，各跑 3 次取最快）")
    print("-" * 78)
    print(f"{'算子':22s} {'手写 ms':>10s} {'cv2 ms':>9s} {'慢多少倍':>10s}")
    got_any = False
    for name, mine_fn, ref_fn, rule, note in build_cases():
        try:
            def best(fn, n=3):
                b = float("inf")
                for _ in range(n):
                    t0 = time.perf_counter()
                    fn(big)
                    b = min(b, time.perf_counter() - t0)
                return b

            t_mine = best(mine_fn)
            t_ref = best(ref_fn)
            got_any = True
            print(f"{name:22s} {t_mine * 1000:10.1f} {t_ref * 1000:9.1f} "
                  f"{t_mine / t_ref:9.1f}x")
            for r in rows:
                if r["name"] == name:
                    r["t_mine_ms"] = t_mine * 1000
                    r["t_ref_ms"] = t_ref * 1000
        except NotImplementedError:
            continue
        except Exception:                                          # noqa: BLE001
            continue
    if not got_any:
        print("  （还没有可测的算子——先把 TODO 填完）")
    print()

    # ---------- 报告 ----------
    ok_count = sum(1 for r in rows if r["ok"])
    total = len(rows)
    md = [
        "# W3 对标报告",
        "",
        f"> 自动生成：`python 练习/W03/w3_compare.py`",
        f"> 测试图：{img.shape}（速度用 {big.shape}）｜环境：WSL2 / Python 3.11 / opencv {cv2.__version__}",
        "",
        "## 一、精度对标",
        "",
        "| 算子 | PSNR (dB) | SSIM | 最大差 | 不一致像素 | 验收线 | 结果 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        p_txt = "inf" if r["psnr"] == float("inf") else f"{r['psnr']:.1f}"
        md.append(f"| {r['name']} | {p_txt} | {r['ssim']:.4f} | {r['maxdiff']} | "
                  f"{r['pct']:.2f}% | {r['rule']} | {'✅' if r['ok'] else '❌'} |")

    md += [
        "",
        f"**通过 {ok_count} / {total} 项**",
        "",
        "## 二、速度对标",
        "",
        "| 算子 | 手写 (ms) | OpenCV (ms) | 慢多少倍 |",
        "| --- | --- | --- | --- |",
    ]
    for r in rows:
        if "t_mine_ms" in r:
            md.append(f"| {r['name']} | {r['t_mine_ms']:.1f} | {r['t_ref_ms']:.1f} | "
                      f"{r['t_mine_ms'] / r['t_ref_ms']:.1f}× |")

    md += ["", "## 三、差异可视化", ""]
    for r in rows:
        md.append(f"### {r['name']}")
        md.append("")
        md.append(f"`{r['file']}`（左=OpenCV，中=手写，右=差异放大 4 倍）")
        md.append("")

    md += [
        "## 四、差异原因分析（这里才是重点，请你亲自写）",
        "",
        "> 报告的价值不在数字，在『为什么会有这些差异』。下面每条都对应一类常见原因，",
        "> 用你的实测结果填空，并说明在哪个算子上体现得最明显。",
        "",
        "| 差异来源 | 在哪个算子上体现 | 实测现象 | 为什么 |",
        "| --- | --- | --- | --- |",
        "| 边界处理方式不同 | | | reflect101 / reflect / replicate / zero 的差别 |",
        "| 浮点精度与取整 | | | float32 vs float64、rint vs 截断 |",
        "| 算法细节差异 | | | 例如 CLAHE 是否插值、cut 上限的定义 |",
        "| 定点/查表优化 | | | OpenCV 内部用定点数、查表，与逐像素浮点计算不同 |",
        "",
        "## 五、结论",
        "",
        "- 哪些算子做到了逐像素一致？为什么能一致（提示：纯整数运算/无近似）",
        "- 哪些算子只能接近？差异出现在图像的什么位置（提示：看差异热力图亮在哪）",
        "- 从这份表里，你对『手写实现 vs 高度优化库』这件事有什么新认识？",
        "",
    ]
    report = OUT / "对标结果.md"
    report.write_text("\n".join(md), encoding="utf-8")

    print("=" * 78)
    print(f"验收：{ok_count} / {total} 项通过")
    if skipped:
        print(f"待完成（{len(skipped)} 项）：")
        for name, why in skipped:
            print(f"  · {name}：{why}")
    print()
    print(f"三联对比图 → {OUT.as_posix()}/*.png")
    print(f"对标报告   → {report.as_posix()}")
    print()
    print("下一步：打开那些 .png 看差异亮在哪里，然后把『差异原因分析』那节填完，")
    print("       就得到 W3 的核心产出——有数据、有归因的对标报告。")


if __name__ == "__main__":
    main()
