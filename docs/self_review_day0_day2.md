# Day 0-Day 2 自我审查

日期：2026-06-15

## 审查结论

Day 0-Day 2 完成的是项目立项、公开数据优先边界、source registry、sample document cards 和 public-source validator。这个阶段可以进入 ingestion，但还不能声称已经实现 RAG、Agent、评估体系或部署。

## 当前证据

命令：

```bash
cd /Users/liuzhenpeng/Documents/职业规划及个人/evidenceops_public_mvp
python3 scripts/validate_public_sources.py
```

文件证据：

- `README.md`：说明项目定位和不使用私人 LiGaMD 日志作为默认数据；
- `docs/agent_usage_protocol.md`：规定 agent 使用和边界；
- `docs/public_data_source_decisions.md`：记录公开数据源选择；
- `data/source_registry.csv`：登记公开/合成/禁用来源；
- `data/raw/samples/public_source_cards.jsonl`：公开来源卡片；
- `data/raw/samples/sample_documents.jsonl`：样例 document cards；
- `scripts/validate_public_sources.py`：source/license/synthetic/private 边界校验。

## 已满足的阶段要求

| 要求 | 状态 | 证据 |
|---|---|---|
| 主线从私人科研日志改为公开数据优先 | 通过 | `README.md` 和 `docs/public_data_source_decisions.md` |
| 区分真实公开来源和合成企业文档 | 通过 | `data/source_registry.csv`、`sample_documents.jsonl` |
| 保留 license 和 not-use-for 边界 | 通过 | source card 与 validator 校验 |
| 私有/不可默认使用来源不进入 MVP 默认流 | 通过 | validator 拦截 private-required source |
| 形成后续 ingestion 的统一输入 | 通过 | `sample_documents.jsonl` |

## 没完成的内容

这些不能写成已完成：

- ingestion pipeline；
- parser；
- chunking；
- RAG；
- citation-grounded retrieval；
- structured extraction；
- risk check；
- eval harness；
- UI/API；
- online deployment。

## 风险

1. 当前数据是 seed dataset，不是大规模企业数据集。
2. O*NET、SEC、PMC、ChEMBL 等公开来源只作为项目可行性和证据边界样例，不代表实时 JD 或完整企业知识库。
3. 合成 SOP 只能写成 synthetic enterprise document，不能写成真实客户流程。
4. 这个阶段没有指标，不能写任何 recall、accuracy、latency 或 cost claim。

## 下一阶段进入条件

Day 3 可以开始，但必须保持：

- raw source metadata 不能在 ingestion 中丢失；
- private-required source 默认拒绝；
- synthetic 标记必须一路保留；
- ingestion report 只能报告处理状态，不能生成能力指标。
