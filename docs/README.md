# Tài liệu dự án

- [Kiến trúc hệ thống](ARCHITECTURE.md)
- [Bộ dữ liệu đánh giá](../evaluation/README.md)

## Kiểm tra nhanh

Từ thư mục gốc trên Windows:

```powershell
cd backend
venv\Scripts\python.exe -m pytest -q
cd ..
backend\venv\Scripts\python.exe evaluation\validate_dataset.py
```

API integration tests dùng FastAPI dependency overrides và mock RAG stream,
vì vậy không gọi LLM hoặc dịch vụ bên ngoài. Dataset hiện có 36 JSONL cases,
gồm academic, administrative, career và out-of-scope.

Benchmark retrieval reproducible (không gọi LLM):

```powershell
backend\venv\Scripts\python.exe evaluation\benchmark.py --dry-run
```

Benchmark thật cần `GOOGLE_API_KEY` và Chroma index đã ingest; xem
[hướng dẫn benchmark](../evaluation/README.md). Script báo `blocked` và exit
non-zero khi điều kiện này không có, thay vì tạo kết quả giả.

Đánh giá chất lượng câu trả lời độc lập với auth dùng
`evaluation/quality.py`. Công cụ chỉ tính các proxy lexical/context tái lập
được cho Faithfulness, Context Precision và Answer Relevance; không tự nhận
là điểm LLM. Schema, công thức, output mẫu và cách ghi báo cáo Chương 4
được mô tả trong [evaluation README](../evaluation/README.md). Judge adapter
không có sẵn sẽ có trạng thái `unavailable`; chế độ bắt buộc judge sẽ
`blocked`, không bịa điểm.
