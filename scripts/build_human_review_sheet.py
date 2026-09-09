#!/usr/bin/env python3
"""Build a self-contained human review sheet for unresolved phase-2 cases.

The sheet displays the facsimile assets and machine navigation evidence, but no
human decision exists until a reviewer explicitly confirms that the facsimile was
inspected and exports a decision JSON in the browser.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_FACSIMILE_MANIFEST = Path("artifacts/phase2_facsimile_review/facsimile_manifest.json")
DEFAULT_INFERRED_BATCH = Path("artifacts/phase2_facsimile_review/inferred_review_batch.json")
DEFAULT_DECISIONS_DIR = Path("data/reconciliation/decisions")
DEFAULT_OUTPUT = Path("artifacts/phase2_facsimile_review/review_sheet.html")

DECISION_RE = re.compile(r"^ORT1888-rec-([0-9]{6})$")
QUICK_ACTIONS = ["accept_boundary", "reject_false_boundary", "defer_uncertain"]
ADVANCED_ACTIONS = ["merge_candidates", "split_candidate"]


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def existing_decision_numbers(directory: Path) -> set[int]:
    numbers: set[int] = set()
    if not directory.exists():
        return numbers

    def collect(payload: Any) -> None:
        if not isinstance(payload, dict):
            return
        decision_id = payload.get("decision_id")
        if not isinstance(decision_id, str):
            return
        match = DECISION_RE.fullmatch(decision_id)
        if match:
            numbers.add(int(match.group(1)))

    for path in sorted(directory.glob("*.json")):
        collect(json.loads(path.read_text(encoding="utf-8")))
    for path in sorted(directory.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                collect(json.loads(line))
    return numbers


def allocate_decision_ids(count: int, used: set[int]) -> list[str]:
    result: list[str] = []
    number = 1
    while len(result) < count:
        if number not in used:
            result.append(f"ORT1888-rec-{number:06d}")
        number += 1
    return result


def validate_manifests(facsimile: dict[str, Any], inferred: dict[str, Any]) -> list[str]:
    if facsimile.get("human_verified") is not False:
        raise ValueError("facsimile manifest must remain human_verified=false")
    if inferred.get("human_verified") is not False:
        raise ValueError("inferred review batch must remain human_verified=false")
    if facsimile.get("facsimile_required") is not True:
        raise ValueError("facsimile manifest must require facsimile review")
    if inferred.get("facsimile_required") is not True:
        raise ValueError("inferred review batch must require facsimile review")

    facsimile_ids = [case.get("candidate_id") for case in facsimile.get("cases", [])]
    inferred_ids = [case.get("candidate_id") for case in inferred.get("cases", [])]
    if facsimile_ids != inferred_ids:
        raise ValueError(
            "facsimile and inferred-review case lists differ: "
            f"{facsimile_ids!r} != {inferred_ids!r}"
        )
    if facsimile.get("case_count") != len(facsimile_ids):
        raise ValueError("facsimile case_count does not match cases")
    if inferred.get("case_count") != len(inferred_ids):
        raise ValueError("inferred review case_count does not match cases")
    return [str(value) for value in facsimile_ids]


def page_numbers(case: dict[str, Any]) -> list[int]:
    values = set()
    for row_key in ("target", "previous_direct_anchor", "next_direct_anchor"):
        row = case.get(row_key)
        if isinstance(row, dict):
            value = row.get("source_pdf_page")
            if isinstance(value, int) and value > 0:
                values.add(value)
    return sorted(values)


def printed_pages(case: dict[str, Any]) -> list[int]:
    values = set()
    for row_key in ("target", "previous_direct_anchor", "next_direct_anchor"):
        row = case.get(row_key)
        if isinstance(row, dict):
            value = row.get("source_printed_page")
            if isinstance(value, int) and value > 0:
                values.add(value)
    return sorted(values)


def render_sheet(
    facsimile: dict[str, Any],
    inferred: dict[str, Any],
    suggested_ids: list[str],
) -> str:
    case_ids = validate_manifests(facsimile, inferred)
    if len(suggested_ids) != len(case_ids):
        raise ValueError("suggested decision ID count does not match review cases")

    inferred_by_id = {case["candidate_id"]: case for case in inferred.get("cases", [])}
    cards: list[str] = []
    case_payloads: list[dict[str, Any]] = []

    for index, (case, decision_id) in enumerate(zip(facsimile.get("cases", []), suggested_ids), start=1):
        candidate_id = str(case["candidate_id"])
        target = case.get("target") or {}
        nav = inferred_by_id[candidate_id]
        observations = nav.get("machine_observations", [])
        crops = case.get("boundary_crop_assets", [])
        full_pages = case.get("full_page_assets", [])

        crop_html = "".join(
            f'<figure><img src="{html.escape(asset["path"])}" alt="{html.escape(asset["role"])}"><figcaption>{html.escape(asset["role"])} · PDF {asset["source_pdf_page"]}</figcaption></figure>'
            for asset in crops
        )
        full_html = "".join(
            f'<a class="page-link" href="{html.escape(path)}" target="_blank" rel="noopener">{html.escape(path)}</a>'
            for path in full_pages
        )
        observation_html = "".join(
            f"<li><code>{html.escape(str(observation))}</code></li>" for observation in observations
        )
        quick_options = "".join(
            f'<option value="{action}">{action}</option>' for action in QUICK_ACTIONS
        )
        advanced = ", ".join(f"<code>{action}</code>" for action in ADVANCED_ACTIONS)

        cards.append(
            f"""
<section class="case" id="case-{index}">
  <header>
    <div><span class="eyebrow">Caso {index}</span><h2>{html.escape(candidate_id)} · <code>{html.escape(str(target.get('headword_es_ocr', '')))}</code></h2></div>
    <span class="badge">pendiente de revisión humana</span>
  </header>
  <div class="metadata">
    <div><strong>Span OCR</strong><code>{html.escape(str(target.get('raw_span_ocr', '')))}</code></div>
    <div><strong>Página asignada</strong>PDF {target.get('source_pdf_page')} / impresa {target.get('source_printed_page')}</div>
    <div><strong>ID sugerido</strong><code>{html.escape(decision_id)}</code></div>
  </div>
  <div class="observations"><strong>Señales automáticas — no son una decisión</strong><ul>{observation_html}</ul></div>
  <div class="crops">{crop_html}</div>
  <details><summary>Abrir páginas completas</summary><div class="page-links">{full_html}</div></details>
  <div class="decision-box">
    <label>Acción de un solo candidato
      <select class="action"><option value="">Seleccione…</option>{quick_options}</select>
    </label>
    <label>Justificación basada en el facsímil
      <textarea class="rationale" rows="4" placeholder="Describa qué observa en la página y por qué sostiene la acción elegida."></textarea>
    </label>
    <label class="confirmation"><input type="checkbox" class="confirmed"> Confirmo que inspeccioné personalmente el facsímil mostrado para este caso.</label>
    <p class="advanced-note">Si la evidencia exige {advanced}, no use la exportación rápida: esas acciones requieren candidatos o spans adicionales.</p>
    <div class="buttons"><button type="button" class="copy">Copiar JSON</button><button type="button" class="save">Guardar JSON</button></div>
    <pre class="output" aria-live="polite"></pre>
  </div>
</section>
"""
        )
        case_payloads.append(
            {
                "candidate_id": candidate_id,
                "decision_id": decision_id,
                "source_pdf_pages": page_numbers(case),
                "source_printed_pages": printed_pages(case),
                "source_pdf_sha256": facsimile.get("source_pdf_sha256", ""),
                "facsimile_assets": [asset.get("path") for asset in crops] + list(full_pages),
            }
        )

    payload_json = json.dumps(case_payloads, ensure_ascii=False).replace("</", "<\\/")
    source_hash = html.escape(str(facsimile.get("source_pdf_sha256", "")))
    witness = html.escape(str(facsimile.get("source_witness_id", "")))

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cora Histórico Digital · revisión humana de fronteras</title>
<style>
:root {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color-scheme: light; }}
body {{ margin: 0; background: #f4f1e9; color: #26231f; }}
main {{ max-width: 1180px; margin: 0 auto; padding: 32px 20px 80px; }}
.hero, .case {{ background: #fffdf8; border: 1px solid #d8d0c0; border-radius: 14px; box-shadow: 0 6px 24px rgba(43,37,28,.06); }}
.hero {{ padding: 28px; margin-bottom: 24px; }}
.hero h1 {{ margin: 0 0 12px; font-family: Georgia, serif; font-size: clamp(1.8rem,4vw,3rem); }}
.hero p {{ max-width: 850px; line-height: 1.55; }}
.source {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(260px,1fr)); gap: 10px; padding-top: 10px; font-size: .92rem; }}
.case {{ padding: 22px; margin: 20px 0; }}
.case header {{ display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; }}
h2 {{ margin: 3px 0 16px; font-size: 1.25rem; }}
.eyebrow {{ text-transform: uppercase; letter-spacing: .08em; font-size: .72rem; font-weight: 700; }}
.badge {{ border: 1px solid #8c7353; border-radius: 999px; padding: 6px 10px; font-size: .78rem; white-space: nowrap; }}
.metadata {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap: 12px; margin: 12px 0 18px; }}
.metadata div {{ background: #f8f4ea; padding: 12px; border-radius: 8px; display: flex; flex-direction: column; gap: 5px; }}
code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; overflow-wrap: anywhere; }}
.observations {{ padding: 12px 14px; border-left: 4px solid #8c7353; background: #faf7ef; margin: 14px 0; }}
.observations ul {{ margin: 8px 0 0; }}
.crops {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(330px,1fr)); gap: 16px; margin: 18px 0; }}
figure {{ margin: 0; }}
figure img {{ width: 100%; height: auto; display: block; border: 1px solid #c7bdab; border-radius: 8px; background: white; }}
figcaption {{ font-size: .82rem; margin-top: 6px; color: #5d5549; }}
details {{ margin: 14px 0; }}
.page-links {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }}
.page-link {{ color: #463b2d; background: #eee6d7; padding: 7px 9px; border-radius: 6px; text-decoration: none; }}
.decision-box {{ border-top: 1px solid #d8d0c0; padding-top: 18px; margin-top: 18px; display: grid; gap: 14px; }}
label {{ display: grid; gap: 6px; font-weight: 650; }}
select, textarea, input[type="text"] {{ font: inherit; padding: 10px; border: 1px solid #aaa091; border-radius: 7px; background: white; }}
.confirmation {{ display: flex; gap: 9px; align-items: flex-start; font-weight: 500; }}
.advanced-note {{ margin: 0; font-size: .88rem; color: #5b5145; }}
.buttons {{ display: flex; gap: 10px; }}
button {{ font: inherit; border: 1px solid #554838; border-radius: 7px; padding: 9px 14px; background: #fff; cursor: pointer; }}
button:disabled {{ opacity: .45; cursor: not-allowed; }}
.output {{ white-space: pre-wrap; word-break: break-word; background: #201e1b; color: #f8f3ea; border-radius: 8px; padding: 12px; min-height: 1.2em; }}
.global-reviewer {{ display: grid; gap: 6px; max-width: 480px; margin-top: 20px; }}
.warning {{ font-weight: 650; }}
@media (max-width: 650px) {{ .case header {{ flex-direction: column; }} .badge {{ white-space: normal; }} .crops {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<main>
<section class="hero">
  <span class="eyebrow">Cora Histórico Digital · fase 2</span>
  <h1>Hoja de revisión humana del facsímil</h1>
  <p class="warning">Abrir esta hoja no valida ningún caso. Un JSON con <code>human_verified=true</code> sólo se genera después de que una persona marque expresamente que inspeccionó el facsímil, elija una acción admisible y escriba una justificación.</p>
  <label class="global-reviewer">Nombre de la persona revisora<input id="reviewer" type="text" autocomplete="name" placeholder="Nombre completo"></label>
  <div class="source"><div><strong>Testimonio</strong><br>{witness}</div><div><strong>SHA-256 PDF</strong><br><code>{source_hash}</code></div><div><strong>Casos</strong><br>{len(case_ids)}</div></div>
</section>
{''.join(cards)}
</main>
<script>
const cases = {payload_json};
function buildDecision(section, data) {{
  const reviewer = document.getElementById('reviewer').value.trim();
  const action = section.querySelector('.action').value;
  const rationale = section.querySelector('.rationale').value.trim();
  const confirmed = section.querySelector('.confirmed').checked;
  if (!reviewer) throw new Error('Escriba el nombre de la persona revisora.');
  if (!action) throw new Error('Seleccione una acción.');
  if (!rationale) throw new Error('Escriba una justificación basada en el facsímil.');
  if (!confirmed) throw new Error('Debe confirmar que inspeccionó personalmente el facsímil.');
  if (!['accept_boundary','reject_false_boundary','defer_uncertain'].includes(action)) throw new Error('La acción seleccionada no admite exportación rápida.');
  return {{
    decision_id: data.decision_id,
    source_witness_id: 'ORTEGA1888-TEPIC-IA',
    candidate_ids: [data.candidate_id],
    action,
    source_pdf_pages: data.source_pdf_pages,
    source_printed_pages: data.source_printed_pages,
    reviewer,
    reviewed_at: new Date().toISOString(),
    rationale,
    evidence_note: `Facsimile packet from locked PDF SHA-256 ${{data.source_pdf_sha256}}; assets: ${{data.facsimile_assets.join(', ')}}`,
    human_verified: true
  }};
}}
function show(section, message) {{ section.querySelector('.output').textContent = message; }}
document.querySelectorAll('.case').forEach((section, i) => {{
  const data = cases[i];
  section.querySelector('.copy').addEventListener('click', async () => {{
    try {{
      const decision = buildDecision(section, data);
      const text = JSON.stringify(decision, null, 2);
      await navigator.clipboard.writeText(text);
      show(section, text + '\n\nCopiado al portapapeles.');
    }} catch (error) {{ show(section, 'No se generó decisión: ' + error.message); }}
  }});
  section.querySelector('.save').addEventListener('click', () => {{
    try {{
      const decision = buildDecision(section, data);
      const text = JSON.stringify(decision, null, 2) + '\n';
      const blob = new Blob([text], {{type: 'application/json'}});
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = data.decision_id + '.json';
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(link.href), 1000);
      show(section, text);
    }} catch (error) {{ show(section, 'No se generó decisión: ' + error.message); }}
  }});
}});
</script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--facsimile-manifest", type=Path, default=DEFAULT_FACSIMILE_MANIFEST)
    parser.add_argument("--inferred-batch", type=Path, default=DEFAULT_INFERRED_BATCH)
    parser.add_argument("--decisions-dir", type=Path, default=DEFAULT_DECISIONS_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    facsimile = load_json(args.facsimile_manifest)
    inferred = load_json(args.inferred_batch)
    case_ids = validate_manifests(facsimile, inferred)
    suggested_ids = allocate_decision_ids(
        len(case_ids), existing_decision_numbers(args.decisions_dir)
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_sheet(facsimile, inferred, suggested_ids), encoding="utf-8")
    print(f"wrote human review sheet for {len(case_ids)} cases to {args.output}")


if __name__ == "__main__":
    main()
