# Online Deployment Self Review

日期：2026-06-15

## 线上地址

GitHub Pages：

```text
https://alex051107.github.io/evidenceops-public-mvp/
```

静态数据：

```text
https://alex051107.github.io/evidenceops-public-mvp/evidenceops-data.json
```

GitHub 仓库：

```text
https://github.com/alex051107/evidenceops-public-mvp
```

## 线上验证证据

已验证：

- Pages API status：`built`；
- Pages source：`gh-pages` branch `/`；
- 首页 URL 返回 HTTP 200；
- 首页包含 `EvidenceOps Static Console`；
- `evidenceops-data.json` 返回 HTTP 200；
- 静态 JSON `status=ok`；
- default search：`supported`，evidence count = 3；
- eval dataset size：20 retrieval cases、50 extraction cases。

## 当前上线形态

当前真正上线的是 GitHub Pages 静态版本：

- 不需要后端；
- 加载 `evidenceops-data.json`；
- 展示默认 evidence search；
- 展示 unsupported demo；
- 展示 eval/failure/ablation summary；
- 保留 citation、risk、dataset-size guardrails。

## 未上线的部分

这些没有线上后端部署：

- `/api/search` 动态接口；
- `/api/summary` 动态接口；
- Docker backend；
- Render/Fly/Vercel backend service。

原因：

- 本机 Docker CLI 存在，但 Docker daemon 未运行；
- Render/Fly/Vercel CLI 不在本机；
- 当前已用 GitHub Pages 完成公开静态上线，满足项目展示与简历 demo 链接的最低上线要求。

## 不能夸大的内容

不能写：

- production deployment；
- high-concurrency backend；
- live API service；
- enterprise customer deployment；
- production monitoring；
- HIPAA/GDPR compliance。

可以写：

- deployed a static GitHub Pages demo for the public-source EvidenceOps project；
- shipped a local API/UI demo plus a public static console；
- published source code, static evidence package, eval report, failure taxonomy, and deployment guide。

