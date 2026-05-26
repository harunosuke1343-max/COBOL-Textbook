# CLAUDE.md

古いCOBOL教材のスキャンPDFをデジタル化するプロジェクト。
MarkdownとHTMLの両方へ出力する。

## Workspace Layout

| Path | Description |
|------|-------------|
| `document_pdf.pdf` | Source scanned PDF (~2.7MB, 66 pages) |
| `COBOL入門編_ページ画像/` | Extracted page images `page_001.png`–`page_066.png` |
| `COBOL入門編_文字起こし.txt` | Raw OCR transcription (~88KB) |
| `COBOL入門編.md` | Structured Markdown output (~70KB) |
| `00_BK/` | Backups: previous HTML exports and drafts |

## Python Environment

- **Python 3.12** virtual environment in `.venv/`
- Activate: `.venv\Scripts\activate` (PowerShell) or `source .venv/Scripts/activate` (Git Bash)
- Key packages:
  - **surya-ocr** — primary OCR engine (supports Japanese)
  - **marker-pdf** — PDF-to-Markdown converter
  - **PyMuPDF** — PDF page extraction
  - **torch** (2.11+cu128) — GPU backend for Surya OCR
  - **anthropic** / **openai** — LLM APIs for post-processing
- `.claude/settings.local.json` allows `Bash(python *)` and `WebSearch`

## Workflow

1. **Page extraction** — use PyMuPDF to render PDF pages to PNG in `COBOL入門編_ページ画像/`
2. **OCR** — run Surya OCR on page images to produce `COBOL入門編_文字起こし.txt`
3. **Formatting** — convert raw transcription to structured Markdown (`COBOL入門編.md`) or HTML via LLM
4. **Backup** — save intermediate HTML outputs to `00_BK/`

## Source Material

The textbook is titled "COBOL入門編" (1999), produced by 東京システム営業5部1課. It covers COBOL fundamentals including DIVISIONs, clauses, and file handling for legacy mainframe systems.
