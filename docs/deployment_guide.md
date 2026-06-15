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

3. Render Blueprint：

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

## Render 上线步骤

1. 把 `evidenceops_public_mvp/` 放到 GitHub 仓库根目录，或调整 `render.yaml` 的 Dockerfile 路径。
2. 在 Render 选择 New Blueprint。
3. 连接 GitHub 仓库。
4. 确认 web service 使用 Docker 环境。
5. 部署后访问 `/healthz`。
6. 再访问 `/api/summary` 和 `/api/search?q=source%20license%20synthetic%20citation`。

## 不能声称的内容

- 不能说已生产部署；
- 不能说高并发；
- 不能说企业客户正在使用；
- 不能说 HIPAA/GDPR compliance；
- 没有公网 URL 前不能说已经上线。

