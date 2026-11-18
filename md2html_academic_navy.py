# -*- coding: utf-8 -*-
"""COBOL入門編.md → COBOL入門編_AcademicNavy.html 変換（Academic Navy デザイン）"""
import re
import pathlib
import markdown

SRC = pathlib.Path("COBOL入門編.md")
DST = pathlib.Path("COBOL入門編_AcademicNavy.html")

def slugify_jp(value: str, separator: str) -> str:
    # GitHub 風スラッグ: 小文字化、句読点・括弧等を除去、空白→separator
    v = value.lower()
    v = re.sub(r"[^\w—-]+", " ", v)
    v = re.sub(r"\s+", separator, v.strip())
    v = re.sub(rf"{separator}+", separator, v)
    v = re.sub(rf"{separator}(—)", r"\1", v)  # 「— スペース」→ em-dash 直結（MD側アンカー様式に合わせる）
    v = re.sub(rf"(—){separator}", r"\1", v)
    v = re.sub(rf"^({separator})|({separator})$", "", v)
    return v

md = markdown.Markdown(
    extensions=["tables", "fenced_code", "toc", "sane_lists"],
    extension_configs={"toc": {"slugify": slugify_jp, "separator": "-", "toc_depth": "2-3"}},
)
body = md.convert(SRC.read_text(encoding="utf-8"))

# 既存MDアンカーとの残不一致をファジー照合で書き換え
def norm(s: str) -> str:
    return re.sub(r"[-—_\s]", "", s)

ids = re.findall(r'<h[1-6] id="([^"]+)"', body)
norm_map = {norm(i): i for i in ids}

def fix_anchor(m):
    href = m.group(1)
    if href in ids:
        return m.group(0)
    import urllib.parse
    dec = urllib.parse.unquote(href)
    tgt = norm_map.get(norm(dec))
    if not tgt:
        # 末尾の重複サフィックス違い (例: 1-形式 vs 1-形式-1) も試す
        base = re.sub(r"-\d+$", "", dec)
        cands = [i for i in ids if norm(i).startswith(norm(base))]
        tgt = cands[0] if len(cands) == 1 else None
    if tgt:
        return f'href="#{urllib.parse.quote(tgt)}"'
    return m.group(0)

body = re.sub(r'href="#([^"]+)"', fix_anchor, body)

# mermaid ブロックはコード表示ではなく図としてレンダリングさせる div に変換
import html as _html
body = re.sub(
    r'<pre><code class="language-mermaid">(.*?)</code></pre>',
    lambda m: f'<div class="mermaid">{_html.unescape(m.group(1))}</div>',
    body, flags=re.S,
)

CSS = """
:root{
  --cream:#F7F3E8; --cream-2:#F1ECDD; --paper:#FDFBF4;
  --ink:#232A33; --ink-soft:#4A5260;
  --navy:#1D3A5F; --navy-deep:#152B47; --navy-soft:#3E5C82;
  --line:#CFC7B2; --line-soft:#E0D9C6; --accent:#8C6A2F;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0; background:var(--cream); color:var(--ink);
  font-family:"Noto Serif JP","Shippori Mincho","Yu Mincho",serif;
  font-size:16px; line-height:1.9;
}
a{color:var(--navy-soft); text-decoration:none}
a:hover{color:var(--navy-deep); text-decoration:underline}

/* ===== 本文（幅制限なし） ===== */
main{
  padding:56px 64px 120px; min-width:0;
}
main>h1:first-of-type{
  margin:0 0 8px; font-size:42px; letter-spacing:.08em; color:var(--navy-deep); font-weight:700;
}
.subtitle{
  font-size:13px; letter-spacing:.25em; color:var(--accent);
  text-transform:uppercase; margin-bottom:10px;
}
h1{border-bottom:3px double var(--navy); padding-bottom:18px}

/* 章（h2）: ネイビーの帯 */
main h2{
  margin:3.4em 0 1.2em; padding:16px 22px;
  background:var(--navy); color:#F5F0DF;
  font-size:26px; letter-spacing:.05em; font-weight:600;
  border-left:8px solid var(--accent);
  scroll-margin-top:20px;
}
main h2 .toc-link, main h3 .toc-link, main h4 .toc-link{color:inherit; text-decoration:none}

/* 節（h3）: 左ボーダー */
main h3{
  margin:2.6em 0 1em; padding:2px 0 8px 16px;
  border-left:5px solid var(--navy); border-bottom:1px solid var(--line);
  font-size:21px; color:var(--navy-deep); font-weight:700;
  scroll-margin-top:20px;
}
/* 小節（h4）: 弱い帯 */
main h4{
  margin:2.2em 0 .8em; padding:8px 14px;
  background:var(--cream-2); border:1px solid var(--line-soft); border-left:4px solid var(--navy-soft);
  font-size:17px; color:var(--navy); font-weight:700;
  scroll-margin-top:20px;
}
main h5{margin:1.8em 0 .6em; font-size:16px; color:var(--navy-deep)}

p{margin:0 0 1em}
strong{color:var(--navy-deep)}
hr{border:0; border-top:1px solid var(--line); margin:2.5em 0}

/* ===== コード ===== */
code{
  font-family:"Sarasa Mono SC","Consolas","Courier New",monospace;
  background:var(--cream-2); color:var(--navy-deep);
  padding:.12em .45em; border:1px solid var(--line-soft); font-size:.92em;
}
pre{
  background:var(--navy-deep); color:#E9E4D3;
  padding:18px 24px; overflow-x:auto; line-height:1.7;
  border-top:3px solid var(--accent);
  box-shadow:0 2px 10px rgba(21,43,71,.15);
}
pre code{
  background:transparent; color:inherit; border:0; padding:0; font-size:14px;
  white-space:pre;
}

/* ===== テーブル ===== */
table{
  border-collapse:collapse; width:100%; margin:1.4em 0 2em;
  background:var(--paper); font-size:14.5px; line-height:1.7;
}
th,td{border:1px solid var(--line); padding:9px 14px; vertical-align:top; text-align:left}
thead th{background:var(--navy); color:#F5F0DF; font-weight:600; letter-spacing:.04em; border-color:var(--navy-deep)}
tbody tr:nth-child(even){background:var(--cream-2)}
caption{caption-side:top; text-align:left; color:var(--ink-soft); font-size:13px; padding-bottom:6px}

blockquote{
  margin:1.4em 0; padding:12px 22px; background:var(--paper);
  border-left:5px solid var(--accent); color:var(--ink-soft);
}
ul,ol{margin:0 0 1.2em; padding-left:1.6em}
li{margin:.25em 0}

/* ===== 図（mermaid） ===== */
.mermaid{
  background:var(--paper); border:1px solid var(--line-soft); border-top:3px solid var(--accent);
  padding:24px 16px; margin:1.4em 0 2em; text-align:center; overflow-x:auto;
}
.mermaid:not([data-processed]){font-family:monospace; white-space:pre; text-align:left; font-size:13px; color:var(--ink-soft)}

/* ===== フッター ===== */
footer{
  padding:24px 64px; border-top:1px solid var(--line);
  color:var(--ink-soft); font-size:12px; letter-spacing:.08em;
}
@media print{ pre{box-shadow:none} }
"""

HTML = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>COBOL入門編</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<main>
{body}
</main>
<script>
// 本文内のアンカーリンクはスムーズスクロール
document.querySelectorAll('main a[href^="#"]').forEach(a=>{{
  a.addEventListener('click',e=>{{
    const t=document.getElementById(decodeURIComponent(a.hash.slice(1)));
    if(t){{e.preventDefault(); t.scrollIntoView({{behavior:'smooth'}}); history.replaceState(null,'',a.hash);}}
  }});
}});
</script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
mermaid.initialize({{
  startOnLoad: true, securityLevel: 'loose', theme: 'base',
  themeVariables: {{
    fontFamily: '"Noto Serif JP","Yu Mincho",serif',
    background: '#FDFBF4',
    primaryColor: '#F1ECDD', primaryTextColor: '#232A33', primaryBorderColor: '#1D3A5F',
    secondaryColor: '#E7DFC9', tertiaryColor: '#FDFBF4',
    lineColor: '#3E5C82',
    titleColor: '#152B47', edgeLabelBackground: '#F7F3E8'
  }},
  flowchart: {{ curve: 'basis', padding: 12 }}
}});
</script>
</body>
</html>
"""

DST.write_text(HTML, encoding="utf-8")
print(f"OK -> {DST} ({DST.stat().st_size:,} bytes)")
