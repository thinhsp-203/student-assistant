# Kế hoạch và tiêu chí nghiệm thu khóa luận

## Mục tiêu

Hệ thống hỗ trợ sinh viên tra cứu học vụ bằng RAG có nguồn tham chiếu và đưa ra đề xuất môn học dựa trên dữ liệu cá nhân cùng luật tiên quyết xác định. LLM chỉ diễn giải dữ liệu đã được truy xuất và kết quả của bộ luật; không dùng LLM để tự quyết định điều kiện đăng ký.

## Phạm vi nghiệm thu

1. Đăng nhập bằng tài khoản sinh viên mẫu và xem hồ sơ/bảng điểm.
2. Hỏi đáp về quy chế, chương trình khung và thủ tục bằng tiếng Việt.
3. Hiển thị nguồn tài liệu cho câu trả lời.
4. Tính môn đã hoàn thành, môn còn thiếu và môn đủ điều kiện học.
5. Giải thích lý do cho từng đề xuất và chỉ ra môn tiên quyết còn thiếu.
6. Từ chối rõ ràng khi tài liệu không đủ bằng chứng.

FAQ hành chính và định hướng nghề nghiệp là module mở rộng, chỉ được bật sau khi năm mục trên hoạt động ổn định.

## Kiến trúc và nguyên tắc

```text
React/Vite -> FastAPI -> (SQLite: hồ sơ + curriculum)
                         -> Academic advising rules
                         -> ChromaDB retrieval -> Gemini API
```

- Dữ liệu định lượng (tín chỉ, điểm, tiên quyết) được tính bằng Python.
- RAG lưu metadata tài liệu: tên tài liệu, mục, lĩnh vực và phiên bản.
- Prompt phải yêu cầu chỉ trả lời từ context và nêu nguồn.
- `.env`, khóa API, virtual environment, node_modules và database runtime không nằm trong Git.

## Kế hoạch 12 tuần

| Tuần | Công việc | Đầu ra kiểm chứng |
|---|---|---|
| 1 | Chốt phạm vi, nguồn tài liệu, yêu cầu | Đề cương và backlog được GVHD duyệt |
| 2 | Khảo sát, SRS, Use Case | Chương 1 và yêu cầu chức năng |
| 3 | ERD, Sequence, Component, Deployment | Hồ sơ thiết kế |
| 4 | Chunking, metadata, ingestion | Index Chroma tái lập được |
| 5 | Benchmark retrieval và prompt | Bộ câu hỏi + Recall@k/MRR |
| 6 | Course/prerequisite/transcript | Schema và dữ liệu mẫu |
| 7 | Academic advising engine | API recommendation + unit tests |
| 8 | Tích hợp RAG và student context | Demo backend |
| 9 | Chat/profile/recommendation UI | Demo end-to-end |
| 10 | FAQ/career tối thiểu và UX | Feature freeze |
| 11 | Integration, E2E, benchmark, user study | Test report và bảng số liệu |
| 12 | Viết, đóng gói, bảo vệ thử | Word/PDF/PPT/SETUP/release |

## Bộ bằng chứng cần nộp

- SRS, UML, ERD, API contract và hướng dẫn triển khai.
- Bộ dữ liệu mẫu, câu hỏi đánh giá và đáp án có nguồn.
- Kết quả so sánh: LLM thuần, RAG, RAG + hồ sơ, RAG + rule engine.
- Unit/integration/smoke test và log kết quả.
- Kịch bản demo 7–10 phút, slide và danh sách câu hỏi phản biện.

## Tiêu chí đạt trước bảo vệ

- Cài đặt lại được từ README trên máy sạch.
- Ít nhất ba sinh viên mẫu cho ra đề xuất khác nhau theo bảng điểm/tiến độ.
- Không đề xuất môn khi thiếu tiên quyết.
- Câu trả lời có nguồn hoặc nêu rõ không đủ thông tin.
- Không có secret trong Git; `git status` sạch sau khi build/test.
- Có số liệu về độ chính xác luật, retrieval, nguồn tham chiếu, latency và lỗi.
