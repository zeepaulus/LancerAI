# Team Implementation Plan — LancerAI

Bảng phân công module và kiến trúc đề xuất cho giai đoạn chuyển từ MVP mock → real implementation.

---

## Phân công module

| Module | Owner / Role | Scope |
|---|---|---|
| **Backend/API/DB** | Backend Lead | FastAPI router, Pydantic schema, PostgreSQL, Alembic migrations, DI container |
| **CV Extraction (M1)** | ML Engineer + Backend | PyMuPDF text extraction, PaddleOCR fallback, LLM structuring, embedding indexing |
| **CV Optimization (M2)** | ML Engineer + Backend | Sequential pipeline (retrieve → analyze → rewrite → audit), LangGraph optional |
| **Job Matching (M3)** | Backend + Data Eng. | Hybrid scoring (frequency + position + semantic), JD crawling, skill gap analysis |
| **Interview Voice (M4)** | ML Engineer + Backend | STT (PhoWhisper), TTS (edge-tts), turn-based pipeline, STAR evaluation |
| **Frontend** | Frontend Dev | Auth flow, CV upload/display, optimization view, matching results, interview UI |

---

## Kiến trúc đề xuất theo module

### M1 — CV Extraction

**Pipeline:** `File upload → PyMuPDF (text layer) → [nếu scan: PaddleOCR fallback] → LLM structuring → persist + embedding`

Đề xuất:
- **Bước 1:** PyMuPDF (`fitz`) extract text trước. Tính text density.
- **Bước 2:** Nếu density thấp (scan PDF/ảnh), fallback sang PaddleOCR hoặc VietOCR.
- **Bước 3:** LLM structuring — prompt yêu cầu JSON schema, evidence quotes, không bịa số liệu.
- **Bước 4:** Embedding qua `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- **Lưu ý:** Mỗi bước phải có error handling riêng. Không dùng hidden chain-of-thought.

### M2 — CV Optimization

**Pipeline:** `retrieve_context → analyze_issues → rewrite_sections → audit_truthfulness`

Đề xuất:
- **Bắt đầu sequential** — không LangGraph-first. LangGraph chỉ khi team maintain/debug được.
- `retrieve_context`: Vector DB → industry benchmarks, keyword frequency map.
- `analyze_issues`: LLM prompt phân loại vấn đề (vague_claim, missing_metric, weak_verb, buzzword).
- `rewrite_sections`: Áp dụng Google XYZ formula. Prompt PHẢI require JSON schema output.
- `audit_truthfulness`: So sánh rewrite với gốc. Không cho phép bịa số liệu.
- **Prompts phải require:** JSON schema, evidence quotes, no invented metrics.

### M3 — Job Matching

**Pipeline:** `parse JD → skill overlap + section weighting → embedding similarity → aggregate score`

Đề xuất:
- **Skill overlap + section weighting trước**, embedding similarity sau.
- Crawl JD: rate limit, cache (hash nội dung).
- Hybrid scoring: `0.20 × frequency + 0.30 × position + 0.50 × semantic`.
- Gap analysis: phân loại critical / important / nice_to_have.

### M4 — Interview Voice

**Pipeline:** `PCM mic → turn detection → STT → LLM → TTS → PCM speaker`

Đề xuất:
- **Turn-based voice trước**, realtime/VAD sau.
- STT: `vinai/PhoWhisper-base` — CPU/GPU.
- TTS: `edge-tts` voices `vi-VN-HoaiMyNeural` hoặc `vi-VN-NamMinhNeural`.
- Evaluation: STAR framework (Situation, Task, Action, Result).
- **Không request hidden chain-of-thought.**

---

## Công cụ đề xuất

| Category | Tool | Notes |
|---|---|---|
| LLM | Qwen2.5 3B/7B hoặc Llama 3.1 8B | Local qua Ollama; Groq/OpenAI-compatible fallback |
| OCR | PyMuPDF → PaddleOCR/VietOCR fallback | PyMuPDF cho PDF có text layer |
| Embedding | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | 384 dims, multilingual |
| STT | `vinai/PhoWhisper-base` | HuggingFace Transformers, Vietnamese ASR |
| TTS | `edge-tts` vi-VN voices | Hoặc Piper ONNX local |
| Vector DB | ChromaDB (dev) / Qdrant (prod) | Configured qua `VECTOR_DB_BACKEND` |

---

## Quy trình chuyển mock → real

1. **Chọn module** theo priority (M1 → M2 → M3 → M4).
2. **Implement service method** — replace `NotImplementedError` trong connector/service.
3. **Giữ mock data trong test** — test vẫn dùng deterministic mock.
4. **Thêm integration test** với real connector (mark `@pytest.mark.slow` nếu cần).
5. **Router không đổi** — chỉ thay service internals.
6. **PR review** — chạy đủ `pytest`, `ruff`, `mypy` trước merge.

---

## Quality gates bắt buộc

```bash
uv run pytest -q               # All tests pass
uv run ruff check app tests     # No lint errors
uv run mypy app tests            # No type errors
```

Frontend (nếu có script):
```bash
cd frontend && npm run build    # Build clean
```
