PYTHON ?= python3

.PHONY: ingest validate source-coverage appendix-machine-inventory machine-corpus stats

ingest:
	$(PYTHON) scripts/ingest_ortega1888.py

validate:
	$(PYTHON) scripts/validate_candidates.py

source-coverage:
	$(PYTHON) scripts/audit_source_coverage.py

appendix-machine-inventory:
	$(PYTHON) scripts/build_appendix_machine_inventory.py

machine-corpus:
	$(PYTHON) scripts/build_machine_corpus.py

stats:
	$(PYTHON) -c "import json; print(json.dumps(json.load(open('reports/machine_resolution.json')), ensure_ascii=False, indent=2))"
