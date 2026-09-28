#!/usr/bin/env python3
"""W2 任务 1 小测：11 道预测题。

用法:
    cd ~/cv-kit
    python 练习/W02/w2_numpy_quiz.py
"""
import numpy as np

M = np.array([[1, 2, 3], [4, 5, 6]])
ARR3 = np.array([[[100, 150, 200], [10, 20, 30]],
                 [[40, 50, 60], [70, 80, 90]]])

QUIZ = [
    (1, "[1, 2, 3] * 2                        # Python 列表",
        lambda: [1, 2, 3] * 2),
    (2, "np.array([1, 2, 3]) * 2             # NumPy 数组",
        lambda: np.array([1, 2, 3]) * 2),
    (3, "np.array([1, 2, 3]) + np.array([10, 20, 30])",
        lambda: np.array([1, 2, 3]) + np.array([10, 20, 30])),
    (4, "np.array([[1, 2, 3], [4, 5, 6]]).shape",
        lambda: M.shape),
    (5, "m = np.array([[1,2,3],[4,5,6]])\n      m[1, 2]                      # 取一个元素",
        lambda: M[1, 2]),
    (6, "m = np.array([[1,2,3],[4,5,6]])\n      m[:, 0]                      # 一整列",
        lambda: M[:, 0]),
    (7, "m = np.array([[1,2,3],[4,5,6]])\n      m.sum(axis=0)                # axis=0",
        lambda: M.sum(axis=0)),
    (8, "m = np.array([[1,2,3],[4,5,6]])\n      m.sum(axis=1)                # axis=1",
        lambda: M.sum(axis=1)),
    (9, "np.array([250.7, 3.9]).astype(np.uint8)   # 类型转换",
        lambda: np.array([250.7, 3.9]).astype(np.uint8)),
    (10, "arr = np.zeros((480, 640, 3), dtype=np.uint8)\n      arr.shape                    # ?",
        lambda: np.zeros((480, 640, 3), dtype=np.uint8).shape),
    (11, "arr 是三维数组, arr.shape = (2, 2, 3)   # 两小问一起答\n"
         "      arr[0, 1]       -> ?\n"
         "      arr[:, :, 1]    -> ?",
        lambda: (ARR3[0, 1], ARR3[:, :, 1])),
]

print("=" * 66)
print("W2 任务 1 小测：11 道预测题")
print("=" * 66)
print("""
玩法：每题先在心里（或纸上）写下答案，再按回车看真实结果。
      最后算总分。
""")
input("准备好了就按回车开始…")

score = 0
for no, question, answer_fn in QUIZ:
    print()
    print("-" * 66)
    print(f"第 {no} 题:  {question}")
    print("-" * 66)
    input("  -> 先写下你的答案，然后按回车看结果…")
    try:
        result = answer_fn()
    except Exception as e:
        result = f"[报错] {type(e).__name__}: {e}"
    print(f"  答案: {result}")
    mark = input("  答对了吗? (y/n) -> ").strip().lower()
    if mark == "y":
        score += 1

print()
print("=" * 66)
print(f"总分: {score} / 11")
if score >= 9:
    print("✅ 过关！可以进任务 2（把图片读成数组）")
else:
    print("⚠️  建议重看 w2_numpy_intro.py 的对应部分，再来一遍")
print("=" * 66)
print("""
重点提示

  第 1 题 vs 第 2 题：列表乘 2 = "重复两遍"；数组乘 2 = "每个元素乘 2"。
                      这是 NumPy 能取消循环的根本原因。

  第 7 题 vs 第 8 题：axis=0 把行压扁（结果个数 = 列数）
                      axis=1 把列压扁（结果个数 = 行数）

  第 9 题：astype 是【截断】不是四舍五入：250.7 -> 250，3.9 -> 3
           （和 W1 循环版的 int() 行为一致，正好可以对拍）

  第 11 题：三维数组 = (高, 宽, 通道)
            arr[0, 1]     -> 第 0 个"高"、第 1 个"宽"位置上的【一个像素】(3 个数)
            arr[:, :, 1]  -> 所有行、所有列、第 1 通道 -> 【整张绿色通道图】
            这题会做的意义：任务 3 的灰度公式就是靠 arr[:, :, 0/1/2] 取三个通道
""")
