# Day N：标题

## 一句话目标

今天只完成一个清晰目标，不顺手扩范围。

## 面试考点

面试官可能会问：

1. 你为什么这样设计？
2. 这个模块的输入输出是什么？
3. 如果数据坏了、来源不明、没有证据，你怎么处理？
4. 你怎么验证它真的工作？

## 背景/痛点

把今天要解决的问题重新讲清楚，不假设读者记得前一天。

## 停！先自己想

先回答：

- 今天的数据从哪里来？
- 是否公开、是否能追溯许可？
- 最小可运行版本是什么？
- 哪些内容今天不做？

## 统一规范/决策表

| 项目 | 决策 | 原因 | 替代方案 | 什么时候不用 |
|---|---|---|---|---|
| 数据源 | 待填 | 待填 | 待填 | 待填 |
| schema | 待填 | 待填 | 待填 | 待填 |
| validator | 待填 | 待填 | 待填 | 待填 |

## 你要给 AI 的 prompt

```text
你是 EvidenceOps Agent 项目的 executor。
今天目标：<填今天目标>。
必须先读这些文件：
- <路径 1>
- <路径 2>

请只修改这些文件：
- <路径范围>

输出要求：
1. 说明你新增/修改了哪些文件；
2. 给出如何运行验证；
3. 不得写 production、clinical、真实客户、真实患者、HIPAA/GDPR；
4. 如果缺少公开来源或许可，请停止并标记 DATA_INSUFFICIENT。
```

## 你应该收到的结果

你应该收到：

- 文件 A：结构是什么；
- 文件 B：结构是什么；
- 验证命令；
- 失败时的错误信息应该可读。

如果 AI 输出了无法追溯来源的结论，追问：

```text
请给出每条结论对应的 source_url、retrieved_at、license_status 和 not_use_for。
没有来源的结论请删掉或标为 unsupported。
```

## 今日交付

- `path/to/file_a`
- `path/to/file_b`
- `path/to/validator`

## 自我验证

- [ ] 每个 public source 有 URL；
- [ ] 每个 document card 有 license；
- [ ] synthetic 数据标记为 `is_synthetic=true`；
- [ ] 无 private data 进入默认样例；
- [ ] validator 通过；
- [ ] 没有不能写的 claim。

## 今天故意留的坑

今天故意不解决：

- <坑 1>
- <坑 2>

这些坑会在 Day <N+1> 或 Phase <X> 解决。

## 面试自测题

1. 为什么你的项目要做 source registry？
2. 为什么不能直接把所有公开网页抓下来？
3. synthetic enterprise docs 在项目里的边界是什么？
4. 如果一个 claim 没有 citation，系统应该怎么处理？
5. 你今天的模块怎么测试？

