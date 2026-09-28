# W1 Python 基础手册（零基础版）

> 配套代码：`~/cv-kit/try_pillow.py`、`~/cv-kit/grayscale_cli.py`
> 用法：**不用背**。写代码卡住时回来查对应小节；每节的「动手验证」都跑一遍。

---

# 第 0 章：一个 .py 文件是怎么跑起来的

## 0.1 `.py` 文件是什么

就是一个纯文本文件，里面写着 Python 语言的指令。它**不是**软件、不需要编译、不需要双击。

## 0.2 怎么跑它

在终端里：

```bash
python 文件名.py
```

这一行的意思是：**"启动 Python 这个程序，让它去读 `文件名.py` 里的指令，从上到下一条条执行。"**

比如 `python try_pillow.py` 就是：启动 Python → 打开 `try_pillow.py` → 从第一行开始执行到最后一行。

## 0.3 执行顺序：从上到下，一行一行

```python
print("第一行")     # 先执行这条
print("第二行")     # 再执行这条
```

只要有一条报错，**后面的全部不执行**。这就是为什么有时候你的程序"只打印了一半就停了"。

## 0.4 你之前踩的坑（记住这个）

**文件是空的，Python 会"成功运行"然后什么都不打印。**

它没坏，它只是没活干。所以看到"终端没反应"，第一反应是：

```bash
cat 文件名.py      # 看看文件里到底有没有东西
```

## 0.5 交互模式 vs 脚本模式

| | 交互模式 | 脚本模式 |
| --- | --- | --- |
| 怎么进 | 终端敲 `python` 回车 | 终端敲 `python 文件.py` |
| 长什么样 | 提示符变成 `>>>` | 直接出结果 |
| 变量能留吗 | **能**，一直留着 | **不能**，跑完就没了 |
| 用途 | 试验、查东西 | 干正事 |

**交互模式是你最好的老师**。想试一个函数干什么，敲 `python` 进去试，试完 `exit()` 出来。

```python
>>> 1 + 1              # 敲进去回车，它立刻告诉你
2
>>> exit()             # 退出
```

---

# 第 1 章：import —— "这个东西从哪来"

## 1.1 为什么要 import

Python 本身只带了**基础功能**（加减乘除、循环、打印）。像"读图片"这种专业功能，打包在**别人写好的工具箱**里。你要用之前，得**先把工具箱拿出来**。

```python
from PIL import Image
```

**逐字读一遍**：

| 词 | 意思 |
| --- | --- |
| `from` | 从……里面 |
| `PIL` | 一个工具箱的名字（Python Imaging Library，处理图片的） |
| `import` | 拿过来 |
| `Image` | 工具箱里的**一件具体工具**（用来打开、创建图片的） |

连起来：**"从 PIL 这个工具箱里，把 Image 这件工具拿出来，放在手边。"**

## 1.2 不 import 会怎样（你踩过）

```python
im = Image.open("testdata/small_640x480.jpg")
# NameError: name 'Image' is not defined
```

翻译：**"Image 是谁？我不认识这个名字。"**

Python 不认识它，因为你没告诉它这个名字从哪来。

## 1.3 三条铁律

1. `import` 要写在**用它的代码之前**（习惯上写在文件最开头）。
2. 一个文件**只需要 import 一次**，但每次新建文件都要重写。
3. **`import` 之后的名字才存在**；不 import 就永远 `NameError`。

## 1.4 常见变形（认识就行，暂时不用）

```python
import os                      # 把整个工具箱拿来，用的时候写 os.path.join(...)
from PIL import Image          # 只拿一件，用的时候直接写 Image.open(...)
import numpy as np             # 拿整个箱子，但起个别名 np，用的时候写 np.array(...)
```

## 🔬 动手验证

```bash
python -c "import PIL; print(PIL.__version__)"
python -c "from PIL import Image; print('拿到 Image 了')"
```

---

# 第 2 章：变量 —— "起个名字，把东西存起来"

## 2.1 赋值：`=` 是"存进去"，不是"等于"

```python
x = 5
```

读法是：**"把 5 存进名叫 x 的盒子。"**

⚠️ **`=` 是赋值，不是数学的"等于"**。数学里 `x = x + 1` 是不可能的；Python 里它完全合法，意思是"把 x 现在的值加 1，再存回 x"。

```python
x = 5
x = x + 1        # 现在 x 是 6
```

## 2.2 变量名怎么起

```python
img = ...        # ✅ 好
Img = ...        # ⚠️ 能跑，但违反了"变量名小写"的惯例
1img = ...       # ❌ 报错：数字不能开头
my-img = ...     # ❌ 报错：横杠在 Python 里是减号
my_img = ...     # ✅ 用下划线连接（Python 的风格）
```

**规则**：字母/数字/下划线组成，**不能数字开头**，不能用 Python 保留词（`for`、`if`、`class`…）。

**好名字 > 短名字**。你写的 `img` 就比 `im` 好，因为半年后你还看得懂。

## 2.3 变量的"值"和"类型"

```python
n = 5              # 整数 int
f = 3.14           # 小数 float
s = "hello"        # 文本 str（引号包起来）
b = True           # 布尔 bool（真/假）
t = (640, 480)     # 元组 tuple（一串固定的值，括号包起来）
```

用 `type()` 查它在 Python 眼里是什么：

```python
>>> x = 5
>>> type(x)
<class 'int'>
>>> type((640, 480))
<class 'tuple'>
```

## 2.4 用变量：写名字就是取它的值

```python
img = Image.open("testdata/small_640x480.jpg")
print(img.size)       # 这里写 img，等于取出刚才那张图
```

## 2.5 一行同时存多个（元组解包）

```python
w, h = img.size
```

因为 `img.size` 是**两个数装在一起的元组** `(640, 480)`，左边写两个名字，Python 就自动**按位置一个一个拆开**：

| 位置 | 拆给谁 | 值 |
| --- | --- | --- |
| 第 1 个 | `w` | 640 |
| 第 2 个 | `h` | 480 |

**为什么要这么做？** 因为这样代码能适应任意尺寸的图片。写死 `640` 的话，换张图就废了。

**拆的数量必须对上**，否则报错：

```python
w, h = (640, 480)      # ✅ 2 对 2
w = (640, 480)         # ⚠️ 也行，但 w 变成了整个元组，不是数字
w, h, c = (640, 480)   # ❌ ValueError: not enough values to unpack
```

## 2.6 变量的生命周期（重要！）

```bash
python -c "x = 5; print(x)"      # ✅ 同一条命令里，没问题
python -c "print(x)"             # ❌ NameError —— x 不存在了！
```

**每跑一次 `python`，都是一个全新的、用完就扔的世界。** 上一条命令里的变量，下一条命令里**不存在**。

这就是为什么我们最后要写**脚本文件**：把一整串操作放进一个文件里，一次跑完，变量从头到尾都在。

## 🔬 动手验证

```bash
python
```
```python
>>> img_size = (640, 480)
>>> w, h = img_size
>>> w
640
>>> type(img_size)
<class 'tuple'>
>>> exit()
```

---

# 第 3 章：print 和函数调用 —— "括号是暗号"

## 3.1 函数：别人写好的"机器"

**函数**就是一台机器：**给它料（参数），它给你产出（返回值）**。

```python
len("hello")        # len 是机器，给它 "hello"，它返回 5
```

## 3.2 调用的写法：名字 + 括号

```python
print("hi")         # 调用 print，料是 "hi"
img.size            # ⚠️ 这个没有括号 —— 它不是调用，是"读取属性"
img.load()          # 有括号 —— 这是在调用 load()
```

**有没有括号，是完全不同的两件事**：

| 写法 | 意思 |
| --- | --- |
| `img.size` | 读取 img 的 size 属性（尺寸） |
| `img.load()` | 调用 img 的 load 方法（去读像素） |
| `img.save("x.png")` | 调用 save 方法，料是文件路径 |

> 记忆法：**括号 = "动手做"**；没有括号 = "看一眼，拿个东西"。

## 3.3 `print()` 的三个用法

```python
print("hello")                              # ① 打印一个东西
print("size =", 640)                        # ② 打印多个东西，用逗号隔开
print("size", "=", "640")                   # ③ 多少个都行
```

**逗号的作用**：把几个东西**依次打印出来，中间自动加一个空格**。

所以：

```python
print("size =", img.size)      # 输出：size = (640, 480)
print("size = " + img.size)    # ❌ 报错！字符串和元组不能相加
```

**带标签打印是个好习惯**，你在 `try_pillow.py` 里做对了：

```python
print("左上角: (0, 0)")        # ❌ 看不出是哪个点算出来的
print("左上角:", px[0, 0])     # ✅ 值变了你也一眼看清
```

## 3.4 返回值：函数干了活，得交回来

```python
px = img.load()
```

`img.load()` 去读了像素，**把结果交回来**，我们用 `px = ...` **接住**它。

**不接会怎样？** 东西丢了：

```python
img.load()                    # 读了，但没接住，白读
px = img.load()               # ✅ 接住了，以后用 px
```

## 3.5 常见报错怎么读（TypeError 系列）

```python
TypeError: object of type 'PixelAccess' has no len()
```

**逐段读**：

| 片段 | 意思 |
| --- | --- |
| `TypeError` | 类型错误 —— "你给的东西类型不对，这活儿我干不了" |
| `object of type 'PixelAccess'` | 出问题的东西是一个"像素表" |
| `has no len()` | 它**没有** `len()` 这个功能 |

翻译成人话：**"像素表这种东西，不支持数长度。"**

👉 想知道图片多大，用 `img.size`，**永远别去数像素**。

## 🔬 动手验证

```bash
python -c "print('a', 1, True)"
python -c "print(len('hello'))"
python -c "print('5' + 5)"       # 故意报错，看报错长什么样
```

---

# 第 4 章：元组、下标、坐标系 —— 取像素的核心

## 4.1 元组的读法：从头开始数，从 0 数

```python
pt = (10, 20, 30)
pt[0]      # 10  ← 第一个
pt[1]      # 20  ← 第二个
pt[2]      # 30  ← 第三个
pt[3]      # ❌ IndexError: tuple index out of range
```

**下标从 0 开始**，这是编程界的统一规矩，不是 Python 特例。所以 3 个元素的下标是 `0/1/2`。

**负数**从尾巴数：

```python
pt[-1]     # 30  ← 最后一个
```

## 4.2 元组解包：一次拿三个

```python
r, g, b = src[x, y]        # (91, 200, 31) → r=91, g=200, b=31
```

等价于：

```python
pixel = src[x, y]          # pixel 是 (91, 200, 31)
r = pixel[0]               # 91
g = pixel[1]               # 200
b = pixel[2]               # 31
```

**解包版更清爽**，也是 Python 的习惯写法。

## 4.3 像素坐标：`src[x, y]` 里 x 和 y 谁在前？

**PIL 的规矩：`[x, y]` —— 横坐标在前。**

坐标系的图（想象你的屏幕）：

```
        x →
   ┌─────────────────────┐
 y │ (0,0)        (639,0)│   ← 左上角是原点
 ↓ │                     │
   │ (0,479)   (639,479) │   ← 右下角是 (宽-1, 高-1)
   └─────────────────────┘
```

| 要取的点 | 写法（w=640, h=480） |
| --- | --- |
| 左上角 | `px[0, 0]` |
| 右上角 | `px[w - 1, 0]` |
| 左下角 | `px[0, h - 1]` |
| 右下角 | `px[w - 1, h - 1]` |
| 正中心 | `px[w // 2, h // 2]` |

**为什么右下角是 `w-1` 不是 `w`？** 因为从 0 开始数：640 个像素的编号是 `0 ~ 639`。

## 4.4 两套括号（新手必错）

```python
dst[x, y] = 148                    # ✅ 坐标是一个整体 (x, y)，只有一对方括号
dst[(x, y)] = 148                  # ✅ 完全等价，Python 自己看懂了
dst[x][y] = 148                    # ❌ 这是"二维表"的写法，像素表不是这样用的
```

同理，`putpixel` 用**圆括号**：

```python
out.putpixel((x, y), 148)          # ✅ 值也是括号包的
out.putpixel(x, y, 148)            # ❌ 少了一层括号
```

## 4.5 重要预告：NumPy 的顺序是反的

```python
PIL:   px[x, y]        # 横、纵
NumPy: arr[y, x]       # 纵、横（因为是"第 y 行"）
```

W2 换到 NumPy 时这是头号翻车点。**现在先记住 PIL 是 `[x, y]`**。

## 🔬 动手验证

```bash
python
```
```python
>>> t = (91, 200, 31)
>>> r, g, b = t
>>> r
91
>>> t[-1]
31
>>> t[0]
91
>>> exit()
```

---

# 第 5 章：数据类型和数字运算

## 5.1 int / float / str / bool

```python
n = 5               # int     整数
f = 0.299           # float   小数
s = "testdata"      # str     文本（引号）
ok = True           # bool    真/假
```

**关键区别**：`5` 和 `"5"` 是**完全不同的东西**。

```python
5 + 5         # 10    （数字相加）
"5" + "5"     # "55"  （文本拼接！）
5 + "5"       # ❌ TypeError: unsupported operand type(s)
```

## 5.2 算术运算符

```python
7 + 2      # 9      加
7 - 2      # 5      减
7 * 2      # 14     乘（注意：Python 里乘号是 *，不是 ×）
7 / 2      # 3.5    除（结果永远是小数）
7 // 2     # 3      整除（只要整数部分）
7 % 2      # 1      取余（除不尽的零头）
7 ** 2     # 49     幂
```

**`//` 是你在取"中间点"时的关键**：

```python
640 // 2     # 320  ← 整数，可以直接当下标用
640 / 2      # 320.0 ← 小数，当下标用会报错！
```

## 5.3 灰度公式的运算过程

```python
Y = 0.299*r + 0.587*g + 0.114*b
```

以 `(91, 200, 31)` 为例：

| 步骤 | 计算 | 结果 |
| --- | --- | --- |
| ① | `0.299 * 91` | `27.209` |
| ② | `0.587 * 200` | `117.400` |
| ③ | `0.114 * 31` | `3.534` |
| ④ 相加 | `27.209 + 117.400 + 3.534` | `148.143` |

因为是小数，**塞不进灰度图**（灰度图只收 0~255 的整数），必须转：

```python
int(148.143)      # 148  ← 截断（小数部分直接扔掉）
round(148.143)    # 148  ← 四舍五入
int(148.7)        # 148  ← 截断的差别在这
round(148.7)      # 149  ← 这里就看出来了
```

**选哪个？** 两个都能用，但**全项目必须统一**，并且**写进注释**说明你的选择 —— 因为 W3 要拿它跟 OpenCV 的结果对比，标准不一致就没法比。

## 5.4 运算符优先级

`*` 和 `/` 比 `+` 和 `-` 先算（跟数学一样）。拿不准就**加括号**：

```python
0.299*r + 0.587*g    # 先算两个乘法，再相加 ✅
(0.299*r + 0.587*g) / 2   # 括号让语义一目了然
```

## 5.5 范围问题：为什么公式结果一定在 0~255

因为 `0.299 + 0.587 + 0.114 = 1.0`，三个系数加起来正好是 1 —— 这是**加权平均**，不是随便定的。

如果 R、G、B 都是最大 255，结果就是 `255 × 1.0 = 255`，正好卡在上限，**永远不会越界**。

## 🔬 动手验证

```bash
python -c "print(640 // 2, 640 / 2)"
python -c "print(0.299*91 + 0.587*200 + 0.114*31)"
python -c "print(int(148.7), round(148.7))"
python -c "print('5' + '5', 5 + 5)"
```

---

# 第 6 章：缩进和 if 分支

## 6.1 缩进 = 层级（Python 最独特的地方）

其他语言用 `{}` 表示"这几行是一伙的"，**Python 用缩进**。

```python
def f():
    print("我在函数里面")      # 缩进 4 空格 → 属于 f
print("我在函数外面")          # 顶格 → 不属于 f
```

**规则（重要）**：

| 规则 | 说明 |
| --- | --- |
| 同一个块里缩进必须**完全一样** | 都用 4 空格，不能一行 4 一行 2 |
| **不要混用 Tab 和空格** | VS Code 里按 Tab 会自动转 4 空格，统一用它 |
| 冒号 `:` 后面**必须换行 + 缩进** | `def f():`、`if x:`、`for y in ...:` 都是 |

**报错长这样**：

```
IndentationError: expected an indented block
IndentationError: unindent does not match any outer indentation level
```

看到 `IndentationError`，**90% 是缩进没对齐**，去看报错指的那一行和它上面一行。

## 6.2 if：让程序做判断

```python
if img.mode == "L":
    print("这本来就是灰度图")
elif img.mode == "RGBA":
    print("这是带透明通道的图")
else:
    print("这是普通彩色图")
```

**逐行读**：

| 写法 | 意思 |
| --- | --- |
| `if 条件:` | 如果条件成立，就做下面缩进的事 |
| `elif 条件:` | 否则，如果这个条件成立……（可以有零个或多个） |
| `else:` | 上面的都不成立，就做这个 |
| `==` | **判断相等**（两个等号！） |

⚠️ **`=` 和 `==` 是两件事**：

```python
x = 5        # 赋值：把 5 存进 x
x == 5       # 比较：x 是不是等于 5？ → True 或 False
if x = 5:    # ❌ 语法错误
if x == 5:   # ✅
```

## 6.3 字符串比较

```python
img.mode == "L"        # 注意引号！L 是文本，不是变量
img.mode == L          # ❌ NameError: name 'L' is not defined
```

**记住：只要是比较"某个文字"，就要加引号。**

## 6.4 逻辑组合

```python
if x > 0 and y > 0:      # 两个都成立
if x > 0 or y > 0:       # 至少一个成立
if not ok:               # 取反
```

## 🔬 动手验证

```bash
python
```
```python
>>> mode = "L"
>>> if mode == "L":
...     print("是灰度图")
... else:
...     print("不是")
```
（在交互模式里，输完 `if` 那一行按回车会变成 `...` 提示符，还要再按一次回车才开始执行）

---

# 第 7 章：循环 —— 一个像素一个像素地扫

## 7.1 `range()`：造一串数

```python
range(5)          # 生成 0, 1, 2, 3, 4    （5 个数，从 0 开始，不含 5）
list(range(5))    # 想看清楚就用 list() 包一下：[0, 1, 2, 3, 4]
```

**记住：`range(n)` 产生 `0 ~ n-1`，不含 n**。所以遍历 640 个像素用 `range(640)`。

## 7.2 单层 for：一行一行扫

```python
for y in range(h):
    print(y)
```

**逐字读**：`for` = "对……中的每一个"，`y` = 临时名字（每次循环都会更新），`range(h)` = 一串 0 到 h-1。

连起来：**"对于 0 到 h-1 里的每一个数，把它叫做 y，然后做下面缩进的事。"**

执行过程（假设 h=3）：

| 第几轮 | y 的值 | 做了什么 |
| --- | --- | --- |
| 第 1 轮 | 0 | 执行缩进的代码 |
| 第 2 轮 | 1 | 执行缩进的代码 |
| 第 3 轮 | 2 | 执行缩进的代码 |
| 结束 | — | 继续往下执行不缩进的代码 |

## 7.3 双重 for：扫遍整张图

```python
for y in range(h):            # 外层：每一行
    for x in range(w):        # 内层：这一行里的每一列
        r, g, b = src[x, y]   # 取这一个像素
        Y = 0.299*r + 0.587*g + 0.114*b
        dst[x, y] = int(Y)
```

**执行过程（h=2, w=3 的小图）**：

| 外层 y | 内层 x | 处理的坐标 | 是第几个像素 |
| --- | --- | --- | --- |
| 0 | 0 | `(0, 0)` | 第 1 个 |
| 0 | 1 | `(1, 0)` | 第 2 个 |
| 0 | 2 | `(2, 0)` | 第 3 个 |
| 1 | 0 | `(0, 1)` | 第 4 个 |
| 1 | 1 | `(1, 1)` | 第 5 个 |
| 1 | 2 | `(2, 1)` | 第 6 个 |

**顺序是从左到右、从上到下**（跟读书一样）。总次数 = `h × w`。

**缩进层级（最容易错的地方）**：

```python
for y in range(h):            # ← 0 空格
    for x in range(w):        # ← 4 空格
        r, g, b = src[x, y]   # ← 8 空格
        Y = ...               # ← 8 空格
        dst[x, y] = int(Y)    # ← 8 空格
    print("这一行扫完了")       # ← 4 空格（在 y 循环里，不在 x 循环里）
print("全部扫完了")            # ← 0 空格（循环外面）
```

**判断某一行属于哪层，就看它的缩进量。** 属于内层的代码，每扫一个新像素就执行一次；属于外层的代码，每扫完一整行才执行一次。

## 7.4 `while` 循环（认识即可）

```python
i = 0
while i < 5:
    print(i)
    i = i + 1        # 必须有让条件变化的一步，否则死循环
```

对我们这个任务**用 `for`**，`while` 是处理"不知道要循环多少次"的场景。

## 7.5 循环里的累加（统计会用到）

```python
count = 0
for x in range(10):
    count = count + 1        # 或者写 count += 1
print(count)                 # 10
```

**初始化要在循环外面**（写在里面就每次被清零了）。

## 🔬 动手验证

```bash
python
```
```python
>>> for y in range(2):
...     for x in range(3):
...         print("坐标", x, y)
```
（应该打印 6 行，顺序是 (0,0) (1,0) (2,0) (0,1) (1,1) (2,1)）

---

# 第 8 章：函数 `def` —— 把一段代码打包

## 8.1 为什么要有函数

假设你要处理 100 张图。不打包的话，这段循环代码要复制 100 遍。改起来要改 100 处。

**函数 = 给一段代码起个名字，以后喊名字就行。**

## 8.2 定义（造机器）

```python
def to_gray(img):
    """输入一张 RGB 图片，返回灰度图。"""
    w, h = img.size
    ...
    return out
```

**逐部分读**：

| 部分 | 意思 |
| --- | --- |
| `def` | define，我要定义一台机器 |
| `to_gray` | 机器的名字（自己起，习惯用小写+下划线） |
| `(img)` | **入口**：这台机器需要你给它一个东西，它管这个东西叫 `img` |
| `:` | 后面要换行缩进了 |
| `"""..."""` | 文档字符串：说明这台机器干什么（不是必须，但强烈建议） |
| 缩进的代码 | 机器的内部构造，别人看不见过程 |
| `return out` | **出货口**：把结果交出去 |

## 8.3 调用（用机器）

```python
gray = to_gray(img)
```

**读法**：把 `img` 塞进 `to_gray` 这台机器，它吐出结果，我们用 `gray` 接住。

**定义和调用的关系**：

```python
def to_gray(img):     # 这里 img 只是个"占位名"，谁被塞进来就叫谁 img
    ...

gray = to_gray(my_photo)     # 实际塞的是 my_photo，于是机器里的 img 就是 my_photo
gray2 = to_gray(other_photo) # 同一台机器可以反复用，料不同
```

## 8.4 `return` 的两个作用（必懂）

```python
def f(x):
    return x * 2      # ① 把结果交出去 ② 立刻结束函数
    print("永远到不了这行")   # ← 死代码，return 之后的东西不会执行

y = f(5)              # y = 10
```

**忘记了 `return` 会怎样？**

```python
def f(x):
    x * 2             # 算了，但没交出去

y = f(5)              # y = None（啥都没有）
print(y)              # None
```

这叫"函数偷偷返回了 None"，是新手最常犯、最难发现的错之一 —— **函数算完必须 `return`**。

## 8.5 参数（入口）和默认值

```python
def to_gray(img):                    # 需要 1 个参数
    ...

def save_img(img, path):             # 需要 2 个参数，按位置对应
    img.save(path)

save_img(gray, "out/x.png")          # 第 1 个给 img，第 2 个给 path
```

## 8.6 函数的好处（为什么我们要用它）

```python
def to_gray(img):        # 逻辑写在这
    ...

gray1 = to_gray(Image.open("a.jpg"))     # 复用它
gray2 = to_gray(Image.open("b.png"))     # 复用它
gray3 = to_gray(Image.open("c.png"))     # 复用它
```

**如果灰度公式要改（比如换成另一套系数），只改函数里那 1 行，三处调用自动全部生效。**

## 8.7 `if __name__ == "__main__":` 是什么

```python
def to_gray(img):
    ...

if __name__ == "__main__":
    img = Image.open("testdata/small_640x480.jpg")
    gray = to_gray(img)
    gray.save("out/x.png")
```

**先说结论：现在照抄就行，作用只有一句话**——

- **直接跑这个文件时**（`python try_pillow.py`）：`__name__` 等于 `"__main__"`，**if 里面会执行**；
- **别人 `import` 这个文件时**：if 里面**不执行**，只拿走 `to_gray` 这个函数去用。

**为什么需要它？** 以后你的 `grayscale_cli.py` 可以被别的脚本导入复用。如果没这层保护，一 `import` 就会自动开始处理图片，很糟糕。

> 进阶：在交互模式里 `>>> import try_pillow` 试一下，你会发现它没打印任何东西 —— 这就是这行的作用。

## 🔬 动手验证

```bash
python
```
```python
>>> def double(x):
...     return x * 2
...
>>> double(21)
42
>>> def bad(x):
...     x * 2
...
>>> bad(21)            # 什么都不显示，因为返回了 None
>>> print(bad(21))
None
>>> exit()
```

---

# 第 9 章：错误处理 `try / except` —— 一个坏文件不能拖垮整批

## 9.1 为什么需要它

批量处理 100 张图，其中第 37 张是坏文件。**没有错误处理，程序直接崩，剩下 63 张全不处理。**

**`try/except` 就是"如果这里出事，别崩，改走备用方案"。**

## 9.2 基本写法

```python
try:
    risky_thing()
except Exception as e:
    print("出事了，但我不崩:", e)
print("我会继续往下跑")
```

| 部分 | 意思 |
| --- | --- |
| `try:` | 试着执行下面缩进的代码 |
| `except Exception as e:` | 如果出事，**抓住错误**，把它装进变量 `e` |
| `as e` | 给抓住的错误起个名字叫 e |
| `print(..., e)` | 把错误内容打印出来（方便你知道发生了什么） |

**关键：出了事，`try` 里剩下的代码不执行，但 `except` 后面的代码照常执行 —— 程序不崩。**

## 9.3 `e` 里面是什么

```python
except Exception as e:
    print(type(e).__name__, ":", e)
```

输出例子：

```
UnidentifiedImageError : cannot identify image file 'testdata/notes.txt'
```

| 部分 | 意思 |
| --- | --- |
| `type(e)` | 这个错误是什么类型 |
| `.__name__` | 类型的名字（`UnidentifiedImageError`） |
| `e` | 错误的说明文字 |

**打印错误类型 + 文件名**，这样出问题时你才知道是哪个文件、因为什么。

## 9.4 常见的错误类型（认识就行）

| 类型 | 什么时候出现 |
| --- | --- |
| `NameError` | 名字没定义（忘了 import / 拼错 / 变量不存在） |
| `TypeError` | 类型不匹配（字符串 + 数字） |
| `ValueError` | 值不对（`int("abc")`） |
| `FileNotFoundError` | 文件/目录不存在 |
| `ZeroDivisionError` | 除以 0 |
| `UnidentifiedImageError` | PIL 认不出这个文件是图片 |
| `SyntaxError` / `IndentationError` | 代码本身写错了（**这种 try 抓不到，只能改代码**） |

## 9.5 坏图片到底在哪里炸（你必踩的坑）

```python
img = Image.open("testdata/broken_truncated.jpg")   # ← 这里居然不报错！
px = img.load()                                     # ← 真正的炸点在这
```

**因为 `Image.open()` 是"懒惰"的：它只读文件头（拿到尺寸、模式），不读像素数据。**

所以截断的 JPEG 头是完整的 → `open()` 成功；等你去读像素 → 数据不够 → 炸。

**结论：`try` 的范围必须包住"取像素"，光包住 `open()` 是抓不到的。**

```python
try:
    img = Image.open(p)
    gray = to_gray(img)        # ← 取像素发生在这里面
    gray.save(out_path)
except Exception as e:
    print("跳过", p.name, type(e).__name__, e)
```

## 9.6 错误处理的纪律

```python
except Exception as e:      # ✅ 打印 + 继续处理下一个
    print(...)

except Exception as e:      # ❌ 不要静默吞掉，你会不知道出过什么事
    pass

except Exception as e:      # ❌ 批量处理里绝不要 exit，一个坏文件不该杀死整批
    sys.exit(1)

except Exception as e:      # ❌ 更不要 raise 出去
    raise
```

## 🔬 动手验证

```bash
python -c "print(1/0)"                    # 看 ZeroDivisionError
python -c "from PIL import Image; Image.open('testdata/notes.txt')"   # 看 UnidentifiedImageError
python -c "
from PIL import Image
try:
    im = Image.open('testdata/broken_truncated.jpg'); print('open 成功', im.size)
    px = im.load(); print('取像素也成功', px[0,0])
except Exception as e:
    print('抓住了:', type(e).__name__, e)
"
```

---

# 附录 A：报错全景对照表

| 报错 | 人话 | 先查什么 |
| --- | --- | --- |
| `NameError: name 'X' is not defined` | 我不认识 X | 忘了 import？拼写错？变量没定义？ |
| `TypeError: ... not iterable` | 这东西没法一个个拆 | `r, g, b = ...` 右边是不是元组 |
| `IndentationError` | 缩进乱了 | 报错行的缩进量，和上下对比 |
| `FileNotFoundError` | 找不到这个文件/目录 | 路径拼对没？`out/` 目录建了没？ |
| `IndexError` | 下标超范围 | 是不是用了 `px[w, h]`（应该是 `w-1`） |
| `ValueError: not enough values to unpack` | 拆不开 | `w, h = ...` 右边是不是两个 |
| `AttributeError: 'X' object has no attribute 'Y'` | X 没这个功能 | 方法名拼错？对象类型不对？ |
| `UnidentifiedImageError` | 这不是我能认的图片 | 文件坏了/不是图片 |

---

# 附录 B：W1 语法速查卡

```python
# 导入
from PIL import Image

# 打开 / 查看（不读像素）
img = Image.open("路径")
img.size          # (宽, 高)
img.mode          # "RGB" / "L" / "RGBA"

# 读像素（读这一步）
px = img.load()
pixel = px[x, y]          # (r, g, b)
w, h = img.size

# 造新图（单通道灰度）
out = Image.new("L", (w, h))
dst = out.load()
dst[x, y] = 值            # 0~255 的整数

# 存图
out.save("out/x.png")

# 遍历
for y in range(h):
    for x in range(w):
        ...

# 灰度公式
Y = 0.299*r + 0.587*g + 0.114*b
int(Y)      # 或 round(Y)

# 判断
if img.mode == "L":
    ...
elif img.mode == "RGBA":
    ...
else:
    ...

# 函数
def 名字(参数):
    ...
    return 结果

# 错误处理
try:
    ...
except Exception as e:
    print(...)

# 主入口
if __name__ == "__main__":
    ...
```

---

# 附录 C：每一节的"我懂了没"自检

| 自检问题 | 答不上来就回去看 |
| --- | --- |
| `from PIL import Image` 每个词什么意思？ | 第 1 章 |
| `w, h = img.size` 为什么能一行拆成两个？ | 第 2.5、4.2 节 |
| `img.size` 和 `img.load()` 的区别？ | 第 3.2 节 |
| `px[0,0]` 是哪个角？`px[w-1,h-1]` 呢？ | 第 4.3 节 |
| 为什么用 `//` 而不是 `/` 取中间点？ | 第 5.2 节 |
| 双重循环里，哪一行是 4 空格、哪一行是 8 空格？ | 第 7.3 节 |
| 函数忘了 `return` 会怎样？ | 第 8.4 节 |
| 为什么 `try` 要包住"取像素"那一步？ | 第 9.5 节 |

---

# 附录 D：学习方式建议

1. **不要在编辑器里抄完就跑** —— 先在 `python` 交互模式里把每一节的小例子敲一遍（比读十遍有用）。
2. **报错不要怕** —— 报错是 Python 在给你**指路**，附录 A 就是翻译表。
3. **不要背语法** —— 附录 B 打印出来贴在旁边，写到查。
4. **一次只推进一小步** —— 先处理 1 个像素，再上循环，再上函数，再上目录遍历。每步都跑通再加下一步。
5. **卡超过 20 分钟就把报错原文贴出来** —— 包括最后几行和报错类型。
