"""Small stdlib web demo for the EvidenceOps MVP."""

from __future__ import annotations

import json
from pathlib import Path

from evidenceops_public.parser import read_jsonl
from evidenceops_public.retriever import search_chunks
from evidenceops_public.risk_checker import check_search_result


ROOT = Path(__file__).resolve().parents[2]


def read_json(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        return default or {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_chunks(root: Path = ROOT) -> list[dict]:
    path = root / "data" / "processed" / "chunks.jsonl"
    if not path.exists():
        return []
    return read_jsonl(path)


def build_search_response(query: str, chunks: list[dict], *, intended_use: str = "project_demo", top_k: int = 5) -> dict:
    search_result = search_chunks(query, chunks, top_k=top_k)
    risk_report = check_search_result(search_result, intended_use=intended_use)
    return {
        "status": "ok",
        "search": search_result,
        "risk": risk_report,
    }


def build_summary_payload(root: Path = ROOT) -> dict:
    return {
        "status": "ok",
        "eval": read_json(root / "data" / "eval" / "eval_report.json", default={"status": "missing"}),
        "failure_taxonomy": read_json(root / "data" / "eval" / "failure_taxonomy.json", default={"status": "missing"}),
        "ablation": read_json(root / "data" / "eval" / "ablation_report.json", default={"status": "missing"}),
        "gold_manifest": read_json(root / "data" / "eval" / "gold_set_manifest.json", default={"status": "missing"}),
    }


def render_index() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EvidenceOps Console</title>
  <style>
    :root {
      --ink: #18201c;
      --paper: #f7f7f2;
      --line: #c9cec3;
      --moss: #4c6b4f;
      --copper: #b45b38;
      --steel: #4b6473;
      --panel: #ffffff;
      --warn: #8a4a08;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }
    .shell {
      display: grid;
      grid-template-columns: 280px minmax(0, 1fr);
      min-height: 100vh;
    }
    aside {
      border-right: 1px solid var(--line);
      padding: 28px 22px;
      background: #ecefe6;
    }
    main { padding: 28px; }
    h1 {
      margin: 0 0 12px;
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(2rem, 4vw, 4rem);
      line-height: 0.95;
      max-width: 900px;
    }
    .thesis {
      max-width: 760px;
      color: #3f4b43;
      font-size: 1.02rem;
    }
    .rail-title {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--steel);
      margin-bottom: 16px;
    }
    .rail-item {
      border-left: 3px solid var(--moss);
      padding: 8px 0 8px 12px;
      margin: 10px 0;
      font-size: 0.92rem;
    }
    .toolbar {
      margin: 28px 0 18px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    input, select, button {
      font: inherit;
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--ink);
      min-height: 42px;
    }
    input {
      flex: 1 1 360px;
      padding: 0 12px;
    }
    select { padding: 0 10px; }
    button {
      padding: 0 16px;
      background: var(--ink);
      color: white;
      cursor: pointer;
    }
    button:focus, input:focus, select:focus {
      outline: 3px solid rgba(180, 91, 56, 0.28);
      outline-offset: 2px;
    }
    .grid {
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(260px, 0.65fr);
      gap: 18px;
      align-items: start;
    }
    section {
      border: 1px solid var(--line);
      background: var(--panel);
      padding: 18px;
    }
    h2 {
      margin: 0 0 12px;
      font-size: 1rem;
      color: var(--steel);
    }
    pre {
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      margin: 0;
      font-size: 0.86rem;
    }
    .evidence {
      border-top: 1px solid var(--line);
      padding-top: 12px;
      margin-top: 12px;
    }
    .source {
      color: var(--copper);
      font-size: 0.82rem;
      overflow-wrap: anywhere;
    }
    .status {
      display: inline-block;
      padding: 3px 8px;
      border: 1px solid var(--line);
      background: #f3f4ee;
      margin-bottom: 10px;
      font-size: 0.82rem;
    }
    .warning { color: var(--warn); }
    @media (max-width: 820px) {
      .shell { grid-template-columns: 1fr; }
      aside { border-right: 0; border-bottom: 1px solid var(--line); }
      main { padding: 20px; }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <aside>
      <div class="rail-title">Evidence rail</div>
      <div class="rail-item">No citation, no claim</div>
      <div class="rail-item">Public / synthetic boundaries stay visible</div>
      <div class="rail-item">Unsupported is a valid answer</div>
      <div class="rail-item">Metrics report dataset size</div>
    </aside>
    <main>
      <h1>Evidence Console</h1>
      <p class="thesis">Search a small public-first EvidenceOps index. The console returns evidence chunks, citations, and risk flags; it does not generate production claims.</p>
      <form class="toolbar" id="search-form">
        <input id="query" name="query" value="source license synthetic citation" aria-label="Search query">
        <select id="intended-use" aria-label="Intended use">
          <option value="project_demo">project_demo</option>
          <option value="real_customer_data">real_customer_data</option>
          <option value="synthetic_demo">synthetic_demo</option>
        </select>
        <button type="submit">Search evidence</button>
      </form>
      <div class="grid">
        <section>
          <h2>Evidence</h2>
          <div id="evidence-output"><span class="status">Waiting</span></div>
        </section>
        <section>
          <h2>Eval Summary</h2>
          <pre id="summary-output">Loading...</pre>
        </section>
      </div>
    </main>
  </div>
  <script>
    async function loadSummary() {
      const res = await fetch('/api/summary');
      const data = await res.json();
      const small = {
        dataset_size: data.eval.dataset_size,
        retrieval: data.eval.retrieval,
        extraction: data.eval.extraction,
        failure_count: data.failure_taxonomy.total_failure_count,
        ablation_runs: data.ablation.runs
      };
      document.getElementById('summary-output').textContent = JSON.stringify(small, null, 2);
    }
    function renderEvidence(data) {
      const search = data.search;
      const risk = data.risk;
      const rows = [`<span class="status">${search.status}</span> <span class="${risk.status === 'ok' ? '' : 'warning'}">risk: ${risk.status}</span>`];
      if (search.evidence.length === 0) {
        rows.push(`<p>${search.reason || 'No evidence returned.'}</p>`);
      }
      for (const item of search.evidence) {
        rows.push(`<div class="evidence"><strong>#${item.rank} score ${item.score}</strong><p>${item.text}</p><div class="source">${item.citation.source_url}<br>${item.citation.license_status}</div></div>`);
      }
      if (risk.risks.length) {
        rows.push(`<h2>Risk flags</h2><pre>${JSON.stringify(risk.risks, null, 2)}</pre>`);
      }
      document.getElementById('evidence-output').innerHTML = rows.join('');
    }
    document.getElementById('search-form').addEventListener('submit', async (event) => {
      event.preventDefault();
      const query = encodeURIComponent(document.getElementById('query').value);
      const intendedUse = encodeURIComponent(document.getElementById('intended-use').value);
      const res = await fetch(`/api/search?q=${query}&intended_use=${intendedUse}`);
      renderEvidence(await res.json());
    });
    loadSummary();
    document.getElementById('search-form').dispatchEvent(new Event('submit'));
  </script>
</body>
</html>
"""

