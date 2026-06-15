# Day 0-Day 2 执行日志

日期：2026-06-15

## Day 0：Kickoff + 范围锁定

已完成：

- 创建 `evidenceops_public_mvp/` 项目骨架；
- 创建 README；
- 创建 agent 使用协议；
- 锁定公开数据优先主线；
- 明确 private LiGaMD logs 只作为 opt-in extension。

## Day 1：公开来源核验

已完成：

- 创建 `data/source_registry.csv`；
- 创建 `docs/public_data_source_decisions.md`；
- 创建 `data/raw/samples/public_source_cards.jsonl`；
- 将 JD、企业公开文档、科研公开数据、合成企业文档分层。

## Day 2：Document card + validator

已完成：

- 创建 `data/raw/samples/sample_documents.jsonl`；
- 创建 `scripts/validate_public_sources.py`；
- validator 检查 public/private/synthetic/source/license 边界。

## 尚未执行

- 未实现 ingestion；
- 未实现 parser；
- 未实现 RAG；
- 未实现 extraction；
- 未实现 scoring metrics；
- 未生成任何可写入简历的指标。

## 下一步门禁

运行：

```bash
cd /Users/liuzhenpeng/Documents/职业规划及个人/evidenceops_public_mvp
python3 scripts/validate_public_sources.py
```

只有通过后进入 Day 3 ingestion。

