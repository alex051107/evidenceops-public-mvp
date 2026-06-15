# Day 6：Lexical Retrieval + Unsupported 执行记录

## 一句话目标

在 `chunks.jsonl` 上实现一个最小 lexical retrieval baseline：能返回 citation-aware evidence，找不到就返回 `unsupported`。

## 面试考点

面试官可能会问：

1. 为什么先做 lexical baseline，而不是直接上 embedding？
2. `unsupported` 对企业 AI 应用为什么重要？
3. 检索结果和最终答案有什么区别？
4. 为什么现在不能写 recall@k？

## 背景/痛点

很多 RAG demo 一上来就做 LLM answer，但没有先证明系统能稳定返回证据。Day 6 只解决最小问题：

```text
query -> matched chunks -> citations
```

如果没有匹配证据，系统必须返回 `unsupported`，不能为了看起来智能而编答案。

## 停！先自己想

先回答：

- 如果 query 没有匹配 chunk，系统应该输出什么？
- 如果 chunk 是 synthetic，检索结果里要不要暴露？
- lexical baseline 有什么局限？
- 没有 gold set 时能不能写 recall@k？

## 统一规范

| 项目 | 决策 |
|---|---|
| retrieval 方法 | `lexical_term_overlap` |
| 返回对象 | evidence chunks，不是 LLM answer |
| 无匹配 | `status=unsupported` |
| citation | 每条 evidence 必须保留 |
| metric | 不写 recall@k/F1 |
| 后续升级 | Day 9/10 有 gold set 后再评测 |

## 你要给 AI 的 prompt

```text
你是 Public-First EvidenceOps Agent 的 executor。
今天目标：实现 Day 6 lexical retrieval baseline。
必须先读：
- data/processed/chunks.jsonl
- src/evidenceops_public/chunker.py
- tests/test_retriever.py

请只修改：
- src/evidenceops_public/retriever.py
- scripts/search_chunks.py
- docs/day6_retrieval_execution.md
- docs/self_review_day6.md

要求：
1. 查询只返回 evidence chunks 和 citation；
2. 没有匹配时返回 unsupported；
3. 保留 source_url/license_status/is_synthetic/not_use_for；
4. 不生成 LLM answer；
5. 不写 recall@k/F1/ablation。
```

## 你应该收到的结果

文件：

- `src/evidenceops_public/retriever.py`
- `scripts/search_chunks.py`
- `data/processed/search_result.json`

验证命令：

```bash
python3 -m unittest tests.test_retriever
python3 scripts/search_chunks.py --query "source license synthetic citation" --top-k 5
```

## 今日交付

- lexical retriever；
- search CLI；
- supported query demo；
- unsupported 行为测试；
- retrieval 单元测试。

## 自我验证

- [x] 测试先失败，失败原因是 retriever/CLI 未实现；
- [x] 实现后 `python3 -m unittest tests.test_retriever` 通过；
- [x] 真实 query 返回 3 条 evidence；
- [x] 每条 evidence 保留 citation；
- [x] unsupported 行为由测试覆盖；
- [x] 不输出 LLM answer 或 eval metric。

## 今天故意留的坑

Day 6 不做：

- embedding；
- vector DB；
- semantic retrieval；
- reranking；
- answer generation；
- recall@k。

Day 7/8 才做结构化抽取和 risk check；Day 9/10 才做 gold set 和 scoring。

## 面试自测题

1. 为什么 lexical baseline 仍然有价值？
2. `unsupported` 和“回答不知道”有什么工程区别？
3. 检索结果为什么必须带 citation？
4. 为什么现在不能写 retrieval recall？
5. 什么时候应该从 lexical baseline 升级到 embedding search？

