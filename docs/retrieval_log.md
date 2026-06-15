# Retrieval Log

日期：2026-06-15

## 使用规则

每次新增来源或技术判断，都补一行。官方来源优先；论坛/博客只能做低置信参考。

| date | query_or_url | source_type | credibility | used_for | decision | reason |
|---|---|---|---|---|---|---|
| 2026-06-15 | https://chembl.gitbook.io/chembl-interface-documentation/downloads | official_download_doc | high | ChEMBL source registry | selected | 官方下载页列出 release、格式和 DOI，可作为结构化 bioactivity 来源 |
| 2026-06-15 | https://pmc.ncbi.nlm.nih.gov/tools/openftlist/ | official_license_doc | high | PMC OA source registry | selected_with_license_filter | 官方说明 OA subset 可复用但逐篇许可不同，且自动化检索服务有限定 |
| 2026-06-15 | https://www.ncbi.nlm.nih.gov/home/develop/api/ | official_api_doc | high | PubChem/NCBI API decision | selected | NCBI 官方 API 页列出 E-utilities、PubChem PUG 和 PMC APIs |
| 2026-06-15 | https://www.rcsb.org/docs/programmatic-access/web-apis-overview | official_api_doc | high | RCSB source registry | selected | 官方说明 Data API/Search API 与 JSON 输出 |
| 2026-06-15 | https://dailymed.nlm.nih.gov/dailymed/webservices-help/v2/spls_api.cfm | official_api_doc | high | DailyMed source registry | selected | 官方 REST API 支持 SPL 查询和 XML/JSON 输出 |
| 2026-06-15 | https://www.nlm.nih.gov/pubs/techbull/ma24/ma24_clinicaltrials_api.html | official_announcement | high | ClinicalTrials.gov API decision | selected_as_registry_evidence | NLM 公告说明 v2 REST API、OpenAPI 3.0 和 JSON 返回 |
| 2026-06-15 | https://www.sec.gov/search-filings/edgar-application-programming-interfaces | official_api_doc | high | SEC enterprise document source | selected | 官方说明 data.sec.gov REST JSON APIs 不需要认证或 API key |
| 2026-06-15 | https://services.onetcenter.org/reference/ | official_api_doc | high | O*NET skill taxonomy | selected | 官方说明 REST GET JSON、需要注册、API key、license agreement |

