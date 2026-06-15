# Day 5：Chunking + Citation Schema 执行记录

## 一句话目标

把 `parsed_documents.jsonl` 转成带 citation metadata 的 `chunks.jsonl`。

## 面试考点

面试官可能会问：

1. chunk 为什么不能只是文本？
2. citation 应该包含哪些字段？
3. overlap 设置过大会发生什么？
4. chunking 和 retrieval 的边界是什么？

## 背景/痛点

RAG 里最容易被忽略的问题是：检索到了文本，但不知道文本来自哪里，是否可复用，是否 synthetic，能不能用于某类结论。Day 5 的目标是让每个 chunk 都天然带上 citation。

## 停！先自己想

如果一个 chunk 只有 `text`，后面生成回答时就无法回答：

- 这句话来自哪个 source？
- 能不能被引用？
- 是否 synthetic？
- 是否有不能推断的边界？
- 出问题后如何回溯？

## 统一规范

| 字段 | 规则 |
|---|---|
| `chunk_id` | 由 document、section、span、text hash 生成 |
| `section_id` | 必须继承 parser 输出 |
| `source_url` | 必须保留 |
| `license_status` | 必须保留 |
| `is_synthetic` | 必须保留 |
| `citation` | 内嵌 document/source/span/license |
| `not_use_for` | 必须保留，防止越界推断 |
| `overlap_words` | 必须小于 `max_words` |

## 你要给 AI 的 prompt

```text
你是 Public-First EvidenceOps Agent 的 executor。
今天目标：实现 Day 5 chunking + citation schema。
必须先读：
- data/processed/parsed_documents.jsonl
- src/evidenceops_public/parser.py
- tests/test_chunker.py

请只修改：
- src/evidenceops_public/chunker.py
- scripts/chunk_documents.py
- docs/day5_chunking_execution.md
- docs/self_review_day5.md

要求：
1. 每个 chunk 必须带 source_url、license_status、is_synthetic、section_id、char span；
2. 每个 chunk 必须内嵌 citation 对象；
3. overlap_words >= max_words 时必须失败；
4. 不做 embedding、RAG ranking、LLM、F1、recall。
```

## 你应该收到的结果

文件：

- `src/evidenceops_public/chunker.py`
- `scripts/chunk_documents.py`
- `data/processed/chunks.jsonl`
- `data/processed/chunk_report.json`
- `data/processed/chunk_errors.jsonl`

验证命令：

```bash
python3 -m unittest tests.test_chunker
python3 scripts/chunk_documents.py
```

## 今日交付

- chunker 模块；
- chunk CLI；
- citation-aware chunk store；
- chunk report；
- chunk 单元测试。

## 自我验证

- [x] 测试先失败，失败原因是 chunker/CLI 未实现；
- [x] 实现后 `python3 -m unittest tests.test_chunker` 通过；
- [x] `python3 scripts/chunk_documents.py` 通过；
- [x] 真实样本生成 5 个 chunk；
- [x] 每个 chunk 有 citation；
- [x] source/license/synthetic 字段保留；
- [x] 不输出 retrieval 或 metric claim。

## 今天故意留的坑

Day 5 不做：

- embedding；
- vector store；
- BM25；
- query ranking；
- answer generation；
- recall@k。

Day 6 才开始做 retrieval baseline。

## 面试自测题

1. 为什么 RAG chunk 必须保留 citation metadata？
2. chunk overlap 的 tradeoff 是什么？
3. 什么时候 chunk 太大，什么时候 chunk 太小？
4. 如果一个 chunk 来自 synthetic doc，后续回答应该怎么标注？
5. 为什么 Day 5 不能写 recall@k？

