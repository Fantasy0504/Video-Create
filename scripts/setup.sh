#!/usr/bin/env bash
# 创建 .venv 并安装 manimgl，然后跑一次环境自检。
#
#   bash scripts/setup.sh
#
# 想指定解释器：PYTHON=/path/to/python bash scripts/setup.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PY="${PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
    PY="python"
fi
if ! command -v "$PY" >/dev/null 2>&1; then
    echo "找不到 Python，请先安装 Python 3.9 以上版本"
    exit 1
fi

echo "== 解释器：$("$PY" --version 2>&1) =="

if [ ! -d ".venv" ]; then
    echo "== 创建 .venv =="
    "$PY" -m venv .venv
fi

if [ -x ".venv/bin/python" ]; then
    VENV_PY=".venv/bin/python"
else
    VENV_PY=".venv/Scripts/python.exe"
fi

echo "== 安装依赖（会下载若干包）=="
"$VENV_PY" -m pip install --upgrade pip
"$VENV_PY" -m pip install -r requirements.txt

echo
echo "== 环境自检 =="
# 自检失败不中断，让用户看到完整报告
"$VENV_PY" tools/check_env.py || true

echo
echo "后续渲染："
echo "    $VENV_PY tools/render.py examples/binary_search/scene.py"
