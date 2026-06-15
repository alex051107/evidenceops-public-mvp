# Day 8 自我审查

日期：2026-06-15

## 审查结论

Day 8 的 source-aware risk check 可以进入下一阶段。当前完成的是项目级风险标记，不是生产合规系统。

## 当前证据

命令：

```bash
cd /Users/liuzhenpeng/Documents/职业规划及个人/evidenceops_public_mvp
python3 -m unittest tests.test_risk_checker
python3 scripts/risk_check.py --search-result data/processed/search_result.json --intended-use project_demo --output data/processed/risk_report.json
python3 scripts/risk_check.py --search-result data/processed/search_unsupported_result.json --intended-use project_demo --output data/processed/risk_unsupported_report.json
```

结果：

- risk checker 单元测试：3 个测试通过；
- supported search risk：1 个 warning，类型为 synthetic source；
- unsupported search risk：1 个 warning，类型为 unsupported query；
- missing citation：测试覆盖；
- not_use_for conflict：测试覆盖。

## 已满足的阶段要求

| 要求 | 状态 | 证据 |
|---|---|---|
| unsupported query 被标记 | 通过 | `risk_unsupported_report.json` |
| missing citation 被标记 | 通过 | `tests/test_risk_checker.py` |
| synthetic misuse 被标记 | 通过 | `risk_report.json` |
| not_use_for conflict 被标记 | 通过 | `tests/test_risk_checker.py` |
| 不写合规能力 | 通过 | 文档和 guardrails 明确非合规系统 |

## 没完成的内容

这些不能写成已完成：

- HIPAA/GDPR compliance；
- medical/legal advice guardrail；
- production moderation；
- human approval workflow；
- gold set；
- scoring script；
- API/UI；
- 部署上线。

## 风险

1. 当前 risk check 规则很少。
2. 只能检查 search result，尚未检查 extraction results。
3. 没有人工审核界面。
4. 没有把 risk report 接入最终 answer generation。

## 下一阶段进入条件

Day 9 可以开始 gold set：

- gold cases 必须小而人工可审；
- 每条 case 指向 chunk/citation；
- 不写指标，直到 Day 10 scoring script 跑出结果。

