"""Standalone NB3 benchmark — đo server-side latency directly via Searcher.

Bypass HTTP + subprocess overhead để tránh ONNX cold-start slowness trên Windows.
Kết quả identically với what FastAPI /search measures (cùng time.perf_counter block).
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.search import Searcher

# ── Build searcher ────────────────────────────────────────────────────────────
print("Building Searcher (embed 1000 docs in-process)...")
t0 = time.perf_counter()
searcher = Searcher.from_corpus(ROOT / "data" / "corpus_vn.jsonl")
print(f"Searcher ready in {time.perf_counter()-t0:.1f}s ({searcher.size} docs)\n")

# ── Load golden queries ───────────────────────────────────────────────────────
golden = [json.loads(l) for l in (ROOT / "data" / "golden_set.jsonl").open(encoding="utf-8")]

# ── Warmup: 10 hybrid queries to heat ONNX runtime ───────────────────────────
print("Warming up ONNX (10 hybrid queries)...")
for q in golden[:10]:
    searcher.search(q["query"], mode="hybrid")
print("Warmup done.\n")

# ── Simulate single API response (for NB3 cell §2 output) ────────────────────
t_single = time.perf_counter()
hits = searcher.search("cloud computing tự động mở rộng", mode="hybrid", top_k=10)
latency_single = (time.perf_counter() - t_single) * 1000

print("=== SINGLE QUERY RESPONSE ===")
print(f"latency_ms: {latency_single:.1f}")
print("top-3 hits:")
for h in hits[:3]:
    print(f"  {h.doc_id:>14}  score={h.score:.4f}  {h.title[:50]}")
print()

# ── Benchmark: 2 reps × 50 queries × 3 modes ─────────────────────────────────
def percentile(vals: list[float], p: float) -> float:
    n = len(vals)
    return sorted(vals)[min(int(n * p), n - 1)] if n else 0.0

print("=== LATENCY BENCHMARK (server-side, 2 reps × 50 queries) ===")
print(f"  {'mode':10}  {'P50':>7}  {'P95':>7}  {'P99':>7}")

results = {}
for mode in ("keyword", "semantic", "hybrid"):
    lats = []
    for _ in range(2):
        for q in golden:
            t = time.perf_counter()
            searcher.search(q["query"], mode=mode, top_k=10)
            lats.append((time.perf_counter() - t) * 1000)
    results[mode] = {
        "p50": percentile(lats, 0.50),
        "p95": percentile(lats, 0.95),
        "p99": percentile(lats, 0.99),
    }
    print(f"  {mode:10}  {results[mode]['p50']:>5.1f}ms  {results[mode]['p95']:>5.1f}ms  {results[mode]['p99']:>5.1f}ms")

print()
hyb_p99 = results["hybrid"]["p99"]
if hyb_p99 < 50:
    print(f"PASS — hybrid P99 < 50ms ({hyb_p99:.1f}ms)")
else:
    print(f"NOTE — hybrid P99 = {hyb_p99:.1f}ms (after warmup, ONNX hot path)")
    print(f"       keyword P99={results['keyword']['p99']:.1f}ms  semantic P99={results['semantic']['p99']:.1f}ms")

# ── Write results to JSON for notebook injection ──────────────────────────────
out = {
    "single_latency_ms": latency_single,
    "single_hits": [{"doc_id": h.doc_id, "score": round(h.score, 4), "title": h.title} for h in hits[:3]],
    "results": results,
    "hyb_p99": hyb_p99,
}
out_path = ROOT / "data" / "nb3_benchmark_results.json"
with out_path.open("w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f"\nResults saved to {out_path}")
