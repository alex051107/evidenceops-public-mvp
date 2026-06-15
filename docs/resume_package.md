# Resume Package

## 可写前提

只有在以下命令通过后，才可以写项目指标：

```bash
python3 scripts/score_eval.py
python3 scripts/analyze_failures.py
python3 -m unittest discover -s tests
```

## 当前可写 bullets 草案

AI Application / RAG 方向：

- Built a public-source EvidenceOps demo that ingests audited source cards, preserves license/synthetic metadata, creates citation-aware chunks, and returns unsupported when no evidence is found.
- Implemented lexical retrieval, small-schema structured extraction, source-aware risk checks, and a project-local evaluation harness over 20 retrieval cases and 50 extraction cases.
- Shipped a local web console and Docker-ready deployment entrypoint for inspecting evidence chunks, citations, risk flags, eval summaries, and failure taxonomy.
- Published a GitHub Pages static demo with source code, evidence package, eval report, failure taxonomy, and deployment documentation.

Data / MLOps 方向：

- Designed reproducible JSONL-based data contracts for source registry, document store, parsed sections, evidence chunks, extraction labels, gold sets, eval reports, and failure analysis.
- Added validation and scoring scripts to prevent private data leakage, missing citations, unsupported claims, and metric reporting without dataset-size context.

## 必须附带的限定语

- 数据是 public/synthetic project-local samples；
- 当前 gold set 是 20 retrieval cases + 50 extraction cases；
- 指标只适用于当前项目内评测；
- 本地 demo 已验证，公网部署仍需平台连接。
- 公网静态 demo 已发布；动态 API 后端仍是本地 demo，不写 production API。

## 不能写

- Internship；
- production deployment；
- real customer；
- real patient data；
- HIPAA/GDPR compliance；
- high-concurrency distributed system；
- ChEMBL-scale ingestion；
- clinical decision support；
- 动态 API 已线上投产。
