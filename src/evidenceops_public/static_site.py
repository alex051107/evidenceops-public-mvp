"""Static-site export for GitHub Pages fallback deployment."""

from __future__ import annotations

import json
from pathlib import Path

from evidenceops_public.demo_app import build_search_response, build_summary_payload, load_chunks


ROOT = Path(__file__).resolve().parents[2]


def build_static_payload(root: Path = ROOT) -> dict:
    chunks = load_chunks(root)
    return {
        "status": "ok",
        "mode": "static",
        "summary": build_summary_payload(root),
        "default_query": "source license synthetic citation",
        "default_search": build_search_response("source license synthetic citation", chunks, intended_use="project_demo"),
        "unsupported_demo": build_search_response("unmatched astrophysics volcano", chunks, intended_use="project_demo"),
        "guardrails": [
            "static export is a demo artifact, not a live backend",
            "citations and risk flags are preserved in exported JSON",
            "metrics are limited to the project-local gold set",
        ],
    }


def render_static_index() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EvidenceOps Static Console</title>
  <style>
    :root {
      --ink: #17211d;
      --paper: #f6f6ef;
      --panel: #ffffff;
      --line: #c7cec2;
      --moss: #4c6b4f;
      --copper: #ad5a3a;
      --steel: #506674;
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
      background: #e9eee5;
      border-right: 1px solid var(--line);
      padding: 28px 22px;
    }
    main { padding: 28px; }
    h1 {
      margin: 0 0 10px;
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(2rem, 4vw, 4rem);
      line-height: 0.95;
    }
    .lead { max-width: 760px; color: #3d4b42; }
    .rail {
      border-left: 3px solid var(--moss);
      padding-left: 12px;
      margin: 12px 0;
      font-size: 0.92rem;
    }
    .grid {
      display: grid;
      grid-template-columns: minmax(0, 1.25fr) minmax(280px, 0.75fr);
      gap: 18px;
      margin-top: 26px;
      align-items: start;
    }
    section {
      background: var(--panel);
      border: 1px solid var(--line);
      padding: 18px;
    }
    h2 { margin: 0 0 12px; color: var(--steel); font-size: 1rem; }
    pre { white-space: pre-wrap; overflow-wrap: anywhere; font-size: 0.85rem; }
    .evidence { border-top: 1px solid var(--line); margin-top: 12px; padding-top: 12px; }
    .source { color: var(--copper); font-size: 0.82rem; overflow-wrap: anywhere; }
    .status { display: inline-block; border: 1px solid var(--line); padding: 3px 8px; background: #f1f3ed; }
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
      <div class="rail">No citation, no claim</div>
      <div class="rail">Public / synthetic boundaries visible</div>
      <div class="rail">Unsupported remains a valid result</div>
      <div class="rail">Metrics include dataset size</div>
    </aside>
    <main>
      <h1>EvidenceOps Static Console</h1>
      <p class="lead">This GitHub Pages fallback shows the same project evidence package without a backend. It loads <code>evidenceops-data.json</code> and renders citations, risk flags, eval summary, and unsupported behavior.</p>
      <div class="grid">
        <section>
          <h2>Default evidence search</h2>
          <div id="evidence"></div>
        </section>
        <section>
          <h2>Eval and risk summary</h2>
          <pre id="summary">Loading...</pre>
        </section>
      </div>
    </main>
  </div>
  <script>
    function renderEvidence(payload) {
      const search = payload.default_search.search;
      const risk = payload.default_search.risk;
      const rows = [`<span class="status">${search.status}</span> risk: ${risk.status}`];
      for (const item of search.evidence) {
        rows.push(`<div class="evidence"><strong>#${item.rank} score ${item.score}</strong><p>${item.text}</p><div class="source">${item.citation.source_url}<br>${item.citation.license_status}</div></div>`);
      }
      rows.push(`<h2>Unsupported demo</h2><pre>${JSON.stringify(payload.unsupported_demo.search, null, 2)}</pre>`);
      document.getElementById('evidence').innerHTML = rows.join('');
    }
    function renderSummary(payload) {
      const summary = {
        dataset_size: payload.summary.eval.dataset_size,
        retrieval: payload.summary.eval.retrieval,
        extraction: payload.summary.eval.extraction,
        failure_count: payload.summary.failure_taxonomy.total_failure_count,
        ablation_runs: payload.summary.ablation.runs,
        guardrails: payload.guardrails
      };
      document.getElementById('summary').textContent = JSON.stringify(summary, null, 2);
    }
    fetch('evidenceops-data.json')
      .then(response => response.json())
      .then(payload => {
        renderEvidence(payload);
        renderSummary(payload);
      })
      .catch(error => {
        document.getElementById('summary').textContent = String(error);
      });
  </script>
</body>
</html>
"""


def build_static_site(output_dir: Path, *, root: Path = ROOT) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_static_payload(root)
    (output_dir / "index.html").write_text(render_static_index(), encoding="utf-8")
    (output_dir / "evidenceops-data.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / ".nojekyll").write_text("", encoding="utf-8")
    return {
        "status": "ok",
        "output_dir": str(output_dir),
        "files": ["index.html", "evidenceops-data.json", ".nojekyll"],
    }

