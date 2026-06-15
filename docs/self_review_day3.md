# Day 3 自我审查

日期：2026-06-15

## 审查结论

Day 3 完成的是 ingestion MVP：把 Day 2 的 sample document cards 转成规范化 processed document store。这个阶段可以进入 parser，但还不能声称已经完成文档解析、RAG、检索质量评估或 Agent 工作流。

## 当前证据

命令：

```bash
cd /Users/liuzhenpeng/Documents/职业规划及个人/evidenceops_public_mvp
python3 scripts/validate_public_sources.py
python3 scripts/ingest_sample_documents.py
```

文件证据：

- `scripts/ingest_sample_documents.py`；
- `data/processed/document_store.jsonl`；
- `data/processed/ingestion_report.json`；
- `docs/day3_ingestion_execution.md`。

## 已满足的阶段要求

| 要求 | 状态 | 证据 |
|---|---|---|
| raw cards 能进入 processed store | 通过 | `document_store.jsonl` |
| 保留 `source_id/source_url/license_status` | 通过 | processed document records |
| 保留 `is_synthetic` | 通过 | synthetic SOP 仍标记为 true |
| 生成 `text_sha256` 便于追踪 | 通过 | processed document records |
| 拒绝 private-required source 默认进入 | 通过 | validator + ingestion guardrail |
| 输出 ingestion report | 通过 | `ingestion_report.json` |

## 没完成的内容

这些不能写成已完成：

- 任意网页/API/PDF 自动抓取；
- 多格式 parser；
- section-level parsing；
- chunking；
- vector/lexical retrieval；
- LLM extraction；
- risk checker；
- gold set；
- evaluation metrics；
- frontend/backend demo；
- online deployment。

## 风险

1. 当前 ingestion 只处理 already-carded JSONL，不是通用爬虫或企业数据接入平台。
2. 样本量小，不能写“大规模 ingestion”。
3. 没有执行真实 API 请求，公开来源只作为样例和 provenance 依据。
4. ingestion 成功不等于数据质量高，只说明最小 metadata contract 已经建立。

## 下一阶段进入条件

Day 4 可以开始，但必须保持：

- parser 输出仍保留 provenance；
- parse error 必须显式记录；
- 不支持的格式要写边界，不能悄悄假装支持；
- 不在 parser 阶段提前生成 RAG 或 eval claim。
