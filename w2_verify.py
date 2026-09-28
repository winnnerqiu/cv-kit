#!/usr/bin/env python3
"""W2 任务 3 验证：向量化版 vs 循环版，严格对拍 + 性能对比。

用法（必须在仓库根目录跑）:
    cd ~/cv-kit
    python w2_verify.py

会做三件事：
  ① 逐像素比较两版结果（必须完全一致）
  ② 检查输出类型（uint8、二维）
  ③ 测 1920x1080 大图的耗时，算加速比

说明：这个文件留在根目录，因为它要导入 grayscale_cli 和 练习/W02/w2_to_gray_numpy。
"""
import importlib.util
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent


def load_module(path, name):
    """按文件路径导入模块（不依赖 sys.path，也不怕目录改名字）。"""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# 循环版（W1 的正式工具）
cli = load_module(ROOT / "grayscale_cli.py", "cvkit_cli")
to_gray = cli.to_gray

# 向量化版（W2 的练习文件）
np_path = ROOT / "练习" / "W02" / "w2_to_gray_numpy.py"
if not np_path.exists():
    print(f"❌ 找不到 {np_path}")
    print("   确认文件在：~/cv-kit/练习/W02/w2_to_gray_numpy.py")
    sys.exit(1)
w2 = load_module(np_path, "cvkit_w2")
to_gray_numpy = w2.to_gray_numpy


def bench(fn, img, times=3):
    """跑 times 次取最快（排除系统抖动）。"""
    best = float("inf")
    for _ in range(times):
        t0 = time.perf_counter()
        fn(img)
        best = min(best, time.perf_counter() - t0)
    return best


def main():
    print("=" * 62)
    print("① 逐像素对拍（640x480）")
    print("=" * 62)

    img = Image.open("testdata/small_640x480.jpg")
    loop_result = np.array(to_gray(img))        # 循环版 → 数组
    np_result = to_gray_numpy(img)              # 向量化版（已经是数组）

    print(f"  循环版  : {loop_result.shape}  {loop_result.dtype}")
    print(f"  向量化版: {np_result.shape}  {np_result.dtype}")

    if np_result.dtype != np.uint8:
        print(f"  ❌ dtype 应该是 uint8，实际是 {np_result.dtype}")
        return
    if np_result.ndim != 2:
        print(f"  ❌ 应该是二维（高, 宽），实际是 {np_result.ndim} 维 {np_result.shape}")
        return

    if np.array_equal(loop_result, np_result):
        print("  ✅ 完全一致（逐像素）—— 这才是真的写对了")
    else:
        diff = np.abs(loop_result.astype(int) - np_result.astype(int))
        n_diff = int((diff != 0).sum())
        print(f"  ❌ 有 {n_diff} 个像素不一致（占 {n_diff/diff.size*100:.2f}%）")
        print(f"     最大差值 = {diff.max()}")
        ys, xs = np.where(diff != 0)
        y, x = int(ys[0]), int(xs[0])
        print(f"     第一个不同的像素 ({y},{x}): 循环版={loop_result[y,x]}  向量化版={np_result[y,x]}")
        print("     → 常见原因：忘了 astype(float)（uint8 溢出）、通道取错、忘了 clip")

    print()
    print("=" * 62)
    print("② 大图也对拍一遍")
    print("=" * 62)
    big = Image.open("testdata/scene_1920x1080.jpg")
    a = np.array(to_gray(big))
    b = to_gray_numpy(big)
    print(f"  scene_1920x1080.jpg  {'✅ 一致' if np.array_equal(a, b) else '❌ 不一致'}")

    print()
    print("=" * 62)
    print("③ 性能对比（1920x1080，各跑 3 次取最快）")
    print("=" * 62)
    t_loop = bench(to_gray, big)
    t_np = bench(to_gray_numpy, big)
    print(f"  循环版  : {t_loop*1000:8.1f} 毫秒")
    print(f"  向量化版: {t_np*1000:8.1f} 毫秒")
    print(f"  加速比  : {t_loop/t_np:8.1f} 倍")
    print()
    print("  ★ 把这三个数如实抄进 README 的「性能对比」一节，别修饰。")


if __name__ == "__main__":
    main()
