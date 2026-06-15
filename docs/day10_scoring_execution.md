# Day 10：Scoring Script + Eval Report 执行记录

## 一句话目标

用 Day 9 gold set 生成可复现 eval report，并显式记录 dataset size。

## 面试考点

面试官可能会问：

1. 你的指标是怎么跑出来的？
2. 指标对应多少条 case？
3. supported retrieval 和 unsupported retrieval 怎么分别算？
4. extraction precision/recall 的定义是什么？

## 背景/痛点

AI 项目简历里最危险的是写“效果显著提升”“准确率很高”，但没有脚本和数据。Day 10 的目标是把指标绑定到：

- gold set；
- scoring script；
- dataset size；
- eval report。

## 今日交付

- `src/evidenceops_public/scoring.py`
- `scripts/score_eval.py`
- `data/eval/eval_report.json`
- `tests/test_scoring.py`

## 自我验证

命令：

```bash
python3 -m unittest tests.test_scoring
python3 scripts/score_eval.py
```

当前结果：

- retrieval cases：20；
- chunks：5；
- extraction cases：50；
- extractions：12；
- retrieval status accuracy：1.0；
- supported hit rate：1.0；
- unsupported accuracy：1.0；
- extraction presence accuracy：1.0；
- extraction precision：1.0；
- extraction recall：1.0。

## 重要限制

这些 1.0 只能解释为：

> 在当前 5 个 chunk、20 条 retrieval case、50 条 extraction case 的小型项目内 gold set 上，规则型 baseline 与自动生成 case 一致。

不能解释为：

- 真实企业文档总体准确率；
- 生产级系统质量；
- 对任意文档都有效；
- 可以直接写“高准确率”。

## 今天故意留的坑

Day 10 还没有做：

- ablation；
- failure taxonomy；
- manual review；
- API/UI；
- deployment。

Day 11 解决 failure taxonomy 和 ablation。

## 面试自测题

1. 你的 retrieval hit rate 怎么定义？
2. 为什么要把 dataset size 写进 eval report？
3. extraction false positive 和 false negative 分别是什么？
4. 为什么当前 1.0 不能写成“模型准确率 100%”？
5. 如果 gold set 变大，哪些指标可能下降？

