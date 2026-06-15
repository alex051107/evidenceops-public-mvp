# Annotation Guideline

## 目的

`data/eval/` 下的 gold set 用于项目内评测，不代表真实生产质量。每个 case 必须能追溯到公开或 synthetic source、chunk、citation。

## Retrieval Case

每条 retrieval case 至少包含：

- `case_id`
- `query`
- `expected_status`
- `expected_chunk_ids`
- `expected_source_ids`
- `citation_required`
- `notes`

标注规则：

1. 如果 query 应该返回证据，`expected_status=supported`，且 `expected_chunk_ids` 不能为空。
2. 如果 query 不应该返回证据，`expected_status=unsupported`，且 `expected_chunk_ids=[]`。
3. supported case 必须要求 citation。
4. 不允许把 synthetic evidence 当真实企业数据。

## Extraction Case

每条 extraction case 至少包含：

- `case_id`
- `chunk_id`
- `field_type`
- `field_value`
- `expected_present`
- `evidence_span`
- `citation`
- `notes`

标注规则：

1. `expected_present=true` 时，`evidence_span` 必须来自 chunk 原文。
2. `expected_present=true` 时，citation 必须有 source_url 和 license_status。
3. `expected_present=false` 是负例，不要求 evidence_span。
4. 字段只允许小 schema：`skill_signal`、`workflow_signal`、`source_constraint`。

## 使用限制

- 这个 gold set 很小，不能代表真实企业文档总体质量。
- 简历里如果写指标，必须写 dataset size、case count、scoring script。
- 没有人工复核前，不写“生产级”“企业级”“高准确率”。

