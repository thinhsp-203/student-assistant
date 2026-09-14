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
