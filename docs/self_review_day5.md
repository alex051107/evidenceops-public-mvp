# Day 5 自我审查

日期：2026-06-15

## 审查结论

Day 5 的 chunking + citation schema 可以进入下一阶段。当前完成的是“证据片段结构”，不是 retrieval system。

## 当前证据

命令：

```bash
cd /Users/liuzhenpeng/Documents/职业规划及个人/evidenceops_public_mvp
python3 -m unittest tests.test_chunker
python3 scripts/chunk_documents.py
```

结果：

- chunker 单元测试：3 个测试通过；
- 输入 parsed documents：5 条；
- 输出 chunks：5 条；
- chunk errors：0 条；
- synthetic chunk：1 条；
- public chunk：4 条。

## 已满足的阶段要求

| 要求 | 状态 | 证据 |
|---|---|---|
| chunk 保留 source metadata | 通过 | `chunks.jsonl` 包含 `source_id/source_url/source_type` |
| chunk 保留 license | 通过 | `chunks.jsonl` 包含 `license_status` |
| chunk 保留 synthetic 标记 | 通过 | `chunk_report.json` 中 `synthetic_chunk_count=1` |
| chunk 包含 citation | 通过 | 每条 chunk 内嵌 `citation` |
| overlap 参数有约束 | 通过 | `tests/test_chunker.py` 覆盖非法 overlap |
| 不生成检索指标 | 通过 | report 不写 recall/F1 |

## 没完成的内容

这些不能写成已完成：

- RAG retrieval；
- answer generation；
- unsupported fallback；
- citation accuracy；
- gold set；
- scoring script；
- ablation；
- API/UI；
- 部署上线。

## 风险

1. 当前 chunking 是词级窗口，不是语义 chunking。
2. 当前真实样本太短，所以每个 document 只有 1 个 chunk。
3. 还没有 retrieval ranking，不能证明“能找到正确 chunk”。
4. citation schema 已有，但还没有被 answer pipeline 使用。

## 下一阶段进入条件

Day 6 可以开始，但必须保持边界：

- 先做 lexical retrieval baseline；
- search 输出 chunks + citation；
- 无结果返回 `unsupported`；
- 不写 recall@k，直到 Day 9/10 有 gold set。

