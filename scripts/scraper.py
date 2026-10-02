# pip install trafilatura requests
import re, time, pathlib, requests, trafilatura
from urllib.parse import urljoin, urlparse

BASE = "https://camtech.edu.kh"
SITEMAP_CANDIDATES = [
    f"{BASE}/sitemap.xml",
    f"{BASE}/wp-sitemap.xml",
    f"{BASE}/sitemap_index.xml",
]
HEADERS = {"User-Agent": "Mozilla/5.0 (student research project)"}
out = pathlib.Path("data/raw/camtech_web")
out.mkdir(parents=True, exist_ok=True)
pdf_out = pathlib.Path("data/raw/camtech_pdfs")
pdf_out.mkdir(parents=True, exist_ok=True)


def get(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        return r if r.status_code == 200 else None
    except requests.RequestException:
        return None


def collect_urls(sitemap_url, seen):
    r = get(sitemap_url)
    if not r:
        return []
    urls = []
    for loc in re.findall(r"<loc>(.*?)</loc>", r.text):
        if loc in seen:
            continue
        seen.add(loc)
        if loc.endswith(".xml"):
            urls += collect_urls(loc, seen)  # follow child sitemaps
        else:
            urls.append(loc)
    return urls


seen, page_urls = set(), []
for sm in SITEMAP_CANDIDATES:
    page_urls = collect_urls(sm, seen)
    if page_urls:
        print(f"Sitemap worked: {sm} ({len(page_urls)} URLs)")
        break
if not page_urls:
    raise SystemExit(
        "No sitemap found. Open the site in a browser and check /robots.txt for the sitemap URL."
    )

pdf_links = set()
for url in page_urls:
    if urlparse(url).netloc != urlparse(BASE).netloc:
        continue
    if url.lower().endswith(".pdf"):
        pdf_links.add(url)
        continue
    html = trafilatura.fetch_url(url)
    if not html:
        continue
    pdf_links.update(
        urljoin(url, h) for h in re.findall(r'href="([^"]+\.pdf)"', html, flags=re.I)
    )
    text = trafilatura.extract(html, output_format="markdown", include_tables=True)
    if text and len(text) > 200:  # skip near-empty pages
        slug = re.sub(r"\W+", "_", url.replace(BASE, "")).strip("_") or "home"
        (out / f"{slug[:100]}.md").write_text(
            f"{text}\n\n---\nSource: {url}\n", encoding="utf-8"
        )
    time.sleep(0.5)

for pdf in pdf_links:
    if urlparse(pdf).netloc != urlparse(BASE).netloc:
        continue
    r = get(pdf)
    if r:
        (pdf_out / pdf.split("/")[-1]).write_bytes(r.content)
        time.sleep(0.5)
print(f"Saved pages to {out}, PDFs to {pdf_out}")
