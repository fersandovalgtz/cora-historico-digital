PYTHON ?= python3

.PHONY: ingest validate source-coverage appendix-review-inventory reconciliation-queue reconciliation-summary inferred-review-batch render-inferred-facsimile human-review-sheet render-page-review-facsimile page-review-sheet validate-reconciliation reconciliation-status canonicalization-plan stats

ingest:
	$(PYTHON) scripts/ingest_ortega1888.py

validate:
	$(PYTHON) scripts/validate_candidates.py

source-coverage:
	$(PYTHON) scripts/audit_source_coverage.py

appendix-review-inventory:
	$(PYTHON) scripts/build_appendix_review_inventory.py

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

render-page-review-facsimile:
	$(PYTHON) scripts/render_page_review_facsimile.py

page-review-sheet:
	$(PYTHON) scripts/build_page_review_sheet.py

validate-reconciliation:
	$(PYTHON) scripts/validate_reconciliation_decisions.py

reconciliation-status:
	$(PYTHON) scripts/summarize_reconciliation_status.py

canonicalization-plan:
	$(PYTHON) scripts/plan_canonicalization.py

stats:
	$(PYTHON) -c "import json; print(json.dumps(json.load(open('reports/ingest_report.json')), ensure_ascii=False, indent=2))"
