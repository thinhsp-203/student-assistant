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

## Retrieval benchmark

`benchmark.py` chỉ đo retrieval, không gọi LLM. Với mỗi câu hỏi, script ghi
latency (ms), source hit rate (ít nhất một `expected_sources` xuất hiện trong
top-k), và `source_coverage_at_k` (số expected source xuất hiện chia cho tổng
expected source). Summary có p50/p95 latency và trung bình của hai metric
source. Tài liệu không có `expected_sources` được loại khỏi source metrics.

Kiểm tra dataset/configuration mà không cần API key hoặc Chroma:

```powershell
backend\venv\Scripts\python.exe evaluation\benchmark.py --dry-run
```

Chạy benchmark thật (cần `GOOGLE_API_KEY` và index đã được ingest):

```powershell
$env:GOOGLE_API_KEY = "..."
backend\venv\Scripts\python.exe evaluation\benchmark.py --k 5 --output benchmark.json
backend\venv\Scripts\python.exe evaluation\benchmark.py --k 5 --output-format csv --output benchmark.csv
```

Kết quả bị thiếu API key hoặc thư mục Chroma sẽ có `status: "blocked"` và
exit code khác 0; script không tạo số liệu giả. JSON có `summary` và từng
case trong `results`; CSV có một dòng cho mỗi case.
