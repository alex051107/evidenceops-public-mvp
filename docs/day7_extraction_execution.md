# Day 7：Structured Extraction Baseline 执行记录

## 一句话目标

在 evidence chunks 上做一个小而可解释的规则型 structured extraction，只抽 `skill_signal`、`workflow_signal`、`source_constraint` 三类字段。

## 面试考点

面试官可能会问：

1. 为什么先做规则型抽取，而不是直接用 LLM？
2. 每条抽取如何证明不是编出来的？
3. 为什么字段数量要小？
4. 没有 gold set 时能不能写 extraction F1？

## 背景/痛点

企业 AI 应用中，结构化抽取的风险是字段越做越多，最后每个字段都讲不清来源。Day 7 刻意只做三类：

- `skill_signal`：技能/能力信号；
- `workflow_signal`：工作流能力信号；
- `source_constraint`：来源/许可/不能推断的约束。

每条抽取都必须有：

- `chunk_id`
- `field_type`
- `field_value`
- `evidence_span`
- `citation`

## 停！先自己想

先回答：

- 哪些字段是真正需要的？
- 每个字段能不能回到原文片段？
- 如果字段没有证据，是否应该空着？
- 当前能不能写“准确率”？答案是不能。

## 统一规范

| 字段 | 规则 |
|---|---|
| `field_type` | 仅限小 schema |
| `field_value` | 必须来自规则匹配 |
| `evidence_span` | 必须是 chunk text 中的原文片段 |
| `citation` | 必须继承 chunk citation |
| unmatched chunk | 记录到 unmatched，不编造字段 |
| metric | 不写 F1/precision/recall |

## 你要给 AI 的 prompt

```text
你是 Public-First EvidenceOps Agent 的 executor。
今天目标：实现 Day 7 structured extraction baseline。
必须先读：
- data/processed/chunks.jsonl
- src/evidenceops_public/retriever.py
- tests/test_extractor.py

请只修改：
- src/evidenceops_public/extractor.py
- scripts/extract_fields.py
- docs/day7_extraction_execution.md
- docs/self_review_day7.md

要求：
1. 只抽 skill_signal/workflow_signal/source_constraint；
2. 每条抽取必须有 evidence_span 和 citation；
3. 没有规则匹配不能编字段；
4. 不使用 LLM；
5. 不写 F1、precision、recall。
```

## 你应该收到的结果

文件：

- `src/evidenceops_public/extractor.py`
- `scripts/extract_fields.py`
- `data/processed/extractions.jsonl`
- `data/processed/extraction_report.json`
- `data/processed/extraction_unmatched_chunks.jsonl`

验证命令：

```bash
python3 -m unittest tests.test_extractor
python3 scripts/extract_fields.py
```

## 今日交付

- 规则型 extractor；
- extraction CLI；
- extraction result store；
- unmatched chunk log；
- extraction report；
- extractor 单元测试。

## 自我验证

- [x] 测试先失败，失败原因是 extractor/CLI 未实现；
- [x] 实现后 `python3 -m unittest tests.test_extractor` 通过；
- [x] 真实样本抽取 12 条；
- [x] 5 个 chunk 都有规则匹配；
- [x] 每条抽取保留 citation；
- [x] 不输出 extraction metric。

## 今天故意留的坑

Day 7 不做：

- LLM extraction；
- JSON schema validation with Pydantic；
- field-level F1；
- human annotation；
- risk check。

Day 8 做 risk check；Day 9/10 才做 gold set 和 scoring。

## 面试自测题

1. 为什么小 schema 比大而全的 schema 更适合 MVP？
2. 如果 LLM 抽取了没有证据的字段，系统应该怎么处理？
3. evidence_span 和 citation 的区别是什么？
4. 为什么当前不能写 extraction F1？
5. 什么时候应该从规则型抽取升级到 LLM 抽取？

