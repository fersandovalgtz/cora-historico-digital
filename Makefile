PYTHON ?= python3

.PHONY: ingest validate source-coverage appendix-machine-inventory numeral-machine-lexicon irregular-particles-machine machine-corpus stats

ingest:
	$(PYTHON) scripts/ingest_ortega1888.py

validate:
	$(PYTHON) scripts/validate_candidates.py

source-coverage:
	$(PYTHON) scripts/audit_source_coverage.py

appendix-machine-inventory:
	$(PYTHON) scripts/build_appendix_machine_inventory.py

numeral-machine-lexicon:
	$(PYTHON) scripts/build_numeral_machine_lexicon.py

irregular-particles-machine:
	$(PYTHON) scripts/build_irregular_particles_machine.py

machine-corpus:
	$(PYTHON) scripts/build_machine_corpus.py

stats:
	$(PYTHON) -c "import json; print(json.dumps({'lexicon': json.load(open('reports/machine_resolution.json')), 'numerals': json.load(open('reports/numerals_machine.json')), 'irregular_particles': json.load(open('reports/irregular_particles_machine.json'))}, ensure_ascii=False, indent=2))"
