PYTHON ?= python3

.PHONY: ingest validate reconciliation-queue stats

ingest:
	$(PYTHON) scripts/ingest_ortega1888.py

validate:
	$(PYTHON) scripts/validate_candidates.py

reconciliation-queue:
	$(PYTHON) scripts/build_reconciliation_queue.py

stats:
	$(PYTHON) -c "import json; print(json.dumps(json.load(open('reports/ingest_report.json')), ensure_ascii=False, indent=2))"
