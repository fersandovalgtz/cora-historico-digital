PYTHON ?= python3

.PHONY: ingest validate reconciliation-queue reconciliation-summary inferred-review-batch render-inferred-facsimile human-review-sheet validate-reconciliation stats

ingest:
	$(PYTHON) scripts/ingest_ortega1888.py

validate:
	$(PYTHON) scripts/validate_candidates.py

reconciliation-queue:
	$(PYTHON) scripts/build_reconciliation_queue.py

reconciliation-summary:
	$(PYTHON) scripts/summarize_reconciliation_queue.py

inferred-review-batch:
	$(PYTHON) scripts/build_inferred_review_batch.py

render-inferred-facsimile:
	$(PYTHON) scripts/render_inferred_facsimile.py

human-review-sheet:
	$(PYTHON) scripts/build_human_review_sheet.py

validate-reconciliation:
	$(PYTHON) scripts/validate_reconciliation_decisions.py

stats:
	$(PYTHON) -c "import json; print(json.dumps(json.load(open('reports/ingest_report.json')), ensure_ascii=False, indent=2))"
