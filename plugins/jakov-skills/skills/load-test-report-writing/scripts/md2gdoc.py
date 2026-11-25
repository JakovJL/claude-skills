"""Convert a small markdown subset into inline-styled HTML for Google Docs import.

Supported: # / ## / ### headings, paragraphs, **bold**, `code`, [text](url), bullet lists (2 levels, 2 or 4 space
indent), numbered lists, pipe tables (first row = header, columns whose separator ends with ':' are right-aligned),
verdict words coloured in table cells.
Usage: python -I <skill folder>/scripts/md2gdoc.py in.md out.html   (part of the global load-test-report-writing skill)
"""
import html
import re
import sys

FONT = "Arial"
TEXT = "#202124"
MUTED = "#5f6368"
BORDER = "#dadce0"
HEAD_BG = "#f1f3f4"
VERDICT = {
    "Held, no slowdowns": "#188038",
    "Held with slowdowns": "#b06000",
    "Failed": "#c5221f",
}


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", lambda m: f"<span style=\"font-family:'Roboto Mono';font-size:9pt;color:{TEXT}\">{m.group(1)}</span>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" style="color:#1a73e8">\1</a>', s)
    return s


PAGE_PT = 468  # Letter, 1" margins


def col_widths(rows):
    """Width per column in pt: short body cells (<= 14 chars, e.g. '0.24 s', 'COURSE10236') never wrap, header cells
    may wrap at spaces; the rest of the page width goes to columns with longer text."""
    pad = 12

    def pt(s):  # Arial 8.5 pt: capitals are wider than digits and lower case
        return sum(5.8 if ch.isupper() else 4.8 for ch in s)

    mins, typical = [], []
    for j in range(len(rows[0])):
        head = re.sub(r"[`*]", "", rows[0][j]).strip()
        body = [re.sub(r"[`*]", "", r[j]).strip() for r in rows[1:] if j < len(r)]
        units = [pt(w) for w in head.split()] + [pt(c) if len(c) <= 14 else max(pt(w) for w in c.split()) for c in body if c]
        mins.append(min(max(units, default=1), 220) + pad)  # a very long token (a folder name) wraps anyway
        typical.append(min(max((len(c) for c in body), default=1), 40))
    if sum(mins) >= PAGE_PT:
        return [round(PAGE_PT * m / sum(mins)) for m in mins]
    extra = PAGE_PT - sum(mins)
    return [round(m + extra * t / sum(typical)) for m, t in zip(mins, typical)]


def cell_html(text, tag, align, width=None):
    content = inline(text.strip())
    color = VERDICT.get(text.strip())
    if color:
        content = f'<span style="color:{color};font-weight:bold">{content}</span>'
    base = f"border:1px solid {BORDER};padding:3pt 5pt;font-size:8.5pt;vertical-align:top;text-align:{align};"
    if width:
        base += f"width:{width}pt;"
    if tag == "th":
        base += f"background-color:{HEAD_BG};font-weight:bold;"
        content = content.replace("<b>", "").replace("</b>", "")
    return f'<{tag} style="{base}">{content}</{tag}>'


def table(lines):
    rows = [[c for c in l.strip().strip("|").split("|")] for l in lines]
    sep = rows[1]
    aligns = ["right" if c.strip().endswith(":") else "left" for c in sep]
    body = [rows[0]] + rows[2:]
    widths = col_widths(body)
    out = [f'<table style="border-collapse:collapse;width:{PAGE_PT}pt;margin:4pt 0 10pt 0">',
           "<colgroup>" + "".join(f'<col style="width:{w}pt">' for w in widths) + "</colgroup>"]
    for i, r in enumerate(body):
        tag = "th" if i == 0 else "td"
        cells = "".join(cell_html(c, tag, "left" if tag == "th" else aligns[j], widths[j]) for j, c in enumerate(r))
        out.append(f'<tr style="page-break-inside:avoid">{cells}</tr>')
    out.append("</table>")
    out.append('<p style="margin:0;font-size:5pt;line-height:1">&nbsp;</p>')  # Google drops margins after a table
    return "\n".join(out)


def convert(md):
    out = []
    lines = md.replace("\r\n", "\n").split("\n")
    i = 0
    para = []

    def flush():
        if para:
            top = "10pt" if out and out[-1].endswith("</table>") else "0"
            out.append(f'<p style="margin:{top} 0 6pt 0">{inline(" ".join(para))}</p>')
            para.clear()

    while i < len(lines):
        l = lines[i]
        if not l.strip():
            flush(); i += 1; continue
        m = re.match(r"^(#{1,3}) (.*)$", l)
        if m:
            flush()
            n = len(m.group(1))
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
            i += 1; continue
        if l.lstrip().startswith("|"):
            flush()
            block = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                block.append(lines[i]); i += 1
            out.append(table(block)); continue
        if re.match(r"^\s*([-*]|\d+\.) ", l):
            flush()
            stack = []  # [indent, tag, li_open]
            while i < len(lines) and (re.match(r"^\s*([-*]|\d+\.) ", lines[i]) or (lines[i].startswith("    ") and lines[i].strip() and stack)):
                cur = lines[i]
                mm = re.match(r"^(\s*)([-*]|\d+\.) (.*)$", cur)
                if not mm:  # continuation paragraph inside the open list item
                    out.append(f'<p style="margin:2pt 0 4pt 0">{inline(cur.strip())}</p>')
                    i += 1; continue
                indent = 1 if len(mm.group(1)) >= 2 else 0
                tag = "ol" if mm.group(2)[0].isdigit() else "ul"
                while stack and stack[-1][0] > indent:
                    lvl = stack.pop()
                    out.append(("</li>" if lvl[2] else "") + f"</{lvl[1]}>")
                if stack and stack[-1][0] == indent and stack[-1][1] != tag:
                    lvl = stack.pop()
                    out.append(("</li>" if lvl[2] else "") + f"</{lvl[1]}>")
                if stack and stack[-1][0] == indent and stack[-1][2]:
                    out.append("</li>")
                    stack[-1][2] = False
                if not stack or stack[-1][0] < indent:
                    out.append(f'<{tag} style="margin:0 0 7pt 0">')
                    stack.append([indent, tag, False])
                out.append(f'<li style="margin:0 0 2pt 0">{inline(mm.group(3))}')
                stack[-1][2] = True
                i += 1
            while stack:
                lvl = stack.pop()
                out.append(("</li>" if lvl[2] else "") + f"</{lvl[1]}>")
            continue
        para.append(l.strip()); i += 1
    flush()
    body = "\n".join(out)
    return (f'<html><head><meta charset="utf-8"></head>'
            f'<body style="font-family:{FONT};font-size:10pt;line-height:1.15;color:{TEXT}">\n{body}\n</body></html>')


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        md = f.read()
    with open(dst, "w", encoding="utf-8") as f:
        f.write(convert(md))
    print("ok", dst)
