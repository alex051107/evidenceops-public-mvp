# Day 6 自我审查

日期：2026-06-15

## 审查结论

Day 6 的 lexical retrieval baseline 可以进入下一阶段。当前系统已经能做最小 evidence search，但还不能叫完整 RAG answer system。

## 当前证据

命令：

```bash
cd /Users/liuzhenpeng/Documents/职业规划及个人/evidenceops_public_mvp
python3 -m unittest tests.test_retriever
python3 scripts/search_chunks.py --query "source license synthetic citation" --top-k 5
```

结果：

- retriever 单元测试：3 个测试通过；
- 真实查询状态：`supported`；
- evidence count：3；
- 每条 evidence 包含 citation；
- unsupported 行为：测试覆盖。

## 已满足的阶段要求

| 要求 | 状态 | 证据 |
|---|---|---|
| query 能返回 evidence chunks | 通过 | `search_result.json` |
| 每条 evidence 有 citation | 通过 | `search_result.json` evidence entries |
| 无匹配返回 unsupported | 通过 | `tests/test_retriever.py` |
| 不生成答案 | 通过 | retriever 返回 evidence，不生成自然语言 answer |
| 不写 eval metric | 通过 | 无 recall/F1/ablation |

## 没完成的内容

这些不能写成已完成：

- semantic RAG；
- embedding/vector search；
- generated answer；
- citation accuracy；
- structured extraction；
- gold set；
- scoring script；
- API/UI；
- 部署上线。

## 风险

1. lexical overlap 对同义词和语义改写很弱。
2. 当前没有 gold set，不能证明检索质量。
3. 当前只返回 evidence，不生成最终报告。
4. 当前 query demo 数据太小，不能声称覆盖真实企业文档。

## 下一阶段进入条件

Day 7 可以开始，但要保持边界：

- 只做小 schema structured extraction；
- 抽取结果必须带 evidence chunk；
- 不能使用 LLM 编造缺失字段；
- 字段不要膨胀。

