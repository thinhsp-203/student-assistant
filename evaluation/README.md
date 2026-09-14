# Evaluation dataset

`questions.jsonl` là bộ dữ liệu kiểm thử có 36 câu, chia đều cho
`academic`, `administrative`, `career` và `out-of-scope`. Mỗi dòng gồm:

```json
{"id":"academic-001","question":"Em đã học xong môn nào?","expected_sources":["danh_muc_mon_hoc.md"],"expected_intent":"academic"}
```

Bộ tối thiểu nên có 30–50 câu, chia thành academic, administrative, career và out-of-scope. Ghi lại model, embedding, `k`, thời gian chạy và kết quả để báo cáo Recall@k, MRR, tỷ lệ có nguồn, unsupported claims và latency p50/p95.

Kiểm tra schema và xem thống kê:

```bash
python evaluation/validate_dataset.py
```

Có thể truyền đường dẫn JSONL khác làm đối số để kiểm tra bộ dữ liệu mới.
