# Evaluation dataset

Đặt câu hỏi kiểm thử vào `questions.jsonl`, mỗi dòng gồm:

```json
{"id":"academic-001","question":"Em đã học xong môn nào?","expected_sources":["danh_muc_mon_hoc.md"],"expected_intent":"academic"}
```

Bộ tối thiểu nên có 30–50 câu, chia thành academic, administrative, career và out-of-scope. Ghi lại model, embedding, `k`, thời gian chạy và kết quả để báo cáo Recall@k, MRR, tỷ lệ có nguồn, unsupported claims và latency p50/p95.
