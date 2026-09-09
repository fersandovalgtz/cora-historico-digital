#!/usr/bin/env python3
from pathlib import Path
import csv, re, sys, json

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'data/lexicon/candidates.csv'
rows = list(csv.DictReader(path.open(encoding='utf-8')))
errors = []
ids = set()
prev = 0
for row in rows:
    cid = row['candidate_id']
    if not re.fullmatch(r'ORT1888-cand-\d{6}', cid):
        errors.append(f'bad id {cid}')
    if cid in ids:
        errors.append(f'duplicate id {cid}')
    ids.add(cid)
    order = int(row['order'])
    if order <= prev:
        errors.append(f'nonmonotonic order {cid}')
    prev = order
    if row['human_verified'] != 'false':
        errors.append(f'unexpected human_verified {cid}')
    if not row['headword_es_ocr'].strip() or not row['cora_ocr'].strip():
        errors.append(f'empty field {cid}')
    pdf_page = int(row['source_pdf_page'])
    printed_page = int(row['source_printed_page'])
    if pdf_page - printed_page != 4:
        errors.append(f'page offset mismatch {cid}')
if errors:
    print('\n'.join(errors[:100]), file=sys.stderr)
    sys.exit(1)
print(json.dumps({'rows': len(rows), 'status': 'ok', 'human_verified': 0}, indent=2))
