# 公开数据源决策表

生成日期：2026-06-15

## 采用原则

MVP 采用“小而可追溯”的公开数据。目标不是全量下载，而是先用 100-300 条高质量证据建立完整 workflow。

## 主数据源

| source_id | 决策 | 理由 | 用途 |
|---|---|---|---|
| local_jd_skill_matrix | selected | 已在本地结构化，适合做 JD skill seed | Job Intelligence |
| onet | selected | 官方职业技能 taxonomy，适合对齐技能标签 | Skill normalization |
| sec_edgar | selected | 企业公开 filings，适合模拟 enterprise documents | Enterprise Knowledge |
| chembl | selected | 官方结构化 bioactivity 下载清晰 | Scientific transfer |
| pubchem | selected | 官方 PUG/REST 可查 compound metadata | Entity enrichment |
| pmc_oa | selected_with_license_filter | 可复用全文但逐篇许可不同 | Scientific full text |
| rcsb_pdb | selected | 官方结构和 metadata API | Structure evidence |
| dailymed | selected | 药品标签公开 API | Label evidence |
| clinicaltrials | selected_as_registry_evidence | 公开 trial registry，但不是 peer-reviewed efficacy | Trial registry |
| synthetic_enterprise_docs | selected_as_synthetic | 补企业 SOP/FAQ/会议纪要形态 | Workflow demo |

## 不作为默认数据源

| source_id | 决策 | 理由 |
|---|---|---|
| private_ligamd_logs | opt_in_only | 不公开，不适合作为默认 demo、benchmark、简历指标 |
| linkedin_indeed_glassdoor | rejected_for_mvp | ToS 和反爬风险高 |
| paywalled_publisher_fulltext | rejected | 版权和访问风险高 |
| kaggle_or_hf_mirrors | extension_only | 可缓存实验，但必须回链官方来源 |

## 公开数据样例计划

最小 seed：

- `imatinib`
- `aspirin`
- `bortezomib`
- `gefitinib`
- `tanespimycin`

每个 seed 最多取：

- PubChem compound metadata 1 条；
- ChEMBL activity 20-100 条；
- RCSB PDB structure metadata 1-3 条；
- DailyMed label 1-3 条；
- PubMed/PMC OA evidence 5-20 条；
- ClinicalTrials.gov trial registry 5-10 条。

限制：

- 不写临床结论；
- 不跨 assay 直接比较活性；
- 不把 registry 数据当 peer-reviewed evidence；
- 不用私人 MD/LiGaMD 日志做默认评测。

