# 通用递归场景模板

当前参考为 `3163.mp4`。所有递归动画共用同一套执行状态表达，不预设两个分支或求和。

## 默认实现

- `CodePanel.focus()`：当前代码文字与侧边光标蓝色，旧语句恢复白色；可传连续多行的列表。原位改色，不叠加代码副本。透明行框保留原始缩进。
- `HintLine`：字幕按整幅画面底部居中，1080p 字形目标约 46px，中心约 `(960,1005)`。长句自动换为至多两行；超过两行必须拆成多条字幕，不压缩字号。
- `StackPanel`：代码下方左对齐，按实际代码底边避让。蓝色层级标题，下方按字段显示参数、局部变量、等待状态；新接收的返回值绿色。字段按实际字宽换行，纵向放不下时分页停留。
- `CallStack`：每一层独立保存现场；只允许栈顶出栈，返回后恢复调用者，结束时活动栈清空。
- `AlgoScene`：默认动作与停留按 PRD §3 的参考节奏取值。显式写死的 `run_time` 和 `wait` 仍需逐段调整，默认值不等于已经完成视频节奏验收。

## 自动生成

先准备真实 trace、展示用 C++ 和行号映射：

```bash
python tools/scaffold.py traces/fib.json --out examples/fibonacci_recursion/scene_gen.py --class FibonacciGen --title "非记忆化递归" --tag "fib(5)" --code examples/fibonacci_recursion/code.cpp --bindings examples/fibonacci_recursion/bindings.json --params n --receivers left,right
python tools/render.py examples/fibonacci_recursion/scene_gen.py --scene FibonacciGen
```

通用生成器不再使用 Fibonacci 的代码、`left/right` 或求和公式作为其他算法的默认值。`--code` 和 `--bindings` 必须显式提供；`--params` 是实参名称；`--receivers` 可选，只有真实接收子调用返回值的变量才填写。多分支可填写任意数量，未填写时只展示子调用返回数据。

映射中的行号从 0 开始：

| 字段 | 含义 |
|---|---|
| `enter` | 新调用入口位置 |
| `call` | 按子调用次序列出的调用语句；其中一项也可为多行列表 |
| `return` | 有子调用的调用实际返回的位置 |
| `leaf_return` | 没有子调用的调用实际返回的位置 |

不同调用若具有不同的条件分支/返回位置，不应强套上述默认映射：为对应事件填写 `line`，进入事件可填 `entry_line`，返回事件可填 `resume_line`。模板只记录真实调用与返回边界，不能自动推断中间的判断、循环、恢复现场和局部变量赋值。需要逐语句讲解时，必须扩展本期分镜，不能将边界模板宣称为完整逐语句追踪。

事件可补充 `locals`、`caption`；返回事件还可填 `receiver`。无返回值调用设置 `has_value: false`，若算法确实返回空值则显式设置 `has_value: true`。任何未被执行记录确认的局部变量都不得预填将来结果。

## 手写分镜

可复制 `templates/recursion_scene.py`，或继承 `AlgoScene` 自己组织细粒度事件：

```python
self.add_code()
self.add_hint()
panel = self.add_stack()
panel.push(1, "函数调用", params={"参数": "实参"}, locals={"局部量": "未赋值"})
self.code.focus(self, 2)
panel.update(state="等待子调用返回")
panel.push(2, "子调用", params={"参数": "子实参"})
# 按真实代码完成子调用，再返回：
panel.pop(2, value="真实结果", receiver="局部量")
# 此时恢复第 1 层自己的参数和局部量，不展示子调用的参数。
panel.pop(1, has_value=False)
```

字幕使用 `self.hint.set()`，然后按动作和阅读需要显式 `self.wait()`；组件换色本身不会自动插入阅读停留。共享/static 变量仍使用独立 `StaticPanel`，不能当作每帧独有局部变量。

## 兼容与验证

旧 `StatusLine` API 保留，供非递归及历史手写场景使用；它不会凭字符串自动推断递归栈。旧场景若覆写字幕位置、字号或节奏，仍需迁移到新模板。原手工 Fibonacci `scene.py` 保留，新默认生成范例为 `scene_gen.py`。

验证命令：`python -m unittest discover -s tests`、`python tools/selftest.py`、`python tools/check_env.py`。成片还需实际渲染并以 1 倍速检查字幕、代码、当前栈帧及返回阶段的节奏；缺少 ManimGL、字体或图形环境时，不能把数据层测试当作视觉验收。
