# Deployment Guide

## 当前部署形态

项目当前支持三种运行方式：

1. 本地 Python：

```bash
python3 scripts/run_demo_server.py --host 127.0.0.1 --port 8765
```

2. Docker：

```bash
docker build -t evidenceops-public-mvp .
docker run --rm -p 8765:8765 evidenceops-public-mvp
```

3. GitHub Pages static fallback：

```bash
python3 scripts/build_static_site.py --output-dir public
git subtree push --prefix public origin gh-pages
```

4. Render Blueprint：

`render.yaml` 已提供 Docker web service 配置。

## 上线前检查

```bash
python3 scripts/validate_public_sources.py
python3 scripts/ingest_sample_documents.py
python3 scripts/parse_documents.py
python3 scripts/chunk_documents.py
python3 scripts/search_chunks.py --query "source license synthetic citation" --top-k 5
python3 scripts/search_chunks.py --query "unmatched astrophysics volcano" --output data/processed/search_unsupported_result.json
python3 scripts/extract_fields.py
python3 scripts/risk_check.py --search-result data/processed/search_result.json --intended-use project_demo --output data/processed/risk_report.json
python3 scripts/risk_check.py --search-result data/processed/search_unsupported_result.json --intended-use project_demo --output data/processed/risk_unsupported_report.json
python3 scripts/build_gold_set.py
python3 scripts/score_eval.py
python3 scripts/analyze_failures.py
python3 -m unittest discover -s tests
```

## 当前线上部署

已上线 GitHub Pages 静态版本：

```text
https://alex051107.github.io/evidenceops-public-mvp/
```

线上 smoke test：

```bash
python3 - <<'PY'
from urllib.request import urlopen
import json

with urlopen("https://alex051107.github.io/evidenceops-public-mvp/", timeout=10) as r:
    assert r.status == 200
    assert "EvidenceOps Static Console" in r.read().decode("utf-8")

with urlopen("https://alex051107.github.io/evidenceops-public-mvp/evidenceops-data.json", timeout=10) as r:
    data = json.loads(r.read().decode("utf-8"))
    assert data["status"] == "ok"
    assert data["default_search"]["search"]["status"] == "supported"
PY
```

## Render 上线步骤

1. 把 `evidenceops_public_mvp/` 放到 GitHub 仓库根目录，或调整 `render.yaml` 的 Dockerfile 路径。
2. 在 Render 选择 New Blueprint。
3. 连接 GitHub 仓库。
4. 确认 web service 使用 Docker 环境。
5. 部署后访问 `/healthz`。
6. 再访问 `/api/summary` 和 `/api/search?q=source%20license%20synthetic%20citation`。

## GitHub Pages 上线步骤

1. 确保 `public/index.html` 和 `public/evidenceops-data.json` 存在。
2. 推送主分支到 GitHub。
3. 推送 `public/` 到 `gh-pages` 分支。
4. 在 GitHub Pages 设置里选择 `gh-pages` branch `/root`，或用 GitHub API 配置 Pages。
5. 访问 `https://<owner>.github.io/<repo>/`。

## 不能声称的内容

- 不能说已生产部署；
- 不能说高并发；
- 不能说企业客户正在使用；
- 不能说 HIPAA/GDPR compliance；
- 没有公网 URL 前不能说已经上线。
