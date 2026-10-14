# 从 PRD 到 scene.py

`PRD_TEMPLATE.md` 第二部分填完之后，怎么把它变成能跑的动画？

这份文档用**二分查找**那一期做例子，逐项对应。左边是 PRD 里填的内容，
右边是 `examples/binary_search/scene.py` 里对应的代码。

结论先说：**PRD 第二部分和 `scene.py` 是一一对应的**，不是两份独立的东西。
照着填，代码基本就是"翻译"。

---

## 对照总表

| PRD 第二部分 | 落到代码的哪里 | 怎么落 |
|---|---|---|
| §6 任务卡 | 类属性 `TITLE_TEXT` / `TITLE_TAG` / `DATA` / `TARGET` | 直接抄 |
| §7 C++ 演示代码 | 类属性 `CODE_SOURCE` | 原样贴，缩进别动 |
| §8 正确性基准 | **不写进代码**，但要用它核对渲染结果 | 验收时对照 |
| §9.1 执行顺序 | `build()` 里的循环 / 调用顺序 | 一行一行翻译 |
| §9.2 单步视觉过程 | `build()` 里用的引擎原语 | 挑对应的 API |
| §10 布局与颜色 | 基本不用写 | 引擎默认值就是规范 |
| §11 分镜 | `build()` 里的分段 | 一段一个方法 |
| §12 验收清单 | **不写进代码** | 出片后逐条看 |

---

## 一、§6 任务卡 → 类属性

PRD 里填的：

> - **主题**：在有序数组里查找目标值，每轮排除一半区间。
> - **演示输入**：`a = {3, 7, 11, 18, 25, 33, 41}`，目标 `25`。

代码里：

```python
DATA = (3, 7, 11, 18, 25, 33, 41)
TARGET = 25


class BinarySearch(AlgoScene):
    TITLE_TEXT = "二分查找"
    TITLE_TAG = f"target = {TARGET}"
```

`TITLE_TEXT` 渲染成左上角的白色标题，`TITLE_TAG` 是它右边的蓝色标记。
示数、目标值这类参数放模块级常量，`CODE_SOURCE` 和其它地方都能引用。

**容易漏**：PRD 的"演示输入"要选**规模小、能看全**的。7 个格子的数组正好铺满右侧，
再多就要缩小格子了。

---

## 二、§7 演示代码 → `CODE_SOURCE`

PRD 里贴的 C++ 原样搬进元组，一行一个字符串：

```python
CODE_SOURCE = (
    "int bsearch(int a[], int n, int x) {",
    "    int lo = 0, hi = n - 1;",
    "    while (lo <= hi) {",
    "        int mid = (lo + hi) / 2;",
    "        if (a[mid] == x) return mid;",
    "        if (a[mid] < x) lo = mid + 1;",
    "        else hi = mid - 1;",
    "    }",
    "    return -1;",
    "}",
)
```

**两条经验**：

1. **缩进原样保留**，引擎不做格式化。行太长时会**自动缩字号**（`max_width=4.10`），
   不用手工调 —— 但代码太宽终究会变小，能压短就压短。
2. **行号要能对上分镜**。写完先数一遍下标，后面 `bind()` 要用。

---

## 三、§9.1 执行顺序 → `build()` 的骨架

PRD §9.1 是按真实顺序列的事件表：

> | 轮 | lo | hi | mid | a[mid] | 判断 | 动作 |
> |---|---|---|---|---|---|---|
> | 1 | 0 | 6 | 3 | 18 | 18 < 25 | `lo = mid + 1 = 4` |
> | 2 | 4 | 6 | 5 | 33 | 33 > 25 | `hi = mid - 1 = 4` |
> | 3 | 4 | 4 | 4 | 25 | 命中 | 返回 4 |

**这张表直接就是循环体**：

```python
lo, hi = 0, len(DATA) - 1
while lo <= hi:
    mid = (lo + hi) // 2          # 表中的 mid 列
    ...
    if DATA[mid] == TARGET:       # 表中的"判断"列
        ...                       # 命中 → 返回
        break
    if DATA[mid] < TARGET:
        lo = mid + 1              # 表中的"动作"列
    else:
        hi = mid - 1
```

**这一步是整份文档里最要紧的**：不要凭印象写动画，照着执行记录翻译。
否则很容易做出"看起来合理但执行顺序不真实"的片子 —— 斐波那契那一期如果
按层展开再逐层返回，就是典型错误。

---

## 四、§9.2 单步视觉过程 → 引擎原语

PRD 里写"进入 / 命中 / 推进"的自然语言，对应到具体 API：

| PRD 里的话 | 代码 |
|---|---|
| "当前行用蓝色光标定位" | `self.code.focus(self, "mid")` |
| "在网格下方指出当前端点" | `self.move_pointer("lo", lo, theme.BLUE)` |
| "越界或冲突需要特别注意" | `self.array.cost(mid)` |
| "命中，结果正确" | `self.array.hit(mid)` |
| "其余内容退到次要位置" | `self.array.dim_except([mid])` |
| "左侧显示当前步骤的中间值" | `self.status.set(f"lo = {lo}    hi = {hi}")` |
| "底部一行简短提示" | `self.hint.set("命中 a[4]")` |

递归树结构换成 `tree.*` 的原语，见 `engine/tree.py`；
数组换成 `engine/array.py`。**两种结构之外的（图、栈、队列）目前没有现成组件**，
照 `engine/array.py` 的样子新写一个模块即可，接口风格保持一致就行。

---

## 五、§10 布局与颜色 → 通常不用写

PRD §10 规定的"左侧 38% 代码 / 右侧 62% 图形 / 四色语义 / 安全边距"，
**已经在引擎里了**，正常情况一行都不用写：

- 背景纯黑、四色常量 → `engine/theme.py`
- 标题 / 代码 / 状态 / 提示的位置 → `AlgoScene` 的类属性
- 节点宽度、行距、叶子展开范围 → `TREE_BOX`

只有**这期内容和默认布局打架**时才覆写，例如二分查找：

```python
    # 代码行较长，面板会自动缩小字号，中心相应右移一点
    CODE_CENTER = (-4.60, 1.05)
    STATUS_CENTER = (-4.60, -1.05)
```

---

## 六、§11 分镜 → 一段一个方法

PRD §11 分了几段，代码就分几个方法，方法名直接叫 `scene_xxx`：

```python
    def build(self):
        self.tree = self.add_tree(self.spec)
        self.scene_intro()          # §11 场景一
        self.scene_rules()          # §11 场景二
        self.scene_search()         # §11 场景三
        self.scene_conclusion()     # §11 场景四
```

**这样做的好处**：改节奏只要动一段，不影响别处；时长超预算时也知道该砍哪段。

每段里的 `run_time=` 和 `self.wait()` 对着 PRD §11 的"停留多久"填。
拿不准就用引擎上挂的节奏常量：

```python
self.play(..., run_time=self.FIRST.run_time)   # 首次出现的关键规则
self.wait(self.FIRST.hold)
```

---

## 七、§8 和 §12 不写进代码

**§8 正确性基准**和 **§12 验收清单**是给**渲染之后**用的：

- 先按 §8 核对最终值、中间状态、操作次数对不对
- 再按 §12 逐条看画面（配色、排版、节奏、有没有文字截断）

这一步不能省。光看源码参数看不出效果 —— 二分查找简洁版第一版就是渲染完
截图才发现代码块被左边界截断了。

---

## 完整的一遍

以"想加一期冒泡排序"为例：

```
1. cp PRD_TEMPLATE.md examples/bubble_sort/README.md
2. 填 §6~§11：先写死一个 6 元素的小数组，手工跑一遍记录每轮的比较与交换
3. 把 §7 的代码贴成 CODE_SOURCE，数好行号
4. 把 §9.1 的事件表翻译成 build() 里的双重循环
5. §9.2 的每个动作挑对应原语（compare / swap / hit）
6. python tools/render.py examples/bubble_sort/scene.py
7. 按 §12 验收，不对就回去改对应的那一段
```

第 2 步是**最花时间也最不能省**的：执行记录错了，后面画得再好看也是错的。
