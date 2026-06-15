# Day 12：Demo API/UI + Deployment Prep 执行记录

## 一句话目标

把 EvidenceOps MVP 从脚本流水线推进到可访问的本地 Web/API demo，并补齐 Docker/Render 部署文件。

## 面试考点

面试官可能会问：

1. 你的项目怎么演示？
2. API 返回什么？
3. UI 是否保留 citation 和 risk？
4. 本地 demo 和 production deployment 的边界是什么？

## 当前 Demo

启动命令：

```bash
python3 scripts/run_demo_server.py --host 127.0.0.1 --port 8765
```

本地地址：

```text
http://127.0.0.1:8765/
```

API：

| Endpoint | 用途 |
|---|---|
| `/healthz` | 健康检查 |
| `/api/summary` | 返回 eval/failure/ablation 摘要 |
| `/api/search?q=...&intended_use=...` | 返回 evidence chunks + citation + risk |
| `/` | Evidence Console 页面 |

## UI 设计边界

这个界面是内部操作台，不是营销落地页。它的视觉重点是：

- 左侧 evidence rail，强调 no citation/no claim；
- 主区域输入 query；
- 右侧展示 eval summary；
- evidence 区展示 citation 和 risk flags。

## 今日交付

- `src/evidenceops_public/demo_app.py`
- `scripts/run_demo_server.py`
- `Dockerfile`
- `.dockerignore`
- `render.yaml`
- `tests/test_demo_app.py`

## 自我验证

命令：

```bash
python3 -m unittest tests.test_demo_app
python3 scripts/run_demo_server.py --host 127.0.0.1 --port 8765
```

HTTP 验证：

- `/healthz` 返回 200；
- `/api/summary` 返回 200；
- `/api/search` 返回 200；
- `/` 返回 200 HTML。

## 部署状态

当前完成的是：

- 本地可运行 Web demo；
- Dockerfile；
- Render blueprint。

尚未完成的是：

- 真正推送到 GitHub；
- 连接 Render/Vercel/Fly.io 账号；
- 获得公网 URL；
- 线上健康检查。

所以目前不能说“已经正式上线”，只能说“已具备部署上线的工程入口，且本地服务已验证”。

## 面试自测题

1. 为什么用 stdlib HTTP server，而不是一开始上 FastAPI？
2. 这个 demo 的 API 和生产 API 差别是什么？
3. 为什么 UI 要展示 risk flags？
4. Dockerfile 能证明什么，不能证明什么？
5. 如果要真正上线，还缺哪些外部步骤？

