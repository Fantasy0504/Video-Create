"""按实际字宽换行；测量函数由渲染层提供，便于独立验证。"""
import re


def wrap_text(text, max_width, measure):
    if max_width <= 0:
        raise ValueError("文字区域宽度必须大于零")
    lines = []
    for paragraph in str(text).split("\n"):
        current = ""
        # 英文标识符尽量保持完整，中文允许逐字换行。
        tokens = re.findall(r"[A-Za-z_][A-Za-z_0-9]*(?:\([^\n()]*\))?|\d+(?:\.\d+)?|\s+|[^\s]", paragraph)
        for token in tokens:
            if measure(token.strip()) > max_width:
                raise ValueError(f"完整字段过宽，请调整文字区域或拆分说明：{token!r}")
            candidate = current + token
            if current and measure(candidate.rstrip()) > max_width:
                lines.append(current.rstrip())
                current = token.lstrip()
            else:
                current = candidate.lstrip() if not current else candidate
        lines.append(current.rstrip())
    return lines
