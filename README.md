# 算法动画模板 · ManimGL

把"做一支算法讲解动画"变成一件有规范、可复用的事。

当前递归模板按 `3163.mp4`：执行代码文字标蓝、底部字幕整幅居中、代码下方显示当前栈帧。见 **[通用递归模板](docs/recursion-template.md)**，可复制 `templates/recursion_scene.py` 或用生成器生成。

内置一套视觉与节奏规范（纯黑背景、白蓝红绿四色、分步变化后留出阅读时间），
你只需要描述**这一期要讲什么算法**，引擎负责把它渲染成 1080p 视频。

- 引擎不绑定具体算法。递归树、数组、双指针……结构由算法决定，不统一套成递归树。
- 规范写在代码里，不靠每一期手工对齐配色和节奏。
- `examples/` 下有两个完整示例，覆盖两种完全不同的结构。

---

## 快速开始

```bash
git clone <本仓库地址>
cd manim-algorithm-animation

# 1. 自检：缺什么会直接告诉你
python tools/check_env.py

# 2. 渲染一个示例
python tools/render.py examples/binary_search/scene.py
#    成片输出到 out/binary_search.mp4
```

如果 `check_env.py` 提示缺 manimgl 或 ffmpeg，见下面的「环境准备」。

---

## 环境准备

仓库只放依赖声明，不放环境本身 —— Python 解释器和 manimgl 的二进制是
平台绑定的，体积也大，`pip` 一条命令就能重建。

| 依赖 | 装法 |
|---|---|
| Python ≥ 3.9（建议 3.12） | 系统自行安装 |
| manimgl 及全部 Python 依赖 | `pip install -r requirements.txt` |
| ffmpeg | 系统级，**必须在 PATH 里**，manimgl 用它把帧合成 MP4 |
| 中文字体 | 思源黑体 / Noto Sans CJK SC / 微软雅黑 / 苹方，**任意一个**即可 |

字体是自动挑的（`engine/theme.py` 里按优先级逐个探测），所以不必先装思源黑体。
一个中文字体都没有时会回退到通用族名，可能缺字 —— `check_env.py` 会给出警告。

一键配置（创建 `.venv` 并按 `requirements.txt` 安装）：

```bash
bash scripts/setup.sh                 # macOS / Linux / Git Bash
powershell -File scripts\setup.ps1    # Windows PowerShell
```

手动装也行：

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt      # Windows 用 .venv\Scripts\pip
```

装完务必跑一次 `python tools/check_env.py`，ffmpeg 和中文字体缺了它会直接说。

---

## 怎么加一个新算法

以"想讲清冒泡排序"为例，全程只写一个文件：

```bash
mkdir examples/bubble_sort
cp PRD_TEMPLATE.md examples/bubble_sort/README.md   # 填这一期的内容
$EDITOR examples/bubble_sort/scene.py
```

`scene.py` 的骨架只有三件事：

```python
import os, sys
_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, "engine")):
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, _ROOT)

from manimlib import *
from engine import AlgoScene, ArrayView, theme


class BubbleSort(AlgoScene):
    TITLE_TEXT = "冒泡排序"
    TITLE_TAG = "n = 6"

    CODE_SOURCE = (
        "void bubble(int a[], int n) {",
        "    for (int i = 0; i < n - 1; ++i)",
        "        for (int j = 0; j < n - 1 - i; ++j)",
        "            if (a[j] > a[j + 1]) swap(a[j], a[j + 1]);",
        "}",
    )

    def build(self):
        self.array = ArrayView(self, (5, 1, 4, 2, 8, 3), center=(2.3, 0.5))
        self.add_title()
        self.add_code()
        self.code.bind(outer=1, inner=2, cmp=3)
        self.array.appear()

        for i in range(5):                 # ← 这里就是分镜，按真实执行顺序写
            for j in range(5 - i):
                self.code.focus(self, "cmp")
                self.array.compare(j, j + 1)
                if self.array.values[j] > self.array.values[j + 1]:
                    self.array.swap(j, j + 1)
```

然后：

```bash
python tools/render.py examples/bubble_sort/scene.py
```

**没有别的东西要配置** —— 背景色、配色、字号、安全边距、节奏都已经由引擎按规范内置。

---

## 目录结构

```
engine/              通用引擎（核心）
  theme.py           颜色与跨平台字体选择
  scene.py           AlgoScene 基类：背景、布局、节奏常量
  panel.py           标题 / 蓝色执行代码 / 栈帧详情 / 居中字幕 / 结论页
  recursion.py       通用递归事件场景
  stack_state.py     独立保存每层现场的活动调用栈
  text_layout.py     按实际字宽换行
  tree.py            递归树：TreeSpec + TreeView
  array.py           数组：ArrayView
templates/recursion_scene.py   可复制的通用递归模板
examples/            示例（每个示例一个目录，互不依赖）
  fibonacci_recursion/   递归树结构
  binary_search/         数组 + 双指针结构
tools/
  check_env.py       环境自检
  render.py          一键渲染
scripts/             环境安装脚本
PRD_TEMPLATE.md      每期动画的填写模板
```

---

## 引擎 API 速查

### 继承 `AlgoScene`

```python
class MyScene(AlgoScene):
    TITLE_TEXT = "标题"          # 左上角
    TITLE_TAG = "n = 5"          # 标题右边的蓝色标记，可省
    CODE_SOURCE = (...)          # 代码行，原样显示

    def setup(self):             # 可选：准备数据
    def build(self):             # 必须实现：写分镜
```

引擎已固定的布局：左侧约 38% 放代码与局部变量，右侧约 62% 放图形，
底部一行提示。想改就覆写 `CODE_CENTER` / `STATUS_CENTER` / `HINT_CENTER` / `TREE_BOX`。

### 代码面板

```python
code = self.add_code()                  # 显示并返回面板
code.bind(sig=0, base=1, left=2)        # 给行起名字
code.focus(self, "base")                # 这一行文字与光标变蓝，旧行恢复白色
code.focus_now("base")                  # 不播放动画，直接定位
code.hide(self)                         # 淡出
```

代码太长冲出安全边距时，面板会**自动缩小字号**，不需要手工调。

### 递归树

```python
spec = TreeSpec(nodes, children, leaf_order)   # nodes: (id, 显示名, 深度, 父id)
tree = self.add_tree(spec)

tree.root()                     # 只显示根节点
tree.enter(nid)                 # 按真实调用顺序长出一个节点
tree.return_value(nid, "=1")    # 绿色返回值出现在节点下方，再沿边回传父节点
tree.send_up(nid)               # 只回传（用于非边界情况的求和结果）
tree.mark_done(nid)             # 边框转绿：已完成
tree.cost_animation(nid)        # 红色强调：重复计算等代价
tree.ids_with_label("fib(2)")   # 按显示名筛选节点
```

`nodes` 里每个 id 是一次**独立调用**；同参数的多次调用必须给不同 id，
不能合并成共享节点。

### 数组

```python
arr = ArrayView(self, (3, 7, 11), center=(2.3, 0.5))
arr.appear()
arr.compare(i, j)               # 一起变蓝
arr.swap(i, j)                  # 交换内容（值移动，格子不动）
arr.hit(i)                      # 转绿：命中 / 已确定
arr.cost(i)                     # 转红：越界、冲突等代价
arr.dim_except([i])             # 其余变暗
arr.pointer(i, "lo")            # 格子下方加箭头 + 名字
```

### 状态与提示

```python
status = self.add_status()
status.set_call("fib(2)", left=1)        # → fib(2)    left = 1
status.set_expr("fib(2)", "1 + 0 = 1")
status.clear()

hint = self.add_hint()
hint.set("到达边界，返回")  # 整幅画面底部居中，约 46px 视觉字高
hint.clear()
```

### 结论页

```python
from engine import curtain, complexity_row

curtain(self)                                     # 压暗已有画面
rows = VGroup(complexity_row("时间上界  ", "2", "n", theme.RED),
              complexity_row("栈空间    ", "", "n", theme.GREEN))
```

`complexity_row` 的指数用手工上标排版，不依赖 LaTeX，
也不使用可能缺字的上标字符。

---

## 视觉与节奏规范

引擎内置的规则，改之前建议先想清楚：

**颜色只有四种含义，不新增**

| 颜色 | 含义 |
|---|---|
| 白 `#FFFFFF` | 普通文字、非活动代码、历史节点、常规连线 |
| 蓝 `#58C4DD` | 当前执行位置、当前处理的对象、正在进入的路径 |
| 红 `#FC6255` | 重复计算、冲突、需要特别注意的代价 |
| 绿 `#83C167` | 已确定的值、已完成的操作、正确结果、返回的数据 |

背景统一纯黑 `#000000`，不用深蓝底、渐变、光晕、阴影、大面积彩色卡片。

**节奏：看清一个变化，停下来读懂，再进行下一个变化**

`AlgoScene` 上挂着几档节奏常量，分镜里直接取用：

| 常量 | run_time / hold | 用在 |
|---|---|---|
| `FIRST` | 1.00 / 2.30 | 首次出现的关键规则、边界、返回 |
| `NORMAL` | 0.55 / 1.80 | 普通的移动、连线、数值变换 |
| `REPEAT` | 0.45 / 1.60 | 已讲清的重复步骤 |
| `LOCAL_RESULT` | 0.65 / 2.30 | 一个完整的局部结果 |
| `CONCLUSION` | 0.70 / 3.00 | 最终结论 |

这些是起点而不是累加公式。**不要**为了凑时长把整片渲染完再统一加速。

**输出**：1920 × 1080、30 fps、H.264 MP4，默认无配音无背景音乐，
靠代码、图形和简短标签说明。

---

## 示例

| 示例 | 结构 | 时长 |
|---|---|---|
| `examples/fibonacci_recursion` | 递归调用树，15 次调用，真实深度优先 | 49 s |
| `examples/binary_search` | 数组 + lo/hi/mid 双指针 | 24 s |

两者的画面结构完全不同，但共用同一套引擎 —— 加新结构时照
`engine/array.py` 的样子再写一个模块即可（图、栈、队列同理）。

---

## 每期动画的填写模板

`PRD_TEMPLATE.md` 是给每一期动画用的填写模板：先确定学习目标，
再写执行记录，最后排分镜。**建议先填完模板再写 `scene.py`**，
否则很容易做出"看起来合理但执行顺序不真实"的动画。

填完怎么变成代码，见 **[docs/prd-to-scene.md](docs/prd-to-scene.md)** ——
用二分查找那一期逐项对照，说明 PRD 的每一栏落到 `scene.py` 的哪一段。

## 只有代码？递归类算法可以自动生成骨架

递归算法的画面结构不用选（**就是调用树**），执行记录也不用手工数 ——
跑一遍就有。所以递归类可以省掉最机械、最容易写错的那部分：

```bash
# 1. 写一份逐句对应的 Python 等价版（展示给观众的仍然是 C++）
#    见 examples/fibonacci_recursion/fib_py.py

# 2. 跑一遍，导出完整调用树
python tools/trace.py examples/fibonacci_recursion/fib_py.py:fib \
    --args 5 --label "fib({0})" -o traces/fib.json

# 3. 从调用树生成可运行的 scene.py 骨架
python tools/scaffold.py traces/fib.json \
    --out examples/my_algo/scene.py --class MyAlgo \
    --title "非记忆化递归" --tag "fib(5)" \
    --code examples/fibonacci_recursion/code.cpp \
    --bindings examples/fibonacci_recursion/bindings.json \
    --params n --receivers left,right --conclusion examples/fibonacci_recursion/conclusion.json
```

步骤 2 顺带会报告一份核对清单：调用次数、基础情况次数、各参数出现次数、
最大深度，以及**「进入与返回是否严格交替」** —— 最后一项直接验证执行顺序
是真实的深度优先，而不是按层展开再逐层返回。

步骤 3 生成继承 `RecursionScene` 的场景，复用真实调用树、事件顺序、栈帧保存/恢复、居中字幕与蓝色执行代码。C++ 和代码行号映射必须显式提供；生成器不会为其他算法填入 Fibonacci 代码、假设两个分支或凭子返回值拼出求和公式。

调用记录只包含调用/返回边界，不能推断中间的判断、循环、局部变量赋值或撤销操作。制作完整逐语句讲解时应补充分镜。详见 [通用递归模板](docs/recursion-template.md)。旧手写示例可能自定义位置与节奏，新生成示例在 `examples/fibonacci_recursion/scene_gen.py`；两者不要混同为已全部迁移。

> 非递归算法（排序、查找、图遍历）不适用这条路：画面结构需要人选
> （数组？图？），"哪一步值得详细讲"也不能从代码推出来。

## License

MIT
