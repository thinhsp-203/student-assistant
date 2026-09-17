# Vận hành và thay đổi dữ liệu

## 1. Model RAG không hard-code

Model được đọc từ `backend/.env`:

```env
GEMINI_API_KEY=...
# GOOGLE_API_KEY=... is also supported for backward compatibility.
LLM_MODEL=gemini-3.6-flash
EMBEDDING_MODEL=models/gemini-embedding-001
```

Tên model phải thuộc danh sách model mà API key hiện tại được cấp quyền. Nếu
nhận `401 UNAUTHENTICATED`, cần cấp lại API key/quyền API; đổi tên model không
thể sửa một credential không hợp lệ.

Kiểm tra cấu hình và trạng thái index:

```powershell
cd D:\SONGNAM\student-assistant
backend\venv\Scripts\python.exe -c "from app.core.config import settings; print(settings.LLM_MODEL, settings.EMBEDDING_MODEL)"
```

Sau khi cấu hình key hợp lệ, nạp lại tài liệu:

```powershell
cd backend
venv\Scripts\python.exe scripts\ingest_documents.py
cd ..
backend\venv\Scripts\python.exe evaluation\benchmark.py --k 5 --output evaluation\benchmark.json
```

Benchmark trả `blocked` và mã lỗi khác 0 nếu key/index không hoạt động; không
được dùng kết quả blocked làm số liệu trong luận văn.

Nếu gặp `429 RESOURCE_EXHAUSTED` khi ingestion, đó là quota embedding của
Google đã hết, không phải lỗi API key. Cấu hình mặc định dùng chunk lớn hơn để
giảm số request; vẫn cần chờ thời gian retry hoặc bật billing/tăng quota khi
đồng bộ nhiều tài liệu.

## 2. Thay dữ liệu sinh viên

Không cần sửa code. Tạo file JSON theo cấu trúc
`backend/data/students/sample_students.json`, sau đó chạy:

```powershell
cd backend
venv\Scripts\python.exe scripts\seed_students.py
```

Chế độ mặc định là **upsert**: cập nhật sinh viên cùng `student_id`, thay bảng
điểm của sinh viên đó, giữ các sinh viên khác. Dùng `--replace` chỉ khi muốn
xóa toàn bộ sinh viên/transcript hiện có rồi nạp lại dữ liệu:

```powershell
venv\Scripts\python.exe app\database\init_db.py --replace
```

Có thể truyền file riêng:

```powershell
venv\Scripts\python.exe app\database\init_db.py `
  --students D:\data\students.json `
  --curriculum D:\data\courses.json
```

## 3. Thay chương trình đào tạo

File curriculum cần có `course_id`, `name`, `credits`, `category`,
`suggested_semester`, `prerequisites` và `description`. Chương trình được
thay thế nguyên khối khi import để không còn prerequisite cũ.

## 4. Dữ liệu mô phỏng và dữ liệu thật

Các file hiện tại là dữ liệu mô phỏng để chứng minh tính khả thi. Trong đề
cương cần ghi rõ giới hạn này. Khi có tài liệu/quy chế thật được phép sử dụng,
đặt file Markdown vào `backend/data/documents/`, cập nhật metadata nếu cần và
chạy ingestion lại. Không đưa dữ liệu cá nhân thật hoặc văn bản nội bộ chưa
được phép lên repository công khai.

## 5. Đồng bộ dữ liệu công khai HCM-UTE

Hệ thống có danh sách nguồn được kiểm soát tại
`backend/data/sources/hcmute_public_sources.json`. Chỉ các trang công khai
trên website chính thức được đồng bộ; không lấy dữ liệu cá nhân, dữ liệu đăng
nhập hoặc nội dung sau tường quyền truy cập.

```powershell
cd D:\SONGNAM\student-assistant\backend
venv\Scripts\python.exe scripts\sync_hcmute_open_data.py
venv\Scripts\python.exe scripts\ingest_documents.py
```

Mỗi tài liệu lưu URL, danh mục và thời điểm đồng bộ. Nếu website thay đổi cấu
trúc hoặc một URL không còn tồn tại, script báo lỗi và trả mã thoát khác 0;
không xóa dữ liệu cũ một cách âm thầm. Các trang tin chỉ là dữ liệu tham khảo,
không thay thế quy chế/chương trình đào tạo được nhà trường ban hành.
