#!/usr/bin/env python3
from pathlib import Path
import csv, sys

ROOT = Path(__file__).resolve().parents[1]
query = ' '.join(sys.argv[1:]).strip().casefold()
if not query:
    raise SystemExit('Uso: python scripts/query_lexicon.py término')
rows = csv.DictReader((ROOT / 'data/lexicon/candidates.csv').open(encoding='utf-8'))
for row in rows:
    haystack = (row['headword_es_ocr'] + ' ' + row['cora_ocr']).casefold()
    if query in haystack:
        print(f"{row['candidate_id']}  p.{row['source_printed_page']}  {row['headword_es_ocr']} — {row['cora_ocr']}  [{row['extraction_confidence']}; {row['review_status']}]")
