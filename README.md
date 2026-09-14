# 🎓 Hệ thống Trợ lý Sinh viên Thông minh
## AI-powered Intelligent Student Assistant System

Ứng dụng Web tích hợp AI đóng vai trò trợ lý ảo, hỗ trợ sinh viên ở 3 mảng:
- 📚 **Tư vấn học tập** (trọng tâm): Tư vấn đăng ký môn học, kiểm tra tiên quyết, gợi ý lộ trình
- 📋 **Hỗ trợ hành chính**: FAQ thủ tục, hướng dẫn quy trình
- 💼 **Định hướng nghề nghiệp**: Gợi ý nghề nghiệp, kỹ năng cần thiết

### Công nghệ sử dụng

| Layer | Công nghệ |
|-------|-----------|
| AI/LLM | OpenAI GPT-4o-mini + RAG (Retrieval-Augmented Generation) |
| Vector DB | ChromaDB |
| RAG Framework | LangChain (LCEL) |
| Backend | Python FastAPI |
| Frontend | React + Vite + Tailwind CSS |
| Database | SQLite |

### Kiến trúc

```
Tài liệu học vụ → Chunking → Embedding → ChromaDB
                                              ↓
Sinh viên đặt câu hỏi → Retrieval → LLM + Student Context → Câu trả lời
```

## 🚀 Hướng dẫn cài đặt

### Yêu cầu
- Python 3.10+
- Node.js 18+
- Google Gemini API Key

### Bước 1: Cài đặt Backend

```bash
cd backend

# Tạo virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình environment
copy .env.example .env
# Sửa file .env: thêm GOOGLE_API_KEY của bạn

# Khởi tạo database sinh viên
python scripts/seed_students.py

# Nạp tài liệu vào vector database
python scripts/ingest_documents.py

# Chạy backend server
uvicorn app.main:app --reload --port 8000
```

### Bước 2: Cài đặt Frontend

```bash
cd frontend

# Cài đặt dependencies
npm install

# Chạy development server
npm run dev
```

### Bước 3: Truy cập ứng dụng

Mở trình duyệt tại: **http://localhost:5173**

MSSV mẫu để đăng nhập: `20210001`, `20210045`, `20200112`, `20220078`, `20210099`

## 📁 Cấu trúc dự án

```
student-assistant/
├── backend/                  # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/endpoints/ # REST API endpoints
│   │   ├── core/             # Config, security
│   │   ├── database/         # SQLite management
│   │   ├── models/           # Data models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/         # Business logic (RAG, ChromaDB, etc.)
│   ├── data/
│   │   ├── documents/        # Tài liệu nguồn (quy chế, chương trình...)
│   │   └── students/         # Dữ liệu sinh viên mẫu
│   └── scripts/              # Seed & ingestion scripts
├── frontend/                 # React Frontend
│   └── src/
│       ├── components/       # UI Components
│       ├── hooks/            # Custom React hooks
│       ├── pages/            # Page components
│       ├── services/         # API services
│       └── types/            # TypeScript types
└── README.md
```

## 📖 API Documentation

Sau khi chạy backend, truy cập Swagger UI tại: **http://localhost:8000/docs**

### Endpoints chính:
- `POST /api/v1/chat/completions` — Chat streaming (SSE)
- `GET /api/v1/students/{student_id}` — Thông tin sinh viên
- `GET /api/v1/students/{student_id}/transcript` — Bảng điểm
- `POST /api/v1/students/login` — Đăng nhập (demo mode)
- `POST /api/v1/documents/ingest` — Nạp tài liệu

## 👥 Tác giả

Đề tài tốt nghiệp — Xây dựng hệ thống trợ lý sinh viên thông minh tích hợp AI
