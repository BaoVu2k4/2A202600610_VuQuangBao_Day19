# Reflection — Lab 19

**Tên:** Vũ Xuân Bảo
**Cohort:** A20
**Path đã chạy:** docker (Qdrant server + Redis online store)

---

## Câu hỏi (≤ 200 chữ)

> Trên golden set 50 queries, mode nào thắng ở loại query nào (`exact` /
> `paraphrase` / `mixed`), và tại sao? Khi nào bạn **không** dùng hybrid
> (i.e. khi nào pure BM25 hoặc pure vector là lựa chọn đúng)?

Trên golden set 50 queries: BM25 thắng ở `exact` queries vì các từ kỹ thuật như
"Kubernetes", "OAuth", "PostgreSQL" xuất hiện verbatim trong corpus — BM25 khớp
chính xác term nên Precision@10 rất cao. Vector (semantic) thắng ở `paraphrase`
queries vì embedding nắm bắt được ý nghĩa kể cả khi từ ngữ khác nhau. Hybrid
(RRF k=60) thắng ở `mixed` queries và thắng trung bình tổng thể vì kết hợp cả
hai tín hiệu — BM25 xử lý exact term, vector xử lý ngữ nghĩa, RRF hợp nhất mà
không bị một retriever nào chi phối.

Không dùng hybrid khi: (1) Corpus thuần exact-match, domain rất hẹp và query
luôn dùng đúng thuật ngữ kỹ thuật — BM25 đủ, thêm vector chỉ tốn latency.
(2) Tài nguyên compute hạn chế, không muốn tốn chi phí embedding cho từng query
realtime. (3) Corpus quá nhỏ (< vài trăm docs) — vector embedding không có đủ
signal phân biệt.

---

## Điều ngạc nhiên nhất khi làm lab này

RRF với k=60 chỉ cần 5 dòng code nhưng nhất quán thắng cả BM25 lẫn vector
trên mọi loại query. Sự đơn giản của công thức tương phản với hiệu quả của nó
trong thực tế production.

---

## Bonus challenge

- [ ] Đã làm bonus (xem `bonus/`)
- [ ] Pair work với: _<tên đồng đội nếu có>_
