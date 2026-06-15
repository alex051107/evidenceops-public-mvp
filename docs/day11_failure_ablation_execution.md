# Day 11：Failure Taxonomy + Ablation 执行记录

## 一句话目标

基于 eval report 生成 failure taxonomy，并做一个 retrieval top_k ablation。

## 面试考点

面试官可能会问：

1. 你的系统如果失败，会怎么分类？
2. retrieval miss 和 unsupported false positive 有什么区别？
3. 为什么要做 ablation？
4. top_k ablation 的局限是什么？

## 背景/痛点

一个 AI workflow 如果只展示成功 demo，很难让面试官相信你真的理解系统。Day 11 的目标是建立失败复盘语言：

- retrieval miss；
- unsupported false positive；
- retrieval status mismatch；
- extraction false negative；
- extraction false positive。

## 今日交付

- `src/evidenceops_public/failure_analysis.py`
- `scripts/analyze_failures.py`
- `data/eval/failure_taxonomy.json`
- `data/eval/ablation_report.json`
- `tests/test_failure_analysis.py`

## 自我验证

命令：

```bash
python3 -m unittest tests.test_failure_analysis
python3 scripts/analyze_failures.py
```

当前结果：

- failure analysis 单元测试：3 个通过；
- 当前 eval report 下 total failure count：0；
- ablation runs：3；
- top_k values：1、3、5；
- 每个 top_k 在当前小 gold set 上 status accuracy、supported hit rate、unsupported accuracy 均为 1.0。

## 重要限制

当前没有失败，不代表系统不会失败，只代表：

> 在当前 20 条 retrieval case、50 条 extraction case、5 个 chunks 的项目内小样本上，baseline 没有触发已定义失败类型。

不能写成：

- 系统无失败；
- 生产可用；
- 对真实企业文档鲁棒；
- top_k 参数已最优。

## 今天故意留的坑

Day 11 不做：

- semantic retrieval ablation；
- embedding model comparison；
- latency/cost benchmark；
- UI/API；
- deployment。

Day 12 进入 demo/API/UI 和上线准备。

## 面试自测题

1. 为什么 failure taxonomy 比只报 accuracy 更有价值？
2. retrieval status mismatch 为什么可能和 retrieval miss 重叠？
3. 当前 ablation 为什么不能证明 top_k=1 最优？
4. 如果换成更复杂文档，最可能出现哪类失败？
5. 你会如何扩展 failure taxonomy？

