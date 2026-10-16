#!/usr/bin/env python3
"""从真实调用事件生成 RecursionScene；不猜算法代码、变量名或结果合并方式。"""
from __future__ import annotations
import argparse
import json
import keyword
from pathlib import Path
from pprint import pformat

ROOT = Path(__file__).resolve().parent.parent


def build_source(payload, class_name, title, tag, code, source_json,
                 bindings=None, param_names=(), receivers=()):
    if not class_name.isidentifier() or keyword.iskeyword(class_name):
        raise ValueError("场景类名必须是有效 Python 标识符")
    if not code:
        raise ValueError("必须提供真实 C++ 展示代码，不能用斐波那契代码占位")
    if not bindings:
        raise ValueError("必须提供事件与 C++ 行号映射；调用记录无法推断具体执行语句")
    return f'''"""{title!r}；从 {source_json!r} 自动生成。

模板只复现调用/返回边界；判断、循环、局部变量更新、回溯撤销等语句
请在本期分镜中细化，或在事件上补充 line/entry_line/resume_line/locals。
trace 不记录的局部值不得凭空推断。
"""
import sys
from pathlib import Path

_ROOT = next(p for p in Path(__file__).resolve().parents if (p / "engine").is_dir())
sys.path.insert(0, str(_ROOT))
from engine import RecursionScene


class {class_name}(RecursionScene):
    TITLE_TEXT = {title!r}
    TITLE_TAG = {tag!r}
    CODE_SOURCE = {tuple(code)!r}
    CODE_LINES = {bindings!r}
    PARAM_NAMES = {tuple(param_names)!r}
    RECEIVERS = {tuple(receivers)!r}
    TRACE = {pformat(payload, width=100, sort_dicts=False)}
'''


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace_json')
    parser.add_argument('--out', required=True)
    parser.add_argument('--class', dest='class_name', required=True)
    parser.add_argument('--title', default='算法演示')
    parser.add_argument('--tag', default='')
    parser.add_argument('--code', required=True, help='真实 C++ 文件')
    parser.add_argument('--bindings', required=True, help='事件到 0-based C++ 行号的 JSON 映射文件')
    parser.add_argument('--params', default='', help='实参名称，逗号分隔；不填时显示参数1等')
    parser.add_argument('--receivers', default='', help='按分支顺序填写真实接收变量；不填时只显示返回数据')
    opts = parser.parse_args(argv)
    def path(value):
        p = Path(value)
        return p if p.is_absolute() else ROOT / p
    payload = json.loads(path(opts.trace_json).read_text(encoding='utf-8'))
    code = path(opts.code).read_text(encoding='utf-8').splitlines()
    bindings = json.loads(path(opts.bindings).read_text(encoding='utf-8'))
    names = lambda value: tuple(v.strip() for v in value.split(',') if v.strip())
    source = build_source(payload, opts.class_name, opts.title, opts.tag, code,
                          Path(opts.trace_json).name, bindings,
                          names(opts.params), names(opts.receivers))
    output = path(opts.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(source, encoding='utf-8')
    print(f'已生成 {output}；请核对代码映射并补充分镜，再按 PRD 原速验收。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
