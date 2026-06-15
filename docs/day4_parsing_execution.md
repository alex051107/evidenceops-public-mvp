# Day 4：Parsing + Metadata 执行记录

## 一句话目标

把 Day 3 的 `document_store.jsonl` 解析成带 section 的 `parsed_documents.jsonl`，并保留 source、license、synthetic/private 边界。

## 面试考点

面试官可能会问：

1. 你为什么不直接把原始文本送进向量库？
2. 解析阶段如何防止 metadata 丢失？
3. 空文本、坏文档、格式不支持时怎么处理？
4. 为什么 Day 4 还不写 retrieval metric？

## 背景/痛点

企业文档和公开科研数据的难点不是“有文本就行”，而是每段文本都必须能追溯：

- 来自哪个 source；
- 许可是什么；
- 是否 synthetic；
- 是否 public；
- 哪些推断不能做。

如果 parsing 阶段丢掉这些字段，后面的 RAG citation、risk check、eval 都会变成不可审计。

## 停！先自己想

Day 4 的最小 parser 应该只做一件事：把 normalized document 拆成可追踪 section。它不需要马上支持复杂 PDF、OCR、表格、图片，也不应该提前做 embedding。

## 统一规范

| 字段 | 规则 |
|---|---|
| `document_id` | 继承 Day 3 document store |
| `source_id/source_url/license_status` | 必须保留 |
| `is_public_source/is_synthetic` | 必须保留 |
| `sections` | MVP 每个 document 先生成 1 个 section |
| `section_id` | 用 `document_id + text` 的 hash 生成稳定 ID |
| 空文本 | 进入 parse error，不静默成功 |
| 指标 | Day 4 不生成 recall/F1/ablation |

## 你要给 AI 的 prompt

```text
你是 Public-First EvidenceOps Agent 的 executor。
今天目标：实现 Day 4 parsing。
必须先读：
- data/processed/document_store.jsonl
- scripts/ingest_sample_documents.py
- tests/test_parser.py

请只修改：
- src/evidenceops_public/parser.py
- scripts/parse_documents.py
- docs/day4_parsing_execution.md
- docs/self_review_day4.md

要求：
1. parser 必须保留 source_url/license_status/is_synthetic/not_use_for；
2. 空文本必须进入 parse error；
3. 不做 RAG、embedding、LLM、F1、recall；
4. 先跑 unittest，再跑 parse_documents.py。
```

## 你应该收到的结果

文件：

- `src/evidenceops_public/parser.py`
- `scripts/parse_documents.py`
- `data/processed/parsed_documents.jsonl`
- `data/processed/parse_report.json`
- `data/processed/parse_errors.jsonl`

验证命令：

```bash
python3 -m unittest tests.test_parser
python3 scripts/parse_documents.py
```

## 今日交付

- parser 模块；
- parse CLI；
- parsed document store；
- parse report；
- parse error log；
- parser 单元测试。

## 自我验证

- [x] 测试先失败，失败原因是 parser/CLI 未实现；
- [x] 实现后 `python3 -m unittest tests.test_parser` 通过；
- [x] `python3 scripts/parse_documents.py` 通过；
- [x] 真实样本解析 5 条；
- [x] 公开样本 4 条、合成样本 1 条；
- [x] source/license/synthetic 字段保留；
- [x] 不输出 RAG 或指标 claim。

## 今天故意留的坑

Day 4 没有做复杂 parser：

- 不支持扫描 PDF；
- 不支持 OCR；
- 不支持表格结构识别；
- 不支持网页抓取；
- 不做 chunking。

这些进入 Day 5 chunking/citation schema 或后续 extension。

## 面试自测题

1. 为什么 parsing 阶段必须保留 license metadata？
2. 如果 parser 遇到空文本，为什么不能默默跳过？
3. 为什么 MVP 先用 one-section-per-document，而不是复杂 section tree？
4. 这个 parser 和后续 chunking 的边界是什么？
5. 你怎么证明 parser 没把 synthetic 文档伪装成 public source？

