# Day 19 Track 2 — Trạng thái và hướng dẫn hoàn thiện

> Tạo ngày 2026-06-23. Dùng để bàn giao cho Codex nếu cần tiếp tục.

## Tóm tắt trạng thái hiện tại

| Notebook | File | Trạng thái | Vấn đề |
|---|---|---|---|
| NB1 — Vector Indexing | `notebooks/01_embeddings_index.ipynb` | **DONE ✓** | 7/7 cells có output |
| NB2 — Hybrid Search | `notebooks/02_hybrid_search_rrf.ipynb` | **DONE ✓** | 5/6 cells (1 cell constants, no print = OK) |
| NB3 — API Benchmark | `notebooks/03_search_api_benchmark.ipynb` | **DONE ✓** | 5/6 cells (1 cell imports, no print = OK) |
| NB4 — Feast Feature Store | `notebooks/04_feast_feature_store.ipynb` | **DONE ✓** | 6/7 cells (1 cell imports, no print = OK) |

**Tất cả notebook đã execute xong.** Chỉ còn việc chụp screenshots và push lên GitHub.

---

## Kết quả benchmark quan trọng (rubric)

```
NB2 Precision@10:
  keyword   P@10 = 0.72
  semantic  P@10 = 0.84
  hybrid    P@10 = 0.90  ← winner (vượt 0.80 threshold) ✓

NB3 Latency:
  keyword   P50=1.9ms  P95=4.3ms  P99=5.7ms
  semantic  P50=8.9ms  P95=13.0ms P99=16.2ms
  hybrid    P50=12.2ms P95=15.7ms P99=22.2ms  ← PASS (< 50ms) ✓
```

---

## Fix đã áp dụng (cho Codex biết)

### NB3 timeout fix (Windows-specific)
**Vấn đề:** Python 3.13 + Jupyter kernel trên Windows dùng `ProactorEventLoop`. Khi ONNX 
fastembed khởi tạo thread pool bên trong async kernel, ZMQ socket drop sau vài giây → 
`CellTimeoutError` sau 600s.

**Giải pháp:** Benchmark cell chạy `scripts/run_nb3_benchmark.py` qua `subprocess.run()` 
thay vì import Searcher trực tiếp vào kernel. Subprocess process hoàn toàn thoát khỏi 
asyncio event loop của Jupyter.

```python
# NB3 cell 4 — benchmark qua subprocess
bench_result = subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "run_nb3_benchmark.py")],
    capture_output=True, text=True, encoding="utf-8", timeout=300,
    env={**os.environ, "PYTHONIOENCODING": "utf-8"},
)
print(bench_result.stdout)
```

### NB4 PIT join fix
**Vấn đề:** Entity timestamps sai thứ tự → Feast PIT join chỉ trả 2 rows thay vì 3.

**Giải pháp:** `[NOW, NOW-1h, NOW-2h]` thay vì `[NOW-2h, NOW-1h, NOW]`.

### Windows Unicode fix
Set `PYTHONIOENCODING=utf-8` trong tất cả subprocess calls.

---

## Screenshots cần chụp (cho submission)

Tất cả screenshot vào thư mục `submission/screenshots/`.

### NB1 — `01_nb1_vector_indexing.png`
Chạy notebook, chụp cell cuối cùng có output:
- Precision@10 cho in-memory Qdrant search
- Hoặc cell hiển thị "1000 docs indexed" + 1 sample search result

### NB2 — `02_nb2_hybrid_search.png`
Chụp cell hiển thị bảng Precision@10:
```
  keyword   P@10 = 0.72
  semantic  P@10 = 0.84
  hybrid    P@10 = 0.90  ← winner ✓
```

### NB3 — `03_nb3_api_benchmark.png`
Chụp 2 cells:
1. Cell 2: response API đơn (latency_ms + top-3 hits)
2. Cell 4: bảng latency benchmark + "PASS — hybrid P99 < 50ms (22.2ms)"

### NB4 — `04_nb4_feast.png`
Chụp cell hiển thị:
- `feast apply` output (Feature views registered)
- `feast materialize-incremental` output (rows pushed to Redis)
- Online features output (3 users × 3 feature views)
- Historical features PIT join output (3 rows DataFrame)

---

## Cách chụp screenshot từ Jupyter

Option 1 — Mở notebook trong Jupyter Lab:
```powershell
cd D:\AI_THUCCHIEN\NGAY19\Day19-Track2-VectorFeatureStore-Lab
$env:PYTHONIOENCODING = "utf-8"
.venv\Scripts\jupyter.exe lab
```
Vào `notebooks/`, mở từng file, Cell > Run All, chụp màn hình.

Option 2 — Đọc output từ .ipynb đã execute (không cần mở notebook):
Các file .ipynb đã có output nhúng vào. Mở bằng VS Code hoặc Jupyter Lab,
output đã hiển thị sẵn. Chụp màn hình từ đó.

---

## Push lên GitHub

Trước khi push, đảm bảo Docker containers đang chạy nếu cần test lại NB4:
```powershell
docker compose -f docker/docker-compose.yml up -d
```

Sau khi chụp screenshots:
```powershell
cd D:\AI_THUCCHIEN\NGAY19\Day19-Track2-VectorFeatureStore-Lab
$env:PYTHONIOENCODING = "utf-8"
git add -A
git commit -m "feat: execute all 4 notebooks + fix NB3 Windows benchmark + screenshots"
git push origin main
```

Remote fork: `https://github.com/BaoVu2k4/Day19-Track2-VectorFeatureStore-Lab.git`

---

## Cấu trúc project quan trọng

```
.
├── app/
│   ├── main.py              # FastAPI app (GET /search, GET /healthz)
│   ├── search.py            # Searcher class (keyword/semantic/hybrid)
│   └── feast_repo/
│       ├── feature_store.yaml   # Feast config (Redis online, file offline)
│       ├── features.py          # 3 Feature Views: user_profile, item_popularity, query_velocity
│       └── data/                # Parquet files cho offline store
├── notebooks/
│   ├── 01_embeddings_index.py/.ipynb   # Vector indexing + Qdrant in-memory
│   ├── 02_hybrid_search_rrf.py/.ipynb  # BM25 + Vector + RRF
│   ├── 03_search_api_benchmark.py/.ipynb  # FastAPI + latency benchmark
│   └── 04_feast_feature_store.py/.ipynb   # Feast online/offline store
├── scripts/
│   └── run_nb3_benchmark.py    # Standalone benchmark (bypass Jupyter/Windows issue)
├── data/
│   ├── corpus_vn.jsonl         # 1000 Vietnamese tech docs (50 topics × 20 docs)
│   ├── golden_set.jsonl        # 50 queries với ground truth topic labels
│   └── nb3_benchmark_results.json  # Benchmark results (auto-generated)
├── docker/
│   └── docker-compose.yml      # Qdrant v1.12.4 + Redis 7 + Postgres 16
├── submission/
│   ├── REFLECTION.md           # Filled (Vietnamese, ~200 words)
│   └── screenshots/            # Cần chụp 4 screenshots vào đây
├── .env                        # QDRANT_MODE=server, REDIS_URL=...
└── requirements.txt            # fastembed, qdrant-client, rank-bm25, feast, fastapi...
```

---

## Nếu cần chạy lại notebooks

```powershell
$env:PYTHONIOENCODING = "utf-8"
cd D:\AI_THUCCHIEN\NGAY19\Day19-Track2-VectorFeatureStore-Lab

# NB1
.venv\Scripts\jupytext.exe --to notebook --update notebooks/01_embeddings_index.py
.venv\Scripts\jupyter.exe nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=300 notebooks/01_embeddings_index.ipynb

# NB2
.venv\Scripts\jupytext.exe --to notebook --update notebooks/02_hybrid_search_rrf.py
.venv\Scripts\jupyter.exe nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=300 notebooks/02_hybrid_search_rrf.ipynb

# NB3 (subprocess approach - avoids Windows ZMQ timeout)
.venv\Scripts\jupytext.exe --to notebook --update notebooks/03_search_api_benchmark.py
.venv\Scripts\jupyter.exe nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=300 notebooks/03_search_api_benchmark.ipynb

# NB4 (cần Docker Redis đang chạy)
docker compose -f docker/docker-compose.yml up -d redis
.venv\Scripts\jupytext.exe --to notebook --update notebooks/04_feast_feature_store.py
.venv\Scripts\jupyter.exe nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=300 notebooks/04_feast_feature_store.ipynb
```
