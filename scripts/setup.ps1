# 创建 .venv 并安装 manimgl，然后跑一次环境自检。
#
#   powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "找不到 python，请先安装 Python 3.9 以上版本（勾选 Add to PATH）"
    exit 1
}

Write-Host "== 解释器：$(python --version 2>&1) =="

if (-not (Test-Path ".venv")) {
    Write-Host "== 创建 .venv =="
    python -m venv .venv
}

$VenvPy = ".venv\Scripts\python.exe"

Write-Host "== 安装依赖（会下载若干包）=="
& $VenvPy -m pip install --upgrade pip
& $VenvPy -m pip install -r requirements.txt

Write-Host ""
Write-Host "== 环境自检 =="
& $VenvPy tools\check_env.py
$check = $LASTEXITCODE

Write-Host ""
if ($check -eq 0) {
    Write-Host "后续渲染："
    Write-Host "    $VenvPy tools\render.py examples\binary_search\scene.py"
} else {
    Write-Host "自检有未通过项，按上面的提示补齐后再渲染。"
}
