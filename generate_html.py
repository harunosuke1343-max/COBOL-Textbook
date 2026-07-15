#!/usr/bin/env python3
"""
COBOL入門編 PDF → HTML 変換スクリプト
66枚のページ画像を Claude Vision API で処理して単一 HTML ファイルを生成する。
進捗は _html_progress.json に保存するため、中断・再開が可能。
"""

import anthropic
import base64
import json
import os
import sys
from pathlib import Path

IMAGE_DIR  = Path("COBOL入門編_ページ画像")
OUTPUT_HTML = Path("COBOL入門編.html")
PROGRESS_FILE = Path("_html_progress.json")
TOTAL_PAGES = 66
MODEL = "claude-sonnet-4-6"

client = anthropic.Anthropic()


def encode_image(path: Path) -> str:
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


PAGE_PROMPT = """\
このCOBOL教材（スキャンPDF）のページを、HTMLフラグメントとして正確に再現してください。

【出力仕様】
- 出力は <div class="page" data-page="{page_num}"> … </div> のみ（DOCTYPE/html/head/body タグ不要）
- ページ右上や左上のヘッダー（章タイトル）があれば <p class="page-header"> で出力
- 見出しは <h2>/<h3>/<h4> で階層を表現
- 本文は <p> タグ
- COBOLコードや端末コマンドは <pre><code class="cobol">…</code></pre>
- 表は <table class="data-table"><thead><tr><th>…</th></tr></thead><tbody>…</tbody></table>
- フローチャート・PAD図・図解は SVG または ASCII art を <figure class="diagram"><figcaption>…</figcaption>…</figure> に格納
  - フローチャートは箱と矢印を SVG で描くか、あるいは HTML の <div class="fc-…"> 構造で表現
  - PAD図は入れ子の <div class="pad-…"> 構造で表現
- ページ番号は <p class="page-num"> で出力（例: <p class="page-num">－ 1 －</p>）
- 記号 △ はスペース記号として扱い &thinsp; または △ のまま出力
- 日本語テキストは省略せず全文出力

ページ番号: {page_num}
"""


def process_page(page_num: int) -> str:
    img_path = IMAGE_DIR / f"page_{page_num:03d}.png"
    if not img_path.exists():
        return f'<div class="page" data-page="{page_num}"><p class="error">画像なし: {img_path}</p></div>'

    image_data = encode_image(img_path)
    prompt = PAGE_PROMPT.format(page_num=page_num)

    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_data,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )
    return message.content[0].text


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_progress(progress: dict) -> None:
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


CSS = """
/* ===== Reset ===== */
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }

/* ===== Fonts & Base ===== */
body {
  font-family: "Hiragino Mincho ProN", "Yu Mincho", "Noto Serif JP", "MS Mincho", serif;
  background: #f7f6f2;
  color: #1a1a1a;
  font-size: 15px;
  line-height: 1.9;
}

/* ===== Layout ===== */
.wrapper { display: flex; min-height: 100vh; }

/* ===== Sidebar ===== */
nav#toc {
  position: fixed;
  top: 0; left: 0;
  width: 240px; height: 100vh;
  background: #1c2340;
  overflow-y: auto;
  padding: 1.5rem 0;
  z-index: 100;
  font-family: "Hiragino Sans", "Meiryo", sans-serif;
}
nav#toc::-webkit-scrollbar { width: 3px; }
nav#toc::-webkit-scrollbar-thumb { background: #445; }
nav#toc .toc-title {
  color: #a0aac0;
  font-size: .72rem;
  letter-spacing: .2em;
  padding: .5rem 1.4rem 1rem;
  text-transform: uppercase;
}
nav#toc a {
  display: block;
  color: #c8d0e0;
  text-decoration: none;
  font-size: .82rem;
  padding: .38rem 1.4rem;
  border-left: 3px solid transparent;
  transition: background .15s, color .15s, border-color .15s;
}
nav#toc a:hover, nav#toc a.active {
  background: rgba(255,255,255,.07);
  color: #e8f0ff;
  border-left-color: #6b8cff;
}
nav#toc .toc-section { padding-left: 2.8rem; font-size: .75rem; }

/* ===== Main ===== */
main {
  margin-left: 240px;
  padding: 0;
  flex: 1;
}

/* ===== Cover ===== */
.cover-page {
  background: linear-gradient(145deg, #0d1b3e 0%, #1a2f6e 50%, #233a8a 100%);
  color: #fff;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.cover-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 60% 40%, rgba(100,140,255,.15) 0%, transparent 65%);
}
.cover-inner { position: relative; z-index: 1; }
.cover-inner .cover-title { font-size: 3.5rem; letter-spacing: .3em; font-weight: 300; }
.cover-inner .cover-sub { font-size: 1.4rem; margin-top: .3em; letter-spacing: .2em; color: #aac0ff; }
.cover-inner .cover-meta { margin-top: 3rem; font-size: .85rem; color: #8898cc; line-height: 2.2; }
.cover-silhouette { font-size: 8rem; margin: 2rem 0; opacity: .18; }

/* ===== Page wrapper ===== */
.page {
  max-width: 860px;
  margin: 0 auto;
  padding: 3.5rem 4rem 4.5rem;
  border-bottom: 1px solid #e0ddd4;
}
.page:last-child { border-bottom: none; }

/* ===== Page header (chapter label) ===== */
.page-header {
  font-family: "Hiragino Sans", "Meiryo", sans-serif;
  font-size: .72rem;
  color: #999;
  letter-spacing: .18em;
  text-transform: uppercase;
  margin-bottom: 2.5rem;
  border-bottom: 1px solid #e5e0d8;
  padding-bottom: .5rem;
}

/* ===== Page number ===== */
.page-num {
  text-align: center;
  color: #aaa;
  font-size: .78rem;
  margin-top: 3rem;
  letter-spacing: .1em;
}

/* ===== Headings ===== */
h2 {
  font-size: 1.45rem;
  font-weight: 700;
  margin: 2.5rem 0 1rem;
  padding-bottom: .4rem;
  border-bottom: 2px solid #2c3e7a;
  color: #1a2a5e;
  letter-spacing: .04em;
}
h3 {
  font-size: 1.12rem;
  font-weight: 700;
  margin: 2rem 0 .7rem;
  color: #1a3060;
  border-left: 4px solid #4a6abf;
  padding-left: .7rem;
}
h4 {
  font-size: .97rem;
  font-weight: 700;
  margin: 1.5rem 0 .5rem;
  color: #2a3a70;
}

/* ===== Paragraph ===== */
p { margin-bottom: .9rem; }

/* ===== Code / Pre ===== */
pre {
  background: #f0eeea;
  border: 1px solid #ddd8ce;
  border-left: 4px solid #4a6abf;
  border-radius: 4px;
  padding: 1.1rem 1.4rem;
  margin: 1.2rem 0;
  overflow-x: auto;
  font-family: "Source Code Pro", "Consolas", "Courier New", monospace;
  font-size: .82rem;
  line-height: 1.7;
  color: #1a1a1a;
  white-space: pre;
}
code { font-family: "Source Code Pro", "Consolas", monospace; font-size: .85em; }
p code, li code {
  background: #eae8e2;
  padding: .1em .35em;
  border-radius: 3px;
  font-size: .84em;
}

/* ===== Tables ===== */
.data-table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.4rem 0;
  font-size: .88rem;
}
.data-table th {
  background: #2c3e7a;
  color: #fff;
  padding: .6rem .9rem;
  text-align: left;
  font-weight: 600;
  font-size: .82rem;
  letter-spacing: .04em;
}
.data-table td {
  padding: .55rem .9rem;
  border-bottom: 1px solid #ddd8ce;
  vertical-align: top;
}
.data-table tr:nth-child(even) td { background: #f7f5f0; }
.data-table tr:hover td { background: #edeae3; }

/* ===== Lists ===== */
ul, ol { padding-left: 1.6rem; margin-bottom: .9rem; }
li { margin-bottom: .3rem; }

/* ===== Figures / Diagrams ===== */
figure.diagram {
  margin: 1.8rem 0;
  padding: 1.4rem;
  background: #fff;
  border: 1px solid #ddd8ce;
  border-radius: 6px;
  overflow-x: auto;
}
figcaption {
  font-size: .8rem;
  color: #777;
  margin-top: .8rem;
  text-align: center;
  font-style: italic;
}

/* ===== Flowchart CSS helpers ===== */
.fc-box {
  display: inline-block;
  border: 1.5px solid #2c3e7a;
  background: #fff;
  padding: .3em .8em;
  border-radius: 3px;
  font-size: .8rem;
  margin: .15em;
  text-align: center;
  min-width: 80px;
}
.fc-diamond {
  display: inline-block;
  width: 90px; height: 90px;
  background: #fff;
  border: 1.5px solid #2c3e7a;
  transform: rotate(45deg);
  margin: .6em;
}
.fc-diamond-inner {
  transform: rotate(-45deg);
  display: flex; align-items: center; justify-content: center;
  width: 100%; height: 100%;
  font-size: .72rem;
  text-align: center;
  padding: .2em;
}
.fc-terminal {
  display: inline-block;
  border: 1.5px solid #2c3e7a;
  background: #2c3e7a;
  color: #fff;
  padding: .3em 1.2em;
  border-radius: 20px;
  font-size: .8rem;
  margin: .15em;
}
.fc-arrow { text-align: center; font-size: 1.1rem; color: #555; margin: .2em 0; }

/* ===== PAD diagram ===== */
.pad-block {
  border: 1.5px solid #2c3e7a;
  margin-bottom: 0;
}
.pad-label {
  background: #e8edf8;
  padding: .25rem .6rem;
  font-size: .8rem;
  font-weight: 600;
  border-bottom: 1.5px solid #2c3e7a;
}
.pad-body {
  display: flex;
}
.pad-seq {
  padding: .25rem .6rem;
  font-size: .78rem;
  border-right: 1.5px solid #2c3e7a;
  min-width: 120px;
}
.pad-nest {
  border-left: 1.5px solid #2c3e7a;
  flex: 1;
}

/* ===== Horizontal rule ===== */
hr { border: none; border-top: 1px solid #e0ddd4; margin: 3rem 0; }

/* ===== Table of contents page ===== */
.toc-page h2 { font-size: 1.2rem; margin-bottom: 1.5rem; }
.toc-page .toc-entry {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: .3rem 0;
  border-bottom: 1px dotted #ccc;
  font-size: .9rem;
}
.toc-page .toc-entry a { text-decoration: none; color: inherit; }
.toc-page .toc-entry a:hover { color: #2c3e7a; }
.toc-page .toc-indent { padding-left: 1.5rem; }

/* ===== Print ===== */
@media print {
  nav#toc { display: none; }
  main { margin-left: 0; }
  .page { border: none; page-break-after: always; }
}

/* ===== Responsive ===== */
@media (max-width: 800px) {
  nav#toc { display: none; }
  main { margin-left: 0; }
  .page { padding: 2rem 1.5rem; }
}
"""

JS = """
// ===== Active TOC link tracking =====
(function() {
  const links = document.querySelectorAll('nav#toc a[data-page]');
  const pages = Array.from(document.querySelectorAll('.page[data-page]'));

  function update() {
    const scrollY = window.scrollY + window.innerHeight * 0.25;
    let current = null;
    for (const page of pages) {
      if (page.offsetTop <= scrollY) current = page;
    }
    if (!current) return;
    const num = current.dataset.page;
    links.forEach(a => a.classList.toggle('active', a.dataset.page === num));
  }

  window.addEventListener('scroll', update, { passive: true });
  update();
})();
"""

SIDEBAR_CHAPTERS = [
    ("表紙・目次", [1, 2, 3]),
    ("第一章　概説", [4, 5, 6]),
    ("第二章　IDENTIFICATION", [7, 8]),
    ("第三章　ENVIRONMENT", [9, 10, 11, 12, 13, 14]),
    ("第四章　DATA", [15, 16, 17, 18, 19, 20, 21, 22]),
    ("第五章　PROCEDURE", [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]),
    ("第六章　フロー例", [38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49]),
    ("第七章　TSO", [50, 51, 52, 53, 54, 55, 56, 57]),
    ("第八章　PAD図", [58, 59, 60, 61, 62, 63, 64, 65, 66]),
]


def build_sidebar() -> str:
    items = []
    for chapter, pages in SIDEBAR_CHAPTERS:
        first = pages[0]
        items.append(f'<a href="#page-{first}" data-page="{first}">{chapter}</a>')
        for p in pages[1:]:
            items.append(f'<a class="toc-section" href="#page-{p}" data-page="{p}">p.{p}</a>')
    return "\n".join(items)


def assemble_html(progress: dict) -> None:
    pages_html_parts = []
    for page_num in range(1, TOTAL_PAGES + 1):
        key = str(page_num)
        fragment = progress.get(key, f'<div class="page" data-page="{page_num}"><p class="error">未処理ページ {page_num}</p></div>')
        # ensure the page div has an id for anchor links
        if f'id="page-{page_num}"' not in fragment:
            fragment = fragment.replace(
                f'data-page="{page_num}"',
                f'id="page-{page_num}" data-page="{page_num}"',
                1,
            )
        pages_html_parts.append(fragment)

    pages_html = "\n\n".join(pages_html_parts)
    sidebar = build_sidebar()

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>COBOL入門編</title>
<style>
{CSS}
</style>
</head>
<body>
<div class="wrapper">

<nav id="toc">
  <div class="toc-title">COBOL 入門編</div>
{sidebar}
</nav>

<main>
{pages_html}
</main>

</div>
<script>
{JS}
</script>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = OUTPUT_HTML.stat().st_size / 1024
    print(f"\nHTML 生成完了: {OUTPUT_HTML}  ({size_kb:.1f} KB)")


def main() -> None:
    # Parse optional page range argument: python generate_html.py 1 10
    start_page = 1
    end_page = TOTAL_PAGES
    if len(sys.argv) == 3:
        start_page = int(sys.argv[1])
        end_page = int(sys.argv[2])

    progress = load_progress()
    processed = len(progress)
    print(f"Progress: {processed}/{TOTAL_PAGES} pages done")

    for page_num in range(start_page, end_page + 1):
        key = str(page_num)
        if key in progress:
            print(f"  Page {page_num:02d}: skip (done)")
            continue

        print(f"  Page {page_num:02d}/{TOTAL_PAGES}: processing...", end="", flush=True)
        try:
            html_fragment = process_page(page_num)
            progress[key] = html_fragment
            save_progress(progress)
            print(" done")
        except Exception as e:
            print(f" ERROR: {e}")
            # Continue with next page

    print(f"\nAssembling HTML...")
    assemble_html(progress)


if __name__ == "__main__":
    main()
