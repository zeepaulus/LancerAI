# TODO — Danh sách công việc LancerAI

Theo dõi tiến độ implement theo từng module. Check off khi hoàn thành, bổ sung mục khi phát sinh. File tham chiếu được ghi ở đầu mỗi mục để dễ dàng bắt đầu.

**Ký hiệu:** `[ ]` Chưa làm — `[x]` Hoàn thành — `[~]` Đang làm / làm một phần

---

## M0 — Authentication

**Files:** `app/service/auth_service.py`, `app/core/security.py`, `app/core/dependencies.py`, `app/router/v1/auth_api.py`

- [ ] Implement `security.hash_password` và `security.verify_password` (bcrypt hoặc argon2)
- [ ] Implement `security.create_access_token` và `decode_access_token` (PyJWT, HS256)
- [ ] Implement `AuthService.signup` — tạo bản ghi `User`, trả về thông tin user
- [ ] Implement `AuthService.login` — xác minh password, phát hành JWT
- [ ] Implement `AuthService.resolve_token` — giải mã JWT, tra cứu `User` từ database
- [ ] Wire các endpoint trong `auth_api.py` vào `AuthService` (xóa stub HTTP 501)
- [ ] Viết integration test: đăng ký → đăng nhập → `GET /auth/me`
- [ ] (Tùy chọn) Thêm bảng `tenants`, RBAC phân quyền, audit log

---

## M1 — CV Extraction

**Files:** `app/core/ocr_processor.py`, `app/service/extraction_service.py`, `app/router/v1/extraction_api.py`

- [ ] Implement `OCRProcessor.extract_text` và `extract_text_grouped` bằng PaddleOCR (tiếng Việt + tiếng Anh)
- [ ] Implement `ExtractionService.extract_from_pdf` — dùng PyMuPDF cho PDF có text; fallback OCR cho PDF scan
- [ ] Implement `ExtractionService.extract_from_image` — pipeline OCR thuần
- [ ] Dùng `LLMConnector` để cấu trúc hóa raw text thành `CVExtractionResponse` schema (json_mode)
- [ ] Lưu dữ liệu đã trích xuất vào bảng `cv_records` (filter theo `user_id` khi đọc)
- [ ] Lưu CV embedding vào `VectorRepository` để phục vụ RAG (M2) và matching (M3)
- [ ] Wire các endpoint trong `extraction_api.py` vào `ExtractionService` (xóa stub HTTP 501)
- [ ] Viết test: upload PDF → kiểm tra các trường đã được populate đúng

---

## M2 — CV Optimization (LangGraph)

**Files:** `app/service/agents/`, `app/service/optimization_service.py`, `app/router/v1/optimization_api.py`, `app/core/llm_connector.py`

- [ ] Implement `LLMConnector.generate` gọi đến Ollama endpoint `/api/generate`
- [ ] Implement `LLMConnector.generate_chat` và các phiên bản streaming
- [ ] Implement `retrieval_agent` — query vector DB lấy industry benchmark; populate `industry_benchmarks` và `keyword_frequency_map`
- [ ] Implement `roast_agent` — xác định điểm yếu trong CV; xuất ra danh sách `RoastIssue`
- [ ] Implement `rewrite_agent` — viết lại các phần yếu theo công thức Google XYZ; xuất ra danh sách `RewrittenSection`
- [ ] Implement `audit_agent` — kiểm tra tính trung thực; xuất `AuditFlag`; merge các phần được duyệt vào `optimized_cv`
- [ ] Implement `OptimizationService.analyze_cv` — chạy LangGraph đã compile, lưu `optimized_data` lên `CVRecord`
- [ ] Implement `OptimizationService.render_template_cv` — dùng LLM chiếu CV vào template có cấu trúc
- [ ] Implement `OptimizationService.render_template_pdf` — WeasyPrint render HTML thành PDF
- [ ] Wire các endpoint trong `optimization_api.py` (xóa stub HTTP 501)
- [ ] Viết test: kiểm tra graph chạy không lỗi trên sample CV data

---

## M3 — Job Matching

**Files:** `app/service/matching_service.py`, `app/repository/vector_repository.py`, `app/router/v1/job_matching_api.py`

- [ ] Implement `VectorRepository.store_embedding` và `search_similar` (ChromaDB hoặc Qdrant)
- [ ] Implement `MatchingService.match_cv_to_jd` — Hybrid Scoring (tần suất 20% + vị trí 30% + semantic 50%)
- [ ] Thêm chức năng crawl JD từ URL (Scrapy hoặc Playwright) kèm rate limiting
- [ ] Cache JD đã parse theo content hash để tránh gọi LLM lặp lại
- [ ] Implement `MatchingService.get_recommendations` — vector search trong corpus `job_listings`
- [ ] Wire các endpoint trong `job_matching_api.py` (xóa stub HTTP 501)
- [ ] Viết test: kiểm tra trọng số scoring, kiểm tra thứ tự gap list

---

## M4 — Voice Interview

**Files:** `app/core/voice_stt_connector.py`, `app/core/voice_tts_connector.py`, `app/service/interview/pipeline.py`, `app/service/interview/agents.py`, `app/service/interview_service.py`, `app/router/v1/interview_api.py`

- [ ] Implement `VoiceSTTConnector.transcribe` — load PhoWhisper qua HuggingFace Transformers pipeline
- [ ] Implement `VoiceSTTConnector.stream_transcribe` — streaming ASR cho WebSocket pipeline
- [ ] Implement `VoiceTTSConnector.synthesize` — hỗ trợ engine edge-tts; trả về PCM @ 24kHz
- [ ] Implement `VoiceTTSConnector.synthesize_stream` — streaming TTS để giảm độ trễ phát âm
- [ ] Implement `InterviewPipeline.start` — xây dựng system prompt từ CV + JD, phát câu chào mở đầu
- [ ] Implement `InterviewPipeline.feed_audio` — phát hiện lượt nói bằng energy gate, chuyển audio đến STT
- [ ] Implement `InterviewPipeline.stop` — kết thúc phiên, chạy STAR evaluation
- [ ] Implement `question_node`, `evaluate_node`, `wrap_up_node` trong `interview/agents.py`
- [ ] Implement `InterviewService.persist_session` và `get_report`
- [ ] Thêm xác thực WebSocket qua query token (`?token=<jwt>`)
- [ ] Wire WebSocket handler trong `interview_api.py` vào `InterviewPipeline`
- [ ] Frontend: implement AudioWorklet để thu âm PCM ở 16kHz; phát lại ở 24kHz
- [ ] Viết test: kiểm tra logic STAR scoring trên sample transcript

---

## M5 — Background Workers

**Files:** `app/workers/crawler_worker.py`, `app/workers/document_worker.py`

- [ ] Cấu hình Celery app instance với Redis broker và result backend
- [ ] Implement `crawl_job_listings` — scraper bằng Scrapy/Playwright cho TopCV và ITviec
- [ ] Implement `generate_document` — WeasyPrint cho PDF, python-docx cho DOCX
- [ ] Thiết lập Celery Beat schedule để crawl hàng ngày tự động
- [ ] Thêm endpoint admin để trigger crawl thủ công (yêu cầu RBAC từ M0)

---

## Lưu trữ nâng cao

**Files:** `app/repository/vector_repository.py`, `app/repository/graph_repository.py`

- [ ] Implement `VectorRepository` với ChromaDB (hoặc Qdrant)
- [ ] Implement `GraphRepository` với Neo4j — `get_related_skills`, `get_skill_importance`
- [ ] (Tùy chọn) Per-tenant database routing trong `RelationalRepository`
- [ ] Đảm bảo Alembic migration bao phủ đủ tất cả ORM model hiện tại

---

## Frontend product

**Files:** `frontend/src/app/`

- [ ] Trang đăng nhập và đăng ký — lưu JWT vào cookie hoặc localStorage
- [ ] Trang upload CV — multipart form, hiển thị kết quả extraction
- [ ] Trang CV optimization — trigger phân tích, hiển thị roast issue và phần viết lại, xuất PDF
- [ ] Trang job matching — nhập JD URL hoặc paste text, hiển thị điểm và gap list
- [ ] Trang phỏng vấn — WebSocket connection, thu âm bằng AudioWorklet, phát lại audio
- [ ] Dashboard / lịch sử — danh sách phiên phỏng vấn, xem STAR score
- [ ] Navigation và routing tổng thể cho toàn bộ ứng dụng

---

## Chất lượng và Developer Experience

- [ ] `tests/conftest.py` — shared fixture (DB session, mock connector)
- [ ] Integration test suite dùng docker compose stack
- [ ] Pre-commit hooks: ruff, mypy
- [ ] GitHub Actions CI — lint và test tự động khi push/PR
- [ ] Ổn định `response_model` trên tất cả OpenAPI endpoint (thay thế kiểu trả về `dict` bằng schema cụ thể)
- [ ] Thêm `pydantic[email]` và chuyển `AuthSignupRequest.email` sang `EmailStr`
