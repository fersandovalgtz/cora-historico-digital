#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup
from pypdf import PdfReader
from urllib.request import Request, urlopen
import csv, json, hashlib, re, unicodedata

from page_alignment import anchor_inferred_same_page

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / 'data/source/original'
HTML = ORIGINAL / 'ortega_cora_1888_ia.html'
PDF = ORIGINAL / 'ortega_cora_1888_ia.pdf'
PDF_URL = 'https://archive.org/download/vocabulariodelas00orte/vocabulariodelas00orte.pdf'
TEXT_URL = 'https://archive.org/stream/vocabulariodelas00orte/vocabulariodelas00orte_djvu.txt'


def download(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers={'User-Agent': 'Cora-Historico-Digital/0.1 (+https://github.com/fersandovalgtz/cora-historico-digital)'})
    with urlopen(req, timeout=120) as response, path.open('wb') as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)


def ensure_sources() -> None:
    if not PDF.exists():
        print(f'Downloading {PDF_URL}')
        download(PDF_URL, PDF)
    if not HTML.exists():
        print(f'Downloading {TEXT_URL}')
        download(TEXT_URL, HTML)


def collapsed(s):
    return ' '.join(s.split()).strip()


def norm_key(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', s)


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


ensure_sources()
raw_html = HTML.read_text(encoding='utf-8', errors='replace')
soup = BeautifulSoup(raw_html, 'html.parser')
pre = soup.find('pre')
full = pre.get_text('\n') if pre else raw_html
lines = full.splitlines()

(ROOT / 'data/source/ocr').mkdir(parents=True, exist_ok=True)
(ROOT / 'data/lexicon').mkdir(parents=True, exist_ok=True)
(ROOT / 'data/grammar').mkdir(parents=True, exist_ok=True)
(ROOT / 'data/appendices').mkdir(parents=True, exist_ok=True)
(ROOT / 'reports').mkdir(parents=True, exist_ok=True)
(ROOT / 'data/source/ocr/ortega1888_full_ocr.txt').write_text(full, encoding='utf-8')


def find_line(text):
    key = norm_key(text)
    for i, line in enumerate(lines):
        if key in norm_key(line):
            return i
    raise SystemExit(f'Boundary not found: {text}')


start = find_line('A., denotando la persona que padece')
num = find_line('Cuenta para contar todo lo numerable')
irr = find_line('Por último pondrá aqui algunos verbos irregulares')

(ROOT / 'data/grammar/preliminary_ocr.txt').write_text('\n'.join(lines[:start]).rstrip() + '\n', encoding='utf-8')
(ROOT / 'data/source/ocr/lexicon_body_raw.txt').write_text('\n'.join(lines[start:num]).rstrip() + '\n', encoding='utf-8')
(ROOT / 'data/appendices/numerals_ocr.txt').write_text('\n'.join(lines[num:irr]).rstrip() + '\n', encoding='utf-8')
(ROOT / 'data/appendices/irregular_verbs_particles_ocr.txt').write_text('\n'.join(lines[irr:]).rstrip() + '\n', encoding='utf-8')

patterns = [
    re.compile(r'^(?P<a>.{2,100}?)[.]?\s*[-]{1,3}\^?\s*(?P<b>\S.*)$'),
    re.compile(r'^(?P<a>.{2,100}?)[.]?\s*\^[-]\s*(?P<b>\S.*)$'),
    re.compile(r'^(?P<a>.{2,100}?)[.]?\s+r-\s*(?P<b>\S.*)$'),
]


def split_entry(line):
    raw = collapsed(line)
    if len(raw) < 5:
        return None
    if '—' in raw:
        a, b = raw.split('—', 1)
        a = a.rstrip(' .,:;^-r')
        b = b.strip()
        if a and b and any(c.isalpha() for c in a):
            return a, b, 'em_dash'
    for pattern in patterns:
        match = pattern.match(raw)
        if match:
            a = match.group('a').rstrip(' .,:;^-r')
            b = match.group('b').strip()
            if any(c.isalpha() for c in a) and any(c.isalpha() for c in b) and len(a.split()) <= 18:
                return a, b, 'hyphen_variant'
    return None


starts = []
for i in range(start, num):
    split = split_entry(lines[i])
    if split:
        starts.append((i, *split))

reader = PdfReader(str(PDF))
page_norm = {p: norm_key(reader.pages[p - 1].extract_text() or '') for p in range(19, 95)}
current_page = 19
rows = []
for n, (line_index, head, rhs, separator) in enumerate(starts, 1):
    next_i = starts[n][0] if n < len(starts) else num
    span = ' | '.join(collapsed(lines[j]) for j in range(line_index, min(next_i, line_index + 6)) if collapsed(lines[j]))
    key = norm_key(head)
    hit = None
    if len(key) >= 4:
        for page in range(max(19, current_page - 1), min(94, current_page + 4) + 1):
            if key in page_norm[page]:
                hit = page
                break
    if hit:
        current_page = max(current_page, hit)
        pdf_page = hit
        alignment = 'matched_headword'
    else:
        pdf_page = current_page
        alignment = 'inferred_sequence'
    multiple = collapsed(lines[line_index]).count('—') > 1
    confidence = 'high' if separator == 'em_dash' and alignment == 'matched_headword' and not multiple else ('medium' if alignment == 'matched_headword' or separator == 'em_dash' else 'low')
    rows.append({
        'candidate_id': f'ORT1888-cand-{n:06d}',
        'order': n,
        'source_witness_id': 'ORTEGA1888-TEPIC-IA',
        'source_pdf_page': pdf_page,
        'source_printed_page': pdf_page - 4,
        'page_alignment_status': alignment,
        'source_ocr_line_start': line_index + 1,
        'source_ocr_line_end': min(next_i, line_index + 6),
        'headword_es_ocr': head,
        'cora_ocr': rhs,
        'raw_span_ocr': span,
        'separator_type': separator,
        'multiple_separator_flag': str(multiple).lower(),
        'extraction_confidence': confidence,
        'review_status': 'unreviewed_machine_candidate',
        'human_verified': 'false',
    })

# Conservative second pass: an inferred candidate can be reclassified only when
# the nearest previous and next direct headword matches agree on the same page
# already assigned to it. No source page or OCR value is changed.
anchor_inferred_same_page(rows)

fields = list(rows[0])
with (ROOT / 'data/lexicon/candidates.csv').open('w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
with (ROOT / 'data/lexicon/candidates.jsonl').open('w', encoding='utf-8') as f:
    for row in rows:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')

pages_dir = ROOT / 'data/source/ocr/pdf_pages'
pages_dir.mkdir(parents=True, exist_ok=True)
for p, page in enumerate(reader.pages, 1):
    (pages_dir / f'page-{p:03d}.txt').write_text(page.extract_text() or '', encoding='utf-8')

counts = {
    'machine_candidates': len(rows),
    'em_dash_candidates': sum(r['separator_type'] == 'em_dash' for r in rows),
    'hyphen_variant_candidates': sum(r['separator_type'] == 'hyphen_variant' for r in rows),
    'page_alignment_matched': sum(r['page_alignment_status'] == 'matched_headword' for r in rows),
    'page_alignment_anchored_same_page': sum(r['page_alignment_status'] == 'anchored_same_page' for r in rows),
    'page_alignment_inferred': sum(r['page_alignment_status'] == 'inferred_sequence' for r in rows),
    'human_verified': 0,
}
source_hashes = {'pdf': sha256(PDF), 'html_or_text_wrapper': sha256(HTML)}
report = {
    'project': 'Cora Histórico Digital',
    'version': '0.1.0-dev',
    'source_witness_id': 'ORTEGA1888-TEPIC-IA',
    'source_urls': {'pdf': PDF_URL, 'text': TEXT_URL},
    'source_hashes': source_hashes,
    'counts': counts,
    'epistemic_status': 'machine-only candidate inventory; no independent human validation claimed',
}
(ROOT / 'reports/ingest_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
source_manifest = {
    'source_witness_id': 'ORTEGA1888-TEPIC-IA',
    'work_first_printed': 1732,
    'witness_reprint': 1888,
    'internet_archive_identifier': 'vocabulariodelas00orte',
    'urls': {'pdf': PDF_URL, 'text': TEXT_URL},
    'downloaded_sha256': source_hashes,
    'note': 'Source binaries are downloaded reproducibly and are not committed to Git.',
}
(ROOT / 'data/source/source_manifest.json').write_text(json.dumps(source_manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(counts, ensure_ascii=False, indent=2))
