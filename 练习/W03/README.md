# 练习 / W3

W3 主题：**手写卷积 / 滤波 / 直方图均衡 / CLAHE —— 与 OpenCV 对标**

全部脚本都在**仓库根目录**运行（它们自己会找 `testdata/`）：

```bash
cd ~/cv-kit
python 练习/W03/w3_conv.py         # 任务 1：卷积（滑窗 + im2col）
python 练习/W03/w3_filters.py      # 任务 2：均值/高斯/中值
python 练习/W03/w3_histogram.py    # 任务 3：直方图均衡 + CLAHE
python 练习/W03/w3_compare.py      # 任务 4：一键对标出报告
python 练习/W03/w3_metrics.py      # 评估工具自检（PSNR/SSIM 本身对不对）
```

| 文件 | 需要填 TODO | 作用 |
| --- | --- | --- |
| `w3_metrics.py` | ❌ 不用填 | PSNR / SSIM / 对拍判定。**先跑它自检**，确认尺子是准的 |
| `w3_conv.py` | ✅ 2 处 | 卷积：滑窗 + im2col 两种写法 |
| `w3_filters.py` | ✅ 3 处 | 均值 / 高斯（含核生成）/ 中值 |
| `w3_histogram.py` | ❌ 不用填（是思考题） | HE + CLAHE 完整参考，你的任务是读懂 + 改着玩 |
| `w3_compare.py` | ❌ 不用填 | 一键对标，产出三联图和 Markdown 报告 |

## 建议顺序

1. **先跑 `w3_metrics.py`** —— 确认评估工具本身可信（PSNR 定义、SSIM 边界行为）
2. **`w3_conv.py`** —— 核心。先写滑窗版，对拍过了再写 im2col
3. **`w3_filters.py`** —— 复用卷积，重点在高斯核和 σ 公式
4. **`w3_histogram.py`** —— 读代码 + 做 TODO B/C/D 的观察实验
5. **`w3_compare.py`** —— 全部跑一遍，出报告
6. 打开 `out/w3/*.png` 看差异热力图，把 `学习资料/W03/对标报告.md` 填完

## 产物位置

| 产物 | 路径 |
| --- | --- |
| 三联对比图（OpenCV \| 手写 \| 差异热力图） | `out/w3/*.png` |
| 自动生成的报告草稿 | `out/w3/对标结果.md` |
| **要交的对标报告** | `学习资料/W03/对标报告.md`（手动填完） |

> `out/` 已在 `.gitignore` 里 —— **图不进版本库**，但报告（Markdown）要提交。

## 验收线一览

| 算子 | 验收线 | 参考实现能做到 |
| --- | --- | --- |
| 卷积（任意核） | PSNR ≥ 45 dB | **inf（完全一致）** |
| 均值滤波 | ≥ 50 dB | inf |
| 高斯滤波 | ≥ 55 dB | 63.7 dB（cv2 用定点数的必然差异） |
| 中值滤波 | ≥ 50 dB | inf（边界用 `mode="edge"`） |
| 直方图均衡 | 逐像素一致 | inf |
| CLAHE | ≥ 30 dB | 47.0 dB |

**参考值都是实测得出的**（W3 材料准备阶段在同一台机器上跑出来的），
不是拍脑袋定的线——所以"过不了"通常意味着真有问题，不是标准太严。
