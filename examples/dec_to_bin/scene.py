"""十进制转二进制 —— 最简单的递归示例。

演示最简单的单支递归：一路把 n 除以 2 递到边界，再一层层往回拼字符串。
整个调用链是一条竖线，4 次调用，适合作为"递归与回溯"的入门片。

运行：
    manimgl examples/dec_to_bin/scene.py DecToBin -w
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = _HERE
while not os.path.isdir(os.path.join(_ROOT, "engine")):
    _parent = os.path.dirname(_ROOT)
    if _parent == _ROOT:
        break
    _ROOT = _parent
sys.path.insert(0, _ROOT)

from manimlib import *                                    # noqa: E402

from engine import AlgoScene, TreeSpec, curtain, theme    # noqa: E402

N = 13
BITS = "1101"

# 由 tools/trace.py 从 dec_to_bin.py 导出：单支递归，四次调用
NODES = (
    (1, "dec2bin(13)", 0, None),
    (2, "dec2bin(6)", 1, 1),
    (3, "dec2bin(3)", 2, 2),
    (4, "dec2bin(1)", 3, 3),
)
CHILDREN = {1: (2,), 2: (3,), 3: (4,)}
LEAF_ORDER = (4,)

# 每次调用往回拼出来的串
RETURNED = {4: "1", 3: "11", 2: "110", 1: "1101"}


class DecToBin(AlgoScene):
    TITLE_TEXT = "十进制转二进制"
    TITLE_TAG = f"n = {N}"

    CODE_SOURCE = (
        "string dec2bin(int n) {",
        "    if (n < 2) return to_string(n);",
        "    return dec2bin(n / 2) + to_string(n % 2);",
        "}",
    )

    CODE_CENTER = (-5.00, 1.00)
    STATUS_CENTER = (-5.00, -1.30)

    def setup(self):
        self.spec = TreeSpec(NODES, CHILDREN, LEAF_ORDER)

    def build(self):
        self.tree = self.add_tree(self.spec)
        self.scene_intro()
        self.scene_walk()
        self.scene_wrapup()

    # ------------------------------------------------------------ 场景
    def scene_intro(self):
        self.add_title(run_time=0.28)
        self.add_code(run_time=0.48)
        self.code.bind(base=1, rec=2)
        self.code.focus_now("base")
        self.add_status()
        self.add_hint()
        self.tree.root(run_time=0.32)
        self.status.set(f"dec2bin({N})", run_time=0.20)
        self.hint.set("先一路除以 2，递到边界", run_time=0.26)
        self.wait(0.30)

    def scene_walk(self):
        # 下降：13 → 6 → 3 → 1
        for nid in (2, 3):
            self.code.focus(self, "rec", run_time=0.14)
            self.tree.enter(nid, run_time=0.26)
            self.status.set(self.spec.label[nid], run_time=0.16)
        self.code.focus(self, "base", run_time=0.14)
        self.tree.enter(4, run_time=0.24)
        self.status.set("dec2bin(1)    n < 2，返回", run_time=0.18)
        self.wait(0.25)

        # 边界：1 的二进制就是 "1"
        self.hint.set("到达边界，开始往回拼", run_time=0.24)
        self.tree.return_value(4, '="1"', hold=0.50)
        self.status.set('dec2bin(3)    1 + 1', run_time=0.18)

        # 回溯：每层把"商的二进制作"接上"自己的余数"
        for nid, quotient, remainder in ((3, "1", "1"), (2, "11", "0")):
            self.code.focus(self, "rec", run_time=0.14)
            self.status.set(f'{self.spec.label[nid]}    "{quotient}" + "{remainder}"',
                            run_time=0.20)
            self.wait(0.28)
            self.tree.return_value(nid, f'="{RETURNED[nid]}"', hold=0.42)

        # 根调用
        self.code.focus(self, "rec", run_time=0.14)
        self.status.set(f'dec2bin({N})    "110" + "1"', run_time=0.20)
        self.wait(0.30)
        self.tree.return_value(1, f'="{BITS}"', hold=0.50)
        self.wait(0.25)

    def scene_wrapup(self):
        self.hint.set("商继续除以 2，余数从低位到高位拼起来", run_time=0.28)
        self.code.hide(self, run_time=0.26)
        self.status.clear(run_time=0.16)
        self.hint.clear(run_time=0.16)
        curtain(self, run_time=0.28)

        result = Text(f"{N} → {BITS}", font=theme.mono_font(),
                      font_size=theme.SIZE_RESULT, color=theme.GREEN)
        result.move_to(np.array([0.0, 0.35, 0.0]))
        note = Text("4 次调用，递归深度 4", font=theme.chinese_font(),
                    font_size=26, color=theme.WHITE)
        note.move_to(np.array([0.0, -0.60, 0.0]))

        self.play(FadeIn(result, shift=UP * 0.10), run_time=0.40)
        self.play(FadeIn(note, shift=UP * 0.08), run_time=0.34)
        self.wait(1.60)
