"""Render a briefing markdown file to PDF via styled HTML and headless Chromium.

Usage: python3 tools/md2pdf.py input.md output.pdf

Sessions run in ephemeral containers, so the markdown dependency is
installed on demand. Chromium is resolved from the Playwright browsers
directory (PLAYWRIGHT_BROWSERS_PATH) or PATH. YAML front matter is stripped;
local images referenced by the markdown are inlined as data URIs so the
intermediate HTML can live anywhere.
"""

import base64
import glob
import mimetypes
import pathlib
import re
import subprocess
import sys
import tempfile

try:
    import markdown
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "markdown"], check=True)
    import markdown

CSS = """
  @page { size: A4; margin: 18mm 16mm; }
  body { font-family: Georgia, 'Times New Roman', serif; font-size: 10.5pt; line-height: 1.55; color: #1a1a1a; }
  h1 { font-size: 19pt; margin: 0 0 4pt; border-bottom: 2.5pt solid #1a1a1a; padding-bottom: 6pt; }
  h2 { font-size: 13.5pt; margin: 18pt 0 6pt; border-bottom: 1pt solid #999; padding-bottom: 3pt; }
  h3 { font-size: 11pt; margin: 12pt 0 4pt; }
  p { margin: 5pt 0; text-align: justify; }
  li { margin: 3pt 0; }
  a { color: #0b4f8a; text-decoration: none; }
  hr { border: none; border-top: 0.75pt solid #bbb; margin: 12pt 0; }
  img { max-width: 100%; }
  table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 8pt 0; }
  th, td { border: 0.5pt solid #999; padding: 4pt 6pt; text-align: left; vertical-align: top; }
  th { background: #efefef; }
  h2, h3 { page-break-after: avoid; }
  table, blockquote, img { page-break-inside: avoid; }
"""


def strip_front_matter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            return text[end + 4 :].lstrip("\n")
    return text


def inline_images(html: str, base_dir: pathlib.Path) -> str:
    def repl(m):
        src = m.group(1)
        if src.startswith(("http://", "https://", "data:")):
            return m.group(0)
        path = (base_dir / src).resolve()
        if not path.is_file():
            print(f"warning: image not found, left as-is: {src}", file=sys.stderr)
            return m.group(0)
        mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        data = base64.b64encode(path.read_bytes()).decode()
        return m.group(0).replace(src, f"data:{mime};base64,{data}")

    return re.sub(r'<img [^>]*?src="([^"]+)"', repl, html)


def find_chromium() -> str:
    candidates = glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome")
    if candidates:
        return sorted(candidates)[-1]
    for name in ("chromium", "chromium-browser", "google-chrome"):
        found = subprocess.run(["which", name], capture_output=True, text=True)
        if found.returncode == 0:
            return found.stdout.strip()
    raise SystemExit("no chromium binary found")


def main() -> None:
    src = pathlib.Path(sys.argv[1]).resolve()
    out_pdf = pathlib.Path(sys.argv[2]).resolve()

    body = markdown.markdown(
        strip_front_matter(src.read_text()), extensions=["tables", "smarty"]
    )
    body = inline_images(body, src.parent)
    html = (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        f"<style>{CSS}</style></head><body>{body}</body></html>"
    )

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html)
        html_path = f.name

    subprocess.run(
        [
            find_chromium(),
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--print-to-pdf={out_pdf}",
            html_path,
        ],
        check=True,
        capture_output=True,
    )
    print(f"wrote {out_pdf}")


if __name__ == "__main__":
    main()
