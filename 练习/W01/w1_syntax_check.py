#!/usr/bin/env python3
"""W1 语法查漏补缺：5 个知识点，10 分钟做实操。

用法（在 ~/cv-kit 下）：
    python 练习/W01/w1_syntax_check.py       # 一次跑完，看输出
    python -i 练习/W01/w1_syntax_check.py    # 跑完停在交互模式，可以自己接着玩变量

设计原则：每个知识点都给你"能验证的结果"，对不上就是没懂，别往下走。
"""
print("=" * 60)
print("① 列表 list：一串有顺序的东西，下标从 0 开始")
print("=" * 60)
names = ["small_640x480.jpg", "rgba_800x600.png", "scene_1920x1080.jpg"]
print(f"  整个列表      : {names}")
print(f"  names[0]      : {names[0]}      ← 第 1 个（不是第 0 个！）")
print(f"  names[-1]     : {names[-1]}     ← 最后一个（负数从尾巴数）")
print(f"  names[1:3]    : {names[1:3]}    ← 切片：从 1 到 3，但不含 3")
print(f"  长度 len()    : {len(names)}")
names.append("broken_truncated.jpg")          # 往尾巴上加一个
print(f"  append 之后   : {names}")
names.remove("broken_truncated.jpg")         # 按值删掉
print(f"  remove 之后   : {names}")
print(f"  排序 sorted() : {sorted(names)}")
print()

print("=" * 60)
print("② 字典 dict：一对一对存东西（键 → 值），不是按位置取")
print("=" * 60)
timing = {"循环版": 0.05, "向量化版": 0.001}    # 花括号，冒号分隔键和值
print(f"  整个字典          : {timing}")
print(f"  timing['循环版']  : {timing['循环版']}    ← 用【键】取【值】，不是下标！")
timing["numpy版"] = 0.0008                     # 直接加一对新的
print(f"  加一对之后        : {timing}")
print(f"  所有键            : {list(timing.keys())}")
print(f"  加速比            : {timing['循环版'] / timing['numpy版']:.1f} 倍")
print("  ↑ W2 记录实验结果就长这样：{'配置': 耗时}")
print()

print("=" * 60)
print("③ 字符串方法：处理文件名、路径天天用")
print("=" * 60)
s = "  small_640x480.JPG  "
print(f"  原字符串      : {s!r}                     ← !r 显示引号和空格")
print(f"  .strip()      : {s.strip()!r}               ← 去掉两头的空白")
print(f"  .lower()      : {s.strip().lower()!r}       ← 转小写（链式调用）")
print(f"  .upper()      : {s.strip().upper()!r}")
print(f"  .split('_')   : {'small_640x480.JPG'.split('_')}      ← 按下划线切成几块")
print(f"  .startswith() : {'small_640x480.JPG'.startswith('small')}      ← 是不是以...开头")
print(f"  .replace()    : {'a/b/c'.replace('/', '-')}")
print("  ↑ 你代码里的 p.suffix.lower() 就是这类方法的组合")
print()

print("=" * 60)
print("④ .append()：循环里收集结果的标准写法")
print("=" * 60)
results = []                                   # 先准备一个空列表
for name in ["a.jpg", "b.png", "c.txt"]:
    if name.endswith(".txt"):
        continue                               # 跳过（你已经在 CLI 里用过了）
    results.append(name.upper())               # 收集
print(f"  results = {results}")
print(f"  个数    = {len(results)}")
print("  ↑ 模式：空列表 → 循环里 append → 循环后统计。W2 记录每组耗时都用这个")
print()

print("=" * 60)
print("⑤ ★ W2 最关键的桥：二维数据怎么取")
print("=" * 60)
# 纯 Python：列表是一维的，要表示"3 行 4 列"，得嵌套（列表里装列表）
grid = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
]
print("  纯 Python 的二维表格（列表套列表）:")
for row in grid:
    print(f"      {row}")
print(f"  grid[1]        = {grid[1]}          ← 先取【第 1 行】")
print(f"  grid[1][2]     = {grid[1][2]}             ← 再取这行的【第 2 个】")
print("  ⚠️ 注意：必须写两层括号 grid[行][列]，不能写 grid[1, 2]（那是元组下标，会报错）")
print()
print("  NumPy 的数组（W2 的主角）长这样：")
print("      arr[1, 2]        ← 一个括号，逗号分隔：arr[行, 列]")
print("      arr[:, 0]        ← 所有行、第 0 列（一整列）")
print("      arr[0, :]        ← 第 0 行、所有列（一整行）")
print()
print("  ★ 对照记牢（W2 的两种取法）:")
print("      纯 Python : grid[y][x]      （先 y 再 x）")
print("      NumPy     : arr[y, x]       （一个括号，先 y 再 x）")
print("      PIL 像素  : px[x, y]        （你已用过！注意 PIL 是【x 在前、y 在后】）")
print()
print("=" * 60)
print("全部跑完。要自己接着玩，用: python -i 练习/W01/w1_syntax_check.py")
print("=" * 60)
