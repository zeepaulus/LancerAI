# TODO — hạng mục kỹ thuật (LancerAI)

Bảng công việc theo lớp chức năng. Cập nhật checkbox khi xong, bổ sung mục khi
phát sinh. Đường dẫn tệp ở dưới dùng làm neo triển khai.

## Xác thực & tách dữ liệu theo tổ chức

`app/service/auth_service.py`, `app/core/security.py`, `app/core/dependencies.py`
(`get_current_user`), `app/router/v1/auth_api.py`

- [ ] Băm / kiểm tra mật khẩu (`bcrypt` hoặc `argon2`)
- [ ] Ký & giải mã **JWT** (PyJWT, **HS256**)
- [ ] `AuthService`: signup, login, `resolve_token` → `User`
- [ ] Nối router `auth` với service
- [ ] Migration **Alembic** bổ sung nếu schema đổi
- [ ] Test: đăng ký → login → `GET /me`  
- (Tuỳ) bảng tổ chức (`tenants`), phân quyền theo vai trò (**RBAC**), audit log

## Mô-đun 1 — Trích xuất **CV**

`app/core/ocr_processor.py`, `app/service/extraction_service.py`, `app/router/v1/extraction_api.py`

- [ ] **OCR** (PaddleOCR vi+en)
- [ ] `extract_from_pdf` — PyMuPDF, fallback **OCR**; cấu trúc hóa qua **LLM**; lưu `cv_records`
- [ ] `extract_from_image` — **OCR** thuần
- [ ] Lọc bản ghi theo người dùng / tổ chức trên `get_cv`
- [ ] Lưu embedding (phục vụ **RAG** / matching)

## Mô-đun 2 — Tối ưu **CV** (LangGraph)

`app/service/agents/`, `app/service/optimization_service.py`, `app/router/v1/optimization_api.py`

- [ ] `LLMConnector` gọi **Ollama** (generate / chat)
- [ ] Các **agent**: retrieval, roast, rewrite, audit
- [ ] `OptimizationService`: `analyze_cv`, `render_template_cv`, `render_template_pdf` (WeasyPrint)

## Mô-đun 3 — Matching

`app/service/matching_service.py`, `app/router/v1/job_matching_api.py`, `app/repository/vector_repository.py`

- [ ] `match_cv_to_jd` (heuristic + **LLM** + vector)
- [ ] **JD** từ **URL** (Scrapy / Playwright, có rate limit)
- [ ] Gợi ý từ corpus / vector; cache **JD** theo hash

## Mô-đun 4 — Phỏng vấn **voice**

`app/core/voice_stt_connector.py`, `app/core/voice_tts_connector.py`, `app/service/interview/`, `app/router/v1/interview_api.py`

- [ ] **STT** (PhoWhisper), ngưỡng năng lượng chống nhận dạng trên nền im lặng
- [ ] **STT** streaming; **TTS** synthesize + stream
- [ ] `InterviewPipeline` đủ vòng: start, audio, lượt nói, **LLM** stream, **TTS** stream, dừng, chấm **STAR**
- [ ] `InterviewService` lưu / báo cáo session
- [ ] Xác thực **WebSocket** (query `token` hoặc tương đương)
- [ ] **Frontend:** AudioWorklet, 16kHz in / 24kHz out

## Worker

`app/workers/`, thiết lập **Celery**

- [ ] Crawl tin tuyển dụng; render **PDF**/**DOCX** từ dữ liệu CV
- [ ] Lịch **beat**; endpoint admin (khi có phân quyền)

## Lưu trữ nâng cao

- [ ] `VectorRepository` (Chroma / Qdrant)
- [ ] `GraphRepository` (Neo4j)
- [ ] (Tuỳ) chọn kết nối **DB** theo tổ chức
- [ ] Bộ migration gốc đủ bảng **ORM** hiện tại

## Frontend sản phẩm

`frontend/src/app/`

- [ ] Đăng ký / đăng nhập, lưu **JWT**
- [ ] Upload **CV** (multipart)
- [ ] Màn tối ưu & export
- [ ] Màn phỏng vấn (**WebSocket** + audio)
- [ ] Dashboard / lịch sử
- [ ] Trang chính / điều hướng tổng thể

## Chất lượng & **DX**

- [ ] `conftest.py` + **fixture** dùng chung
- [ ] Bài test tích hợp (stack **docker compose**)
- [ ] **Pre-commit** (ruff, mypy, …)
- [ ] **CI** (ví dụ GitHub Actions)
- [ ] `response_model` ổn định trên **OpenAPI**
