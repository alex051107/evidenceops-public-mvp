# Public-First EvidenceOps Agent MVP

这个目录是 EvidenceOps Agent 的公开数据优先执行版。它不使用私人 LiGaMD 日志作为默认数据源，也不把合成企业文档伪装成真实客户资料。

## Online Demo

GitHub Pages:

```text
https://alex051107.github.io/evidenceops-public-mvp/
```

Repository:

```text
https://github.com/alex051107/evidenceops-public-mvp
```

当前线上版本是静态 Evidence Console，用 `public/evidenceops-data.json` 展示 evidence、citation、risk flags、eval summary 和 failure/ablation summary。动态 `/api/search` 后端仍只在本地 demo server 中运行。

## 当前阶段

已启动 Day 0-Day 12：

1. Day 0：锁定公开数据策略和 cannot-write 边界；
2. Day 1：登记公开来源、许可、API/下载方式和限制；
3. Day 2：创建 document card 样例和 validator。
4. Day 3：把 sample documents ingest 成 processed document store。
5. Day 4：把 processed documents parse 成 sectioned document store。
6. Day 5：把 parsed documents chunk 成带 citation metadata 的 evidence chunks。
7. Day 6：在 chunks 上实现 lexical retrieval baseline 和 unsupported fallback。
8. Day 7：在 chunks 上实现小 schema 规则型 structured extraction。
9. Day 8：对 search result 实现 source-aware risk check。
10. Day 9：生成 retrieval/extraction gold set 和 annotation guideline。
11. Day 10：生成 scoring script 和 eval report。
12. Day 11：生成 failure taxonomy 和 retrieval top_k ablation report。
13. Day 12：生成本地 Web/API demo、Dockerfile、Render blueprint 和简历包草案。

后续需要完成外部平台部署，拿到公网 URL 后才算真正上线。

## 目录

```text
evidenceops_public_mvp/
  data/
    source_registry.csv
    raw/samples/public_source_cards.jsonl
    raw/samples/sample_documents.jsonl
    processed/
  docs/
    agent_usage_protocol.md
    public_data_source_decisions.md
    day0_day2_execution_log.md
  scripts/
    validate_public_sources.py
    ingest_sample_documents.py
    parse_documents.py
    chunk_documents.py
    search_chunks.py
    extract_fields.py
    risk_check.py
    build_gold_set.py
    score_eval.py
    analyze_failures.py
    run_demo_server.py
  src/evidenceops_public/
  tests/
```

## 验证

```bash
cd /Users/liuzhenpeng/Documents/职业规划及个人/evidenceops_public_mvp
python3 scripts/validate_public_sources.py
python3 scripts/ingest_sample_documents.py
python3 scripts/parse_documents.py
python3 scripts/chunk_documents.py
python3 scripts/search_chunks.py --query "source license synthetic citation" --top-k 5
python3 scripts/extract_fields.py
python3 scripts/risk_check.py --search-result data/processed/search_result.json --intended-use project_demo --output data/processed/risk_report.json
python3 scripts/build_gold_set.py
python3 scripts/score_eval.py
python3 scripts/analyze_failures.py
python3 scripts/run_demo_server.py --host 127.0.0.1 --port 8765
python3 -m unittest tests.test_parser
python3 -m unittest tests.test_chunker
python3 -m unittest tests.test_retriever
python3 -m unittest tests.test_extractor
python3 -m unittest tests.test_risk_checker
python3 -m unittest tests.test_gold_set
python3 -m unittest tests.test_scoring
python3 -m unittest tests.test_failure_analysis
python3 -m unittest tests.test_demo_app
```

通过条件：

- 每条 source 有 URL、license、access method、decision；
- 默认数据源不依赖 private LiGaMD；
- 每条 sample document 有 source、license、is_synthetic；
- synthetic 数据明确标记；
- 不出现 patient data、clinical advice、production claim。
- parsed documents 保留 source、license、synthetic metadata。
- chunks 内嵌 citation metadata，且不生成未评测指标。
- retrieval 只返回 evidence chunks；无匹配时返回 `unsupported`。
- extraction 只抽小 schema，且每条结果必须有 evidence span 和 citation。
- risk check 只做项目护栏，不写成法律、医疗或合规系统。
- eval 指标必须带 dataset size；当前指标只适用于小型项目内 gold set。
- failure taxonomy 和 ablation 也是小样本项目内报告，不能泛化为生产质量。
- 本地 Web demo 已实现；没有公网 URL 前不能声称正式上线。

## 当前红线

- 不写实习；
- 不写真实客户；
- 不写真实患者数据；
- 不写 clinical / HIPAA / GDPR；
- 不写 production deployment；
- 不写 high-concurrency distributed system；
- 不写 ChEMBL-scale ingestion；
- 无 gold set 不写 F1、recall@k、ablation 数字。
