# Day 9：Gold Set 执行记录

## 一句话目标

为 retrieval 和 extraction 建立项目内 gold set，让 Day 10 的指标有标准答案来源。

## 面试考点

面试官可能会问：

1. 没有 gold set 为什么不能写 recall/F1？
2. retrieval gold case 和 extraction gold case 分别长什么样？
3. 正例和负例为什么都需要？
4. 这个 gold set 的局限是什么？

## 背景/痛点

没有 gold set 的指标都是口头包装。Day 9 的目标是先创建可审计的标准答案，而不是直接追求漂亮数字。

## 统一规范

| 文件 | 要求 |
|---|---|
| `retrieval_gold_set.jsonl` | ≥20 条，包含 supported 和 unsupported |
| `extraction_gold_set.jsonl` | ≥50 条，包含 positive 和 negative |
| `gold_set_manifest.json` | 记录 case count 和 guardrails |
| `annotation_guideline.md` | 说明如何人工复核 |

## 今日交付

- `src/evidenceops_public/gold_set.py`
- `scripts/build_gold_set.py`
- `data/eval/retrieval_gold_set.jsonl`
- `data/eval/extraction_gold_set.jsonl`
- `data/eval/gold_set_manifest.json`
- `docs/annotation_guideline.md`

## 自我验证

命令：

```bash
python3 -m unittest tests.test_gold_set
python3 scripts/build_gold_set.py
```

结果：

- retrieval cases：20；
- extraction cases：50；
- positive extraction cases：12；
- negative extraction cases：38；
- supported retrieval cases：14；
- unsupported retrieval cases：6。

## 今天故意留的坑

这个 gold set 是从当前小样本自动生成的，虽然可审计，但还没有人工逐条复核。因此可以用于项目内评分，不应该直接包装成广泛质量结论。

## 面试自测题

1. 为什么 gold set 要同时包含负例？
2. 如果 gold set 是自动生成的，风险是什么？
3. retrieval case 为什么要记录 expected chunk ids？
4. extraction case 为什么要记录 evidence span？
5. 简历中写指标时必须附带哪些上下文？

