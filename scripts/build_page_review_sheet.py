#!/usr/bin/env python3
"""Build a self-contained page-by-page human review workbench.

The sheet can export only singleton ``accept_boundary`` decisions. A candidate
remains unselected by default and cannot be selected until the reviewer confirms
personal inspection of the corresponding facsimile page. Complex or uncertain
cases must be handled outside this bulk-acceptance interface.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

from build_human_review_sheet import allocate_decision_ids, existing_decision_numbers

DEFAULT_MANIFEST = Path("artifacts/phase2_page_review/page_review_manifest.json")
DEFAULT_DECISIONS_DIR = Path("data/reconciliation/decisions")
DEFAULT_OUTPUT = Path("artifacts/phase2_page_review/review_sheet.html")


def load_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def validate_manifest(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    if manifest.get("artifact_type") != "facsimile_page_review_packet":
        raise ValueError("unexpected page review artifact_type")
    if manifest.get("human_verified") is not False:
        raise ValueError("page review manifest must remain human_verified=false")
    if manifest.get("machine_generated") is not True:
        raise ValueError("page review manifest must be machine_generated=true")
    if manifest.get("facsimile_required") is not True:
        raise ValueError("page review manifest must require facsimile review")

    pages = manifest.get("pages")
    if not isinstance(pages, list):
        raise ValueError("page review manifest pages must be a list")
    if manifest.get("review_page_total") != len(pages):
        raise ValueError("review_page_total does not match pages")

    candidates: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_pages: set[int] = set()
    for page in pages:
        if not isinstance(page, dict):
            raise ValueError("page review page entry must be an object")
        page_number = page.get("source_pdf_page")
        if type(page_number) is not int or page_number < 1:
            raise ValueError("page review page has invalid source_pdf_page")
        if page_number in seen_pages:
            raise ValueError(f"duplicate review page {page_number}")
        seen_pages.add(page_number)
        page_candidates = page.get("candidates")
        if not isinstance(page_candidates, list):
            raise ValueError(f"review page {page_number} candidates must be a list")
        if page.get("candidate_count") != len(page_candidates):
            raise ValueError(f"review page {page_number} candidate_count mismatch")
        for candidate in page_candidates:
            if not isinstance(candidate, dict):
                raise ValueError(f"review page {page_number} candidate must be an object")
            candidate_id = candidate.get("candidate_id")
            if not isinstance(candidate_id, str) or not candidate_id:
                raise ValueError(f"review page {page_number} has candidate without ID")
            if candidate_id in seen_ids:
                raise ValueError(f"duplicate review candidate {candidate_id}")
            if candidate.get("source_pdf_page") != page_number:
                raise ValueError(f"candidate {candidate_id} does not belong to review page {page_number}")
            if candidate.get("page_alignment_status") == "inferred_sequence":
                raise ValueError(f"inferred candidate {candidate_id} must not enter bulk page review")
            seen_ids.add(candidate_id)
            candidates.append(candidate)

    if manifest.get("reviewable_candidate_total") != len(candidates):
        raise ValueError("reviewable_candidate_total does not match candidate inventory")

    excluded = manifest.get("excluded_inferred_candidate_ids")
    if not isinstance(excluded, list):
        raise ValueError("excluded_inferred_candidate_ids must be a list")
    if manifest.get("excluded_inferred_candidate_total") != len(excluded):
        raise ValueError("excluded_inferred_candidate_total does not match excluded IDs")
    if set(excluded) & seen_ids:
        raise ValueError("an inferred-excluded candidate also appears in bulk page review")
    return candidates


def render_sheet(manifest: dict[str, Any], suggested_ids: list[str]) -> str:
    candidates = validate_manifest(manifest)
    if len(suggested_ids) != len(candidates):
        raise ValueError("suggested decision ID count does not match review candidates")
    if len(set(suggested_ids)) != len(suggested_ids):
        raise ValueError("suggested decision IDs must be unique")

    decision_by_candidate = {
        candidate["candidate_id"]: decision_id
        for candidate, decision_id in zip(candidates, suggested_ids)
    }

    page_sections: list[str] = []
    client_pages: list[dict[str, Any]] = []
    for page_index, page in enumerate(manifest["pages"], start=1):
        page_number = page["source_pdf_page"]
        rows_html: list[str] = []
        client_candidates: list[dict[str, Any]] = []
        for candidate in page["candidates"]:
            candidate_id = str(candidate["candidate_id"])
            decision_id = decision_by_candidate[candidate_id]
            printed_page = candidate.get("source_printed_page")
            printed_label = "—" if printed_page is None else str(printed_page)
            rows_html.append(
                f"""
<tr>
  <td><input class="candidate-check" type="checkbox" data-candidate="{html.escape(candidate_id)}" disabled aria-label="Aceptar {html.escape(candidate_id)}"></td>
  <td><code>{html.escape(candidate_id)}</code><br><small>{html.escape(decision_id)}</small></td>
  <td>{candidate.get('order')}</td>
  <td><strong>{html.escape(str(candidate.get('headword_es_ocr', '')))}</strong><br><span class="cora">{html.escape(str(candidate.get('cora_ocr', '')))}</span></td>
  <td><code>{html.escape(str(candidate.get('page_alignment_status', '')))}</code><br><small>{html.escape(str(candidate.get('extraction_confidence', '')))}</small></td>
  <td>{printed_label}</td>
  <td class="raw">{html.escape(str(candidate.get('raw_span_ocr', '')))}</td>
</tr>
"""
            )
            client_candidates.append(
                {
                    "candidate_id": candidate_id,
                    "decision_id": decision_id,
                    "source_pdf_page": page_number,
                    "source_printed_page": printed_page,
                }
            )

        page_sections.append(
            f"""
<section class="page-card" data-page-index="{page_index - 1}">
  <header class="page-header">
    <div><span class="eyebrow">Página de revisión {page_index}</span><h2>PDF {page_number} · {page['candidate_count']} candidatos</h2></div>
    <span class="badge">sin validar</span>
  </header>
  <div class="facsimile"><img src="{html.escape(str(page['path']))}" alt="Facsímil PDF {page_number}" loading="lazy"></div>
  <div class="gate">
    <label class="confirmation"><input class="page-confirmed" type="checkbox"> Confirmo que inspeccioné personalmente esta página completa del facsímil antes de marcar límites como correctos.</label>
    <label>Nota opcional de cotejo<input class="page-note" type="text" placeholder="Observación específica de esta página, si aplica"></label>
    <div class="page-actions"><button type="button" class="select-all" disabled>Marcar todos como límites correctos</button><button type="button" class="clear-all">Limpiar selección</button></div>
  </div>
  <div class="table-wrap"><table><thead><tr><th>Aceptar</th><th>ID</th><th>Orden</th><th>Entrada OCR</th><th>Alineación</th><th>Pág. impresa</th><th>Span OCR</th></tr></thead><tbody>{''.join(rows_html)}</tbody></table></div>
  <div class="export-actions"><button type="button" class="copy-page">Copiar JSONL de esta página</button><button type="button" class="save-page">Guardar JSONL de esta página</button><span class="page-count">0 seleccionados</span></div>
  <pre class="output" aria-live="polite"></pre>
</section>
"""
        )
        client_pages.append(
            {
                "source_pdf_page": page_number,
                "path": page["path"],
                "candidates": client_candidates,
            }
        )

    client_json = json.dumps(client_pages, ensure_ascii=False).replace("</", "<\\/")
    source_hash = html.escape(str(manifest.get("source_pdf_sha256", "")))
    witness = html.escape(str(manifest.get("source_witness_id", "")))
    excluded_count = int(manifest.get("excluded_inferred_candidate_total", 0))

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cora Histórico Digital · banco de revisión por página</title>
<style>
:root {{ font-family: system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; color-scheme: light; }}
body {{ margin:0; background:#f3f1eb; color:#24211d; }}
main {{ max-width:1500px; margin:0 auto; padding:28px 18px 80px; }}
.hero,.page-card {{ background:#fffdf9; border:1px solid #d4cdbf; border-radius:14px; box-shadow:0 6px 22px rgba(50,43,32,.06); }}
.hero {{ padding:26px; margin-bottom:22px; }}
h1 {{ margin:.2rem 0 .8rem; font-family:Georgia,serif; font-size:clamp(1.8rem,4vw,2.8rem); }}
.hero p {{ max-width:1000px; line-height:1.55; }}
.eyebrow {{ text-transform:uppercase; letter-spacing:.08em; font-size:.72rem; font-weight:750; }}
.global {{ display:grid; grid-template-columns:minmax(260px,480px) 1fr; gap:18px; align-items:end; margin-top:18px; }}
label {{ display:grid; gap:6px; font-weight:650; }}
input[type="text"] {{ font:inherit; padding:9px 10px; border:1px solid #aaa293; border-radius:7px; background:white; }}
.summary {{ display:flex; flex-wrap:wrap; gap:10px; font-size:.9rem; }}
.summary span {{ background:#f3eee4; padding:7px 9px; border-radius:7px; }}
.page-card {{ padding:20px; margin:20px 0; }}
.page-header {{ display:flex; justify-content:space-between; gap:16px; align-items:flex-start; }}
h2 {{ margin:4px 0 14px; font-size:1.25rem; }}
.badge {{ border:1px solid #8b7352; border-radius:999px; padding:6px 10px; font-size:.8rem; }}
.facsimile {{ max-width:980px; margin:0 auto 18px; }}
.facsimile img {{ width:100%; height:auto; display:block; border:1px solid #bdb4a5; background:white; }}
.gate {{ display:grid; gap:12px; border:1px solid #d8d0c1; background:#faf7ef; border-radius:9px; padding:14px; margin:14px 0; }}
.confirmation {{ display:flex; gap:9px; align-items:flex-start; font-weight:650; }}
.page-actions,.export-actions,.global-actions {{ display:flex; flex-wrap:wrap; gap:10px; align-items:center; }}
button {{ font:inherit; border:1px solid #594d3e; border-radius:7px; padding:8px 12px; background:white; cursor:pointer; }}
button:disabled {{ opacity:.42; cursor:not-allowed; }}
.table-wrap {{ overflow:auto; border:1px solid #ddd5c8; border-radius:8px; }}
table {{ width:100%; border-collapse:collapse; font-size:.88rem; }}
th,td {{ border-bottom:1px solid #e3ddd2; padding:8px; text-align:left; vertical-align:top; }}
th {{ position:sticky; top:0; background:#f5f0e6; }}
.raw {{ min-width:260px; max-width:440px; }}
.cora {{ color:#4d463c; }}
code {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; overflow-wrap:anywhere; }}
.output {{ white-space:pre-wrap; word-break:break-word; background:#211f1c; color:#f8f3e9; border-radius:8px; padding:11px; min-height:1.2em; }}
.export-actions {{ margin-top:14px; }}
.global-actions {{ position:sticky; bottom:12px; z-index:5; margin-top:24px; background:#fffdf9; border:1px solid #cfc6b7; border-radius:10px; padding:12px; box-shadow:0 5px 20px rgba(40,35,29,.12); }}
.warning {{ font-weight:700; }}
small {{ color:#655d52; }}
@media (max-width:760px) {{ .global {{ grid-template-columns:1fr; }} .page-header {{ flex-direction:column; }} }}
</style>
</head>
<body>
<main>
<section class="hero">
  <span class="eyebrow">Cora Histórico Digital · fase 2</span>
  <h1>Banco de revisión humana por página</h1>
  <p class="warning">Nada está aceptado por defecto. Cada página debe inspeccionarse personalmente; sólo entonces se habilitan sus candidatos. La exportación masiva produce únicamente decisiones <code>accept_boundary</code> para los límites que la persona revisora marque de forma expresa.</p>
  <p>Los {excluded_count} candidatos con alineación <code>inferred_sequence</code> están excluidos de este banco y permanecen en la hoja especializada de fronteras de página. Casos que requieran rechazo, fusión, división o diferimiento tampoco deben resolverse aquí.</p>
  <div class="global">
    <label>Nombre de la persona revisora<input id="reviewer" type="text" autocomplete="name" placeholder="Nombre completo"></label>
    <div class="summary"><span>Testimonio: <strong>{witness}</strong></span><span>Páginas: <strong>{manifest['review_page_total']}</strong></span><span>Candidatos disponibles: <strong>{manifest['reviewable_candidate_total']}</strong></span><span>SHA-256 PDF: <code>{source_hash}</code></span></div>
  </div>
</section>
{''.join(page_sections)}
<div class="global-actions"><button id="copy-all" type="button">Copiar todas las decisiones seleccionadas</button><button id="save-all" type="button">Guardar todas las decisiones seleccionadas</button><strong id="global-count">0 decisiones seleccionadas</strong></div>
</main>
<script>
const pageData = {client_json};
const witness = {json.dumps(manifest.get('source_witness_id', ''), ensure_ascii=False)};
const sourceHash = {json.dumps(manifest.get('source_pdf_sha256', ''), ensure_ascii=False)};

function reviewerName() {{ return document.getElementById('reviewer').value.trim(); }}
function selectedCount(section) {{ return [...section.querySelectorAll('.candidate-check')].filter(input => input.checked).length; }}
function updateCounts() {{
  let total = 0;
  document.querySelectorAll('.page-card').forEach(section => {{
    const count = selectedCount(section);
    section.querySelector('.page-count').textContent = `${{count}} seleccionados`;
    total += count;
  }});
  document.getElementById('global-count').textContent = `${{total}} decisiones seleccionadas`;
}}
function buildDecision(section, candidate) {{
  const reviewer = reviewerName();
  const confirmed = section.querySelector('.page-confirmed').checked;
  if (!reviewer) throw new Error('Escriba el nombre de la persona revisora.');
  if (!confirmed) throw new Error('Confirme primero la inspección personal de esta página.');
  const note = section.querySelector('.page-note').value.trim();
  const rationale = `Inspeccioné personalmente el facsímil de la página PDF ${{candidate.source_pdf_page}} y confirmé visualmente que este candidato corresponde a un límite de artículo.` + (note ? ` Nota de cotejo: ${{note}}` : '');
  const record = {{
    decision_id: candidate.decision_id,
    source_witness_id: witness,
    candidate_ids: [candidate.candidate_id],
    action: 'accept_boundary',
    source_pdf_pages: [candidate.source_pdf_page],
    reviewer: reviewer,
    reviewed_at: new Date().toISOString(),
    rationale: rationale,
    evidence_note: `Revisión visual del facsímil ${{section.querySelector('.facsimile img').getAttribute('src')}}; PDF SHA-256 ${{sourceHash}}.`,
    human_verified: true
  }};
  if (Number.isInteger(candidate.source_printed_page) && candidate.source_printed_page > 0) record.source_printed_pages = [candidate.source_printed_page];
  return record;
}}
function recordsForSection(section) {{
  const page = pageData[Number(section.dataset.pageIndex)];
  const byId = new Map(page.candidates.map(candidate => [candidate.candidate_id, candidate]));
  return [...section.querySelectorAll('.candidate-check:checked')].map(input => buildDecision(section, byId.get(input.dataset.candidate)));
}}
function recordsForAll() {{
  return [...document.querySelectorAll('.page-card')].flatMap(section => recordsForSection(section));
}}
function jsonl(records) {{ return records.map(record => JSON.stringify(record)).join('\n') + (records.length ? '\n' : ''); }}
function requireRecords(records) {{ if (!records.length) throw new Error('No hay candidatos seleccionados para exportar.'); }}
async function copyText(text) {{ await navigator.clipboard.writeText(text); }}
function saveText(text, filename) {{
  const blob = new Blob([text], {{type:'application/x-ndjson;charset=utf-8'}});
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a'); link.href = url; link.download = filename; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}}
function show(section, message) {{ section.querySelector('.output').textContent = message; }}

document.querySelectorAll('.page-card').forEach(section => {{
  const confirm = section.querySelector('.page-confirmed');
  const checks = [...section.querySelectorAll('.candidate-check')];
  const selectAll = section.querySelector('.select-all');
  confirm.addEventListener('change', () => {{
    checks.forEach(input => {{ input.disabled = !confirm.checked; if (!confirm.checked) input.checked = false; }});
    selectAll.disabled = !confirm.checked;
    section.querySelector('.badge').textContent = confirm.checked ? 'página inspeccionada · selección pendiente' : 'sin validar';
    updateCounts();
  }});
  checks.forEach(input => input.addEventListener('change', updateCounts));
  selectAll.addEventListener('click', () => {{ checks.forEach(input => {{ input.checked = true; }}); updateCounts(); }});
  section.querySelector('.clear-all').addEventListener('click', () => {{ checks.forEach(input => {{ input.checked = false; }}); updateCounts(); }});
  section.querySelector('.copy-page').addEventListener('click', async () => {{
    try {{ const records = recordsForSection(section); requireRecords(records); const text = jsonl(records); await copyText(text); show(section, `Copiadas ${{records.length}} decisiones JSONL.`); }}
    catch (error) {{ show(section, error.message); }}
  }});
  section.querySelector('.save-page').addEventListener('click', () => {{
    try {{ const records = recordsForSection(section); requireRecords(records); const page = pageData[Number(section.dataset.pageIndex)].source_pdf_page; saveText(jsonl(records), `ort1888-decisions-page-${{String(page).padStart(3,'0')}}.jsonl`); show(section, `Preparadas ${{records.length}} decisiones JSONL.`); }}
    catch (error) {{ show(section, error.message); }}
  }});
}});

document.getElementById('copy-all').addEventListener('click', async () => {{
  try {{ const records = recordsForAll(); requireRecords(records); await copyText(jsonl(records)); document.getElementById('global-count').textContent = `Copiadas ${{records.length}} decisiones seleccionadas`; }}
  catch (error) {{ document.getElementById('global-count').textContent = error.message; }}
}});
document.getElementById('save-all').addEventListener('click', () => {{
  try {{ const records = recordsForAll(); requireRecords(records); saveText(jsonl(records), 'ort1888-human-decisions.jsonl'); document.getElementById('global-count').textContent = `Preparadas ${{records.length}} decisiones seleccionadas`; }}
  catch (error) {{ document.getElementById('global-count').textContent = error.message; }}
}});
updateCounts();
</script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--decisions-dir", type=Path, default=DEFAULT_DECISIONS_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    candidates = validate_manifest(manifest)
    suggested_ids = allocate_decision_ids(len(candidates), existing_decision_numbers(args.decisions_dir))
    rendered = render_sheet(manifest, suggested_ids)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(
        f"built page review sheet for {manifest['review_page_total']} pages and "
        f"{len(candidates)} candidate boundaries"
    )


if __name__ == "__main__":
    main()
