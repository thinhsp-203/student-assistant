# Student Assistant Backend

Backend FastAPI cho hệ thống Trợ lý sinh viên.

## Yêu cầu hệ thống
- Python 3.10+
- OpenAI API Key

## Cài đặt

1. Tạo môi trường ảo và kích hoạt:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

3. Cấu hình biến môi trường:
Copy `.env.example` thành `.env` và điền OpenAI API key của bạn:
```bash
cp .env.example .env
```

## Khởi tạo dữ liệu (Seed & Ingestion)

1. Tạo cơ sở dữ liệu sinh viên mẫu:
```bash
python scripts/seed_students.py
```
Lệnh này đồng thời tạo các bảng `courses` và `course_prerequisites` và nạp
danh mục môn học có cấu trúc từ `data/curriculum/courses.json`.

## Tư vấn học tập theo luật

API không phụ thuộc LLM để kiểm tra tiên quyết:
```text
GET /api/v1/advising/{student_id}/recommendations?target_semester=6
```
Môn đã hoàn thành bị loại khỏi kết quả; môn chỉ được đề xuất khi toàn bộ
tiên quyết có trong bảng điểm và học kỳ gợi ý không vượt quá học kỳ mục tiêu.
Có thể chạy kiểm tra nhanh bằng:
```bash
python scripts/validate_advising.py
```

2. Đọc và lưu trữ tài liệu (RAG):
Đảm bảo bạn có file `.md` trong thư mục `data/documents/` trước khi chạy:
```bash
python scripts/ingest_documents.py
```

## Khởi chạy Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Kiểm thử API

Chạy toàn bộ test bằng Python trong virtual environment:

```bash
venv\Scripts\python.exe -m pytest -q
```

`tests/test_api_integration.py` kiểm tra login, transcript, progress,
recommendations và SSE chat. Các dependency được override bằng service giả nên
test không cần gọi Google Gemini/LLM hoặc vector database bên ngoài.

## Tài liệu API (Swagger UI)
Sau khi server chạy, truy cập tài liệu API tại: [http://localhost:8000/docs](http://localhost:8000/docs)
