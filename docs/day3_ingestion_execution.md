# Day 3：Ingestion MVP 执行记录

## 一句话目标

把 Day 2 的 sample document cards 读入一个规范化 processed document store。

## 面试考点

面试官会看你是否能讲清楚：

- raw data 和 processed data 的区别；
- source metadata 为什么不能丢；
- synthetic/private/public 的边界如何在 ingestion 阶段保留；
- 为什么 Day 3 不急着做 RAG。

## 背景/痛点

公开数据来自多个来源：API 文档、下载页、许可说明、合成 SOP。它们格式不同，但后续 parser、chunking、retrieval 都需要统一入口。Day 3 的目标就是建立这个入口。

## 停！先自己想

- 进入 processed store 的最小字段是什么？
- 如果 source 是 private，是否应该默认 ingest？
- 如果 source_url 或 license 缺失，是否应该继续？
- 今天是否需要算 recall@k？答案是不需要。

## 今日交付

- `scripts/ingest_sample_documents.py`
- `data/processed/document_store.jsonl`
- `data/processed/ingestion_report.json`

## 自我验证

```bash
cd /Users/liuzhenpeng/Documents/职业规划及个人/evidenceops_public_mvp
python3 scripts/validate_public_sources.py
python3 scripts/ingest_sample_documents.py
```

验收：

- processed store 每条都有 `source_id/source_url/license_status/is_synthetic/text_sha256`；
- private-required source 被拒绝；
- synthetic 文档仍然标记；
- 不生成任何 RAG 或指标结论。

## 今天故意留的坑

Day 3 只处理 already-carded documents，不处理任意 PDF/网页/API 抓取。Day 4 再处理 parser 和 parse error log。

