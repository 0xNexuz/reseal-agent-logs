"""Build the report PDF from report/ReSeal_report.md.

Sprint work. Needs: pip install markdown playwright pypdf (and a Chromium for Playwright).

    python report/build.py
"""

from __future__ import annotations

import base64
import re
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
SRC = HERE / "ReSeal_report.md"
OUT = HERE / "ReSeal_report.pdf"

CSS = """
@page { size: A4; margin: 22mm 21mm 22mm 21mm; }
body { font-family: 'Liberation Serif', 'Times New Roman', Times, serif; font-size: 10.6pt;
       line-height: 1.38; color: #111; }
h1 { font-size: 17.5pt; line-height: 1.2; text-align: center; margin: 0 0 8pt; }
h1 + p, h1 + p + p { text-align: center; margin: 2pt 0; }
h1 + p + p { font-size: 9.5pt; color: #444; margin-bottom: 12pt; }
h2 { font-size: 12.5pt; margin: 14pt 0 4pt; break-after: avoid; }
h3 { font-size: 10.8pt; margin: 10pt 0 3pt; break-after: avoid; }
p { margin: 0 0 6pt; text-align: justify; hyphens: auto; }
ul, ol { margin: 0 0 6pt 16pt; padding: 0; }
li { margin: 0 0 2pt; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 4pt; font-size: 8.8pt;
        font-family: 'Liberation Sans', Arial, Helvetica, sans-serif; line-height: 1.25; }
th, td { border-bottom: 0.5pt solid #bbb; padding: 2.5pt 4pt; text-align: left; vertical-align: top; }
th { border-bottom: 1pt solid #111; border-top: 1pt solid #111; }
tr { break-inside: avoid; }
img { width: 100%; margin: 4pt 0 2pt; }
.fig { break-inside: avoid; }
.fig img { width: 92%; display: block; margin: 4pt auto 3pt; }
h2#abstract { text-align: center; font-size: 11pt; margin-top: 6pt; }
h2#abstract + p { margin: 0 9mm 8pt; font-size: 10pt; }
h2.newpage { break-before: page; }
a { color: #111; text-decoration: none; word-break: break-all; }
em { font-style: italic; }
"""


def html() -> str:
    text = SRC.read_text(encoding="utf-8")
    # Appendix C is generated from the results (python -m reseal.numbers)
    cards = (HERE.parent / "results" / "APPENDIX_C.md").read_text(encoding="utf-8")
    text = text.replace("<!-- CLAIMS_CARDS -->", cards)

    def inline_image(m):
        path = (HERE / m.group(2)).resolve()
        data = base64.b64encode(path.read_bytes()).decode()
        return f'<img alt="{m.group(1)}" src="data:image/png;base64,{data}">'

    body = markdown.markdown(text, extensions=["tables", "sane_lists", "toc"])
    body = re.sub(r'<img alt="([^"]*)" src="([^"]+)"\s*/?>', inline_image, body)
    # keep a figure and its caption together
    body = re.sub(r'<p>(<img [^>]+>)</p>\s*<p>(<em>Figure .*?</em>)</p>',
                  r'<div class="fig">\1<p>\2</p></div>', body, flags=re.S)
    # keep each table on one page
    body = body.replace("<table>", '<div class="t"><table>').replace("</table>", "</table></div>")
    # references and appendices start on a new page: they do not count toward the page limit
    body = body.replace('<h2 id="references">', '<h2 id="references" class="newpage">')
    return f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>ReSeal: Do Tamper-Evident Agent Logs Hold Up Against Their Own Operator?</title><style>{CSS}</style></head><body>{body}</body></html>"


def main():
    from playwright.sync_api import sync_playwright
    from pypdf import PdfReader

    page_html = html()
    (HERE / "ReSeal_report.html").write_text(page_html, encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(page_html, wait_until="load")
        page.pdf(path=str(OUT), format="A4", print_background=True,
                 display_header_footer=True, header_template="<span></span>",
                 footer_template="<div style='font-size:8pt;width:100%;text-align:center;"
                                 "font-family:serif;color:#444'><span class='pageNumber'></span></div>",
                 margin={"top": "22mm", "bottom": "22mm", "left": "21mm", "right": "21mm"})
        browser.close()
    reader = PdfReader(str(OUT))
    first_ref = next((i for i, pg in enumerate(reader.pages)
                      if re.search(r"^References\s*$", pg.extract_text() or "", flags=re.M)), None)
    print(f"wrote {OUT.name}: {len(reader.pages)} pages; main text ends before page "
          f"{(first_ref or 0) + 1} ({first_ref} pages of main text)")


if __name__ == "__main__":
    main()
