PYTHON ?= python3

.PHONY: ingest validate source-coverage appendix-machine-inventory numeral-machine-lexicon irregular-particles-machine machine-corpus tei-lex0 cldf-dictionary release-manifest stats

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

tei-lex0:
	$(PYTHON) scripts/build_tei_lex0.py

cldf-dictionary:
	$(PYTHON) scripts/build_cldf_dictionary.py

release-manifest:
	$(PYTHON) scripts/build_release_manifest.py

stats:
	$(PYTHON) -c "import json; print(json.dumps({'lexicon': json.load(open('reports/machine_resolution.json')), 'numerals': json.load(open('reports/numerals_machine.json')), 'irregular_particles': json.load(open('reports/irregular_particles_machine.json')), 'tei_lex0': json.load(open('reports/tei_lex0.json')), 'cldf_dictionary': json.load(open('reports/cldf_dictionary.json'))}, ensure_ascii=False, indent=2))"
