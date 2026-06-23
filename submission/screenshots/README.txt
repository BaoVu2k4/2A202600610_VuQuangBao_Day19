Screenshots directory — Day 19 Lab submission

All deliverable evidence is captured in the executed .ipynb notebook output cells.
Add screenshots from Jupyter Lab here before final push:

NB1 (01_embeddings_index.ipynb):
  - Cell showing "Indexed: 1000 vectors"
  - Cell showing top-5 results for keyword query
  - Cell showing paraphrase query → all results from 'cloud' topic

NB2 (02_hybrid_search_rrf.ipynb):
  - Cell showing Precision@10 table: Hybrid 78.6% > Keyword 77.8% > Semantic 73.2%
  - Cell showing slice table by query type (exact/paraphrase/mixed)

NB3 (03_search_api_benchmark.ipynb):
  - Cell showing single query API response with latency_ms
  - Cell showing P50/P95/P99 table for keyword/semantic/hybrid
  - Cell showing "PASS — hybrid P99 < 50ms"

NB4 (04_feast_feature_store.ipynb):
  - Cell showing "feast apply" STDOUT with 3 feature views registered
  - Cell showing "materialize-incremental" log → redis online store
  - Cell showing online lookup result for u_001
  - Cell showing P99 = 6.67ms PASS
  - Cell showing PIT join DataFrame (3 rows x features)
