# Day 4 自我审查

日期：2026-06-15

## 审查结论

Day 4 的 parsing 层可以进入下一阶段，但只代表“解析为 sectioned document store”完成，不代表 RAG、抽取、eval 或部署完成。

## 当前证据

命令：

```bash
cd /Users/liuzhenpeng/Documents/职业规划及个人/evidenceops_public_mvp
python3 -m unittest tests.test_parser
python3 scripts/parse_documents.py
```

结果：

- parser 单元测试：3 个测试通过；
- 真实 document store 输入：5 条；
- parsed document 输出：5 条；
- parse error：0 条；
- public document：4 条；
- synthetic document：1 条。

## 已满足的阶段要求

| 要求 | 状态 | 证据 |
|---|---|---|
| 保留 source metadata | 通过 | `parsed_documents.jsonl` 包含 `source_id/source_url/source_type` |
| 保留 license | 通过 | `parsed_documents.jsonl` 包含 `license_status` |
| 保留 synthetic 标记 | 通过 | `synthetic_document_count=1` |
| 空文本进入 parse error | 通过 | `tests/test_parser.py` 覆盖空文本 |
| CLI 可复跑 | 通过 | `scripts/parse_documents.py` 输出 report |
| 不生成指标 claim | 通过 | report 只统计 parse count，不写 F1/recall |

## 没完成的内容

这些不能写成已完成：

- RAG；
- citation-grounded answer；
- structured extraction；
- risk check；
- gold set；
- scoring script；
- ablation；
- API/UI；
- 部署上线。

## 风险

1. 目前 parser 只做 one-section-per-document，后续 chunking 需要更细的 span。
2. 当前样本较小，不能代表真实 ChEMBL/PMC/SEC 大规模格式复杂度。
3. 没有实际请求 API，只是先建立公开来源和样例 schema。
4. 不支持 PDF/OCR/表格，不能在简历里写“支持多格式企业文档解析”。

## 下一阶段进入条件

Day 5 可以开始，但必须保持边界：

- 只做 chunking + citation schema；
- 不直接上 LLM；
- 不写指标；
- 每个 chunk 必须保留 `document_id/source_url/license_status/is_synthetic/section_id`。

