# Day 8：Source-Aware Risk Check 执行记录

## 一句话目标

对 search result 做 source-aware risk check，拦住 unsupported、missing citation、synthetic misuse、not_use_for 冲突。

## 面试考点

面试官可能会问：

1. 为什么 RAG 系统需要 risk check？
2. `unsupported` 为什么不能被包装成回答？
3. synthetic 数据为什么必须显式标记？
4. 这个 risk check 为什么不是合规系统？

## 背景/痛点

这个项目的核心红线是“no citation, no claim”。但是只有 citation 还不够，还要防止：

- 检索失败却生成答案；
- citation 缺失；
- synthetic SOP 被当成真实客户数据；
- `not_use_for` 已经写了禁止用途但下游仍然使用。

Day 8 只做项目级 guardrail，不做法律、医疗或隐私合规判断。

## 停！先自己想

先回答：

- 如果 query 是 unsupported，简历或报告能不能写结论？
- 如果 evidence 来自 synthetic doc，能不能说“企业客户数据”？
- 如果 source 的 `not_use_for` 包含当前 intended use，系统应该 warning 还是 error？
- risk check 是否能替代法律合规审查？

## 统一规范

| 风险 | 严重级别 | 处理 |
|---|---|---|
| `unsupported_query` | warning | 不生成 claim |
| `missing_citation` | error | 不允许作为证据 |
| `synthetic_source_used_for_non_synthetic_context` | warning | 必须标 synthetic |
| `not_use_for_conflict` | error | 当前 intended use 不允许 |

## 你要给 AI 的 prompt

```text
你是 Public-First EvidenceOps Agent 的 executor。
今天目标：实现 Day 8 source-aware risk check。
必须先读：
- data/processed/search_result.json
- data/processed/search_unsupported_result.json
- tests/test_risk_checker.py

请只修改：
- src/evidenceops_public/risk_checker.py
- scripts/risk_check.py
- docs/day8_risk_check_execution.md
- docs/self_review_day8.md

要求：
1. unsupported query 必须被标为 warning；
2. missing citation 必须被标为 error；
3. synthetic evidence 在非 synthetic 场景必须被 warning；
4. not_use_for 与 intended_use 冲突必须 error；
5. 明确说明这不是法律/医疗/合规系统。
```

## 你应该收到的结果

文件：

- `src/evidenceops_public/risk_checker.py`
- `scripts/risk_check.py`
- `data/processed/risk_report.json`
- `data/processed/risk_unsupported_report.json`

验证命令：

```bash
python3 -m unittest tests.test_risk_checker
python3 scripts/risk_check.py --search-result data/processed/search_result.json --intended-use project_demo --output data/processed/risk_report.json
python3 scripts/risk_check.py --search-result data/processed/search_unsupported_result.json --intended-use project_demo --output data/processed/risk_unsupported_report.json
```

## 今日交付

- risk checker 模块；
- risk check CLI；
- supported search risk report；
- unsupported risk report；
- risk checker 单元测试。

## 自我验证

- [x] 测试先失败，失败原因是 risk_checker/CLI 未实现；
- [x] 实现后 `python3 -m unittest tests.test_risk_checker` 通过；
- [x] supported search 中 synthetic evidence 被 warning；
- [x] unsupported query 被 warning；
- [x] missing citation 测试覆盖；
- [x] not_use_for conflict 测试覆盖。

## 今天故意留的坑

Day 8 不做：

- 法律合规判断；
- 医疗建议判断；
- 自动删除证据；
- human approval workflow；
- production guardrail。

Day 9/10 才做 gold set 和 scoring。

## 面试自测题

1. 为什么 risk check 不能只看 answer text？
2. missing citation 为什么是 error？
3. synthetic evidence 可以被用在什么场景？
4. `not_use_for` 和 license 有什么区别？
5. 为什么这个模块不能写成 HIPAA/GDPR compliance？

