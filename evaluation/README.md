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

## Answer-quality proxies (Chapter 4)

`quality.py` mở rộng đánh giá độc lập với authentication và không gọi LLM.
Input là một JSON array; mỗi case có schema:

```json
{
  "id": "fake-001",
  "question": "Điều kiện đăng ký môn?",
  "answer": "Sinh viên phải hoàn thành môn tiên quyết.",
  "contexts": [
    {"text": "Môn tiên quyết phải được hoàn thành trước khi đăng ký.", "source": "quy_che.md"}
  ],
  "expected_sources": ["quy_che.md"]
}
```

`contexts` phải là danh sách string hoặc object `{text, source}` (cũng chấp
nhận `page_content`). `expected_sources` là danh sách tên file; basename được
chuẩn hóa không phân biệt hoa thường. `answer` và `question` là string.

Ba proxy deterministic, không phải LLM judge:

* **Faithfulness proxy** = số content-token phân biệt của answer xuất hiện
  trong toàn bộ context / tổng số content-token của answer. Stopword và dấu
  câu bị loại; score `null` nếu answer không có content-token.
* **Context precision proxy** = số context có source thuộc `expected_sources`
  / số context đã truy xuất (precision@k). Score `null` nếu thiếu expected
  sources hoặc không có context.
* **Answer relevance proxy** = F1 của tập content-token question và answer.
  Đây chỉ là tín hiệu lexical, không khẳng định mức độ liên quan ngữ nghĩa.

Chạy:

```powershell
backend\venv\Scripts\python.exe evaluation\quality.py evaluation\sample_results.json
```

`evaluation/sample_results.json` là fixture nhỏ, có thể dùng để kiểm tra
pipeline trước khi cung cấp kết quả thật.

Output mẫu (rút gọn):

```json
{
  "status": "ok",
  "summary": {
    "cases": 1,
    "faithfulness_proxy": 1.0,
    "context_precision_proxy": 1.0,
    "answer_relevance_proxy": 0.375
  },
  "judge": {"status": "unavailable", "reason": "no judge adapter supplied"}
}
```

Không được gọi các proxy này là human/LLM scores trong báo cáo Chương 4.
Nếu cần judge, tích hợp một callable adapter qua `evaluate(...,
judge_adapter=...)`; adapter phải tự trả về kết quả có provenance/model. Khi
`require_judge=True` mà adapter không có, evaluator trả `status: "blocked"`,
exit code 2 và tuyệt đối không tạo điểm giả. Vì vậy báo cáo phải ghi rõ
proxy, công thức, input version, `k`, và trạng thái judge.
