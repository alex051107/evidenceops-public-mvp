# Agent 使用协议

## 总原则

Agent 用来做并行侦察和互相审查，不用来替代事实核验。所有结论必须回到公开来源、URL、日期和许可。

## 分工

| Agent | 任务 | 输出 | 停止条件 |
|---|---|---|---|
| designer / Codex | 主线整合、计划、验收 | 计划书、任务拆解、最终判断 | 发现来源不明或范围膨胀 |
| data scout | 查公开数据源、许可、API | source candidate table | 无官方来源或许可不明 |
| JD scout | 查官方 JD、技能、workflow | JD evidence table | 只找到论坛/培训软文 |
| architecture planner | 技术栈 why/alternative/when-not | stack decision memo | 为了关键词硬加技术 |
| eval skeptic | 审查 gold set、metric、unsupported claim | eval risk memo | 指标没有脚本或数据 |
| executor | 写脚本和文件 | 代码、schema、样例数据 | 写入范围冲突 |
| reviewer | 验证 artifact 和红线 | review checklist | 出现 cannot-write claim |

## 调用规则

1. 只把非阻塞任务交给 agent；
2. 需要本地立即决定的任务由主线程完成；
3. 写文件的 agent 必须有明确且不重叠的文件范围；
4. agent 输出不能直接进入简历或报告，必须由主线程审查；
5. source 事实必须来自官方或一手资料；
6. forum/community 只记录为低置信 market signal；
7. 如果 agent 和官方来源冲突，保留官方来源并记录冲突。

## 本项目默认 agent 流水线

```text
data scout 查来源 -> designer 合并 -> executor 写 registry/schema -> reviewer 跑 validator -> eval skeptic 检查是否能进入下一阶段
```

## 不能让 agent 做的事

- 不能生成虚假实习；
- 不能把 synthetic data 写成真实企业数据；
- 不能绕过许可；
- 不能把医学注册/标签数据写成医疗建议；
- 不能没有 gold set 就生成指标；
- 不能用“企业级”“生产级”“高并发”包装未实现内容。

