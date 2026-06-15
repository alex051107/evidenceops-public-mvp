# Day 7 自我审查

日期：2026-06-15

## 审查结论

Day 7 的 structured extraction baseline 可以进入下一阶段。当前完成的是规则型小 schema 抽取，不是 LLM 抽取系统，也不是已评测的抽取模型。

## 当前证据

命令：

```bash
cd /Users/liuzhenpeng/Documents/职业规划及个人/evidenceops_public_mvp
python3 -m unittest tests.test_extractor
python3 scripts/extract_fields.py
```

结果：

- extractor 单元测试：3 个测试通过；
- 输入 chunks：5 条；
- matched chunks：5 条；
- unmatched chunks：0 条；
- extraction count：12；
- field types：`skill_signal`、`workflow_signal`、`source_constraint`。

## 已满足的阶段要求

| 要求 | 状态 | 证据 |
|---|---|---|
| 只抽小 schema | 通过 | `field_type_counts` 只有三类 |
| 每条抽取有 evidence_span | 通过 | `extractions.jsonl` |
| 每条抽取有 citation | 通过 | `tests/test_extractor.py` 和输出文件 |
| 不编造无规则字段 | 通过 | unmatched 机制存在 |
| 不写抽取指标 | 通过 | report 无 F1/precision/recall |

## 没完成的内容

这些不能写成已完成：

- LLM structured output；
- schema validation framework；
- extraction accuracy；
- gold set；
- risk check；
- answer generation；
- API/UI；
- 部署上线。

## 风险

1. 当前规则很少，覆盖面有限。
2. 当前所有真实样本都匹配到规则，是因为样本文本较短且围绕项目设计。
3. 规则型抽取不能处理同义改写。
4. 没有人工 gold set，不能声称抽取质量。

## 下一阶段进入条件

Day 8 可以开始：

- risk check 必须检查 unsupported claims、synthetic misuse、license-sensitive claims；
- 不能把 risk check 写成合规系统；
- 只能输出 warning/error，不替用户做法律或医疗判断。

