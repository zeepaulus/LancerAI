# `app/service/optimization/` — CV Intelligence Pipeline (Module 2)

Sub-package tự chứa (**bounded context**) toàn bộ logic tối ưu CV: service orchestrator, LangGraph graph, agent nodes, và shared state schema.

## Structure

```
optimization/
├── service.py           OptimizationService — public entry point duy nhất
├── graph.py             LangGraph builder: build_cv_optimization_graph()
├── state.py             CVOptimizationState (TypedDict) + sub-schemas (Pydantic)
├── retrieval_agent.py   Agent 1: thu thập ngữ cảnh ngành từ vector DB
├── roast_agent.py       Agent 2: phát hiện điểm yếu trong CV
├── rewrite_agent.py     Agent 3: viết lại các phần yếu
└── audit_agent.py       Agent 4: kiểm tra tính trung thực bản viết lại
```

## Pipeline

```
START → retrieval → roast → rewrite → audit → END
```

### `service.py` — OptimizationService

Entry point Module 2 cho router; orchestrator LangGraph `analyze_cv` (stub). Không chứa render template.

| Method | Mô tả |
|--------|--------|
| `analyze_cv` | Chạy pipeline retrieval → roast → rewrite → audit; persist `optimized_data` |

### `template_renderer.py` — CVTemplateRenderer

Render JSON/PDF từ dữ liệu CV; dùng bởi `optimization_api` qua `get_template_renderer`.

| Method | Mô tả |
|--------|--------|
| `render_cv` | Chiếu CV vào template có cấu trúc (JSON) |
| `render_pdf` | HTML → PDF bytes (WeasyPrint khi implement) |

Dependencies: `LLMConnector` (theo constructor class).

---

### `graph.py` — LangGraph Assembly

`build_cv_optimization_graph(llm: LLMConnector) -> CompiledStateGraph`

Wire 4 node agent, compile graph. Gọi từ `OptimizationService.analyze_cv` sau khi service được implement (tránh compile tại import time nếu graph nặng).

---

### `state.py` — Shared State Schema

`CVOptimizationState` (Python `TypedDict`) là state duy nhất flowing qua toàn bộ graph. LangGraph merge state updates bằng reducer functions.

**State sections:**

| Field | Type | Description |
|---|---|---|
| `cv_id`, `raw_cv_data` | `str`, `dict` | CV input |
| `target_job_title`, `target_industry` | `str` | Target context |
| `industry_benchmarks`, `keyword_frequency_map` | `dict` | Retrieval output |
| `roast_issues` | `list[RoastIssue]` (append-only) | Danh sách vấn đề từ Roast |
| `rewritten_sections` | `list[RewrittenSection]` (append-only) | Bản viết lại từ Rewrite |
| `audit_flags` | `list[AuditFlag]` (append-only) | Kết quả kiểm duyệt |
| `optimized_cv` | `dict` | CV tối ưu cuối cùng |
| `overall_improvement_score` | `float` | Điểm cải thiện tổng thể |
| `current_step`, `error_message`, `pipeline_complete` | `str`, `str`, `bool` | Control flow |

**Sub-schemas:**

| Schema | Description |
|---|---|
| `RoastIssue` | Một vấn đề được phát hiện: `field`, `severity`, `issue_type`, `original_text`, `explanation` |
| `InquiryQuestion` | Câu hỏi cần hỏi user để làm rõ thông tin thiếu |
| `RewrittenSection` | Một phần CV được viết lại: `field`, `original`, `rewritten`, `formula_used`, `improvement_score` |
| `AuditFlag` | Kết quả kiểm duyệt: `field`, `rewritten_text`, `original_text`, `issue`, `verdict` |

---

### Agent Nodes

Mỗi agent là một `async def fn(state: CVOptimizationState, llm: LLMConnector) -> dict` trả về dict state updates.

| Agent | Responsibility |
|---|---|
| `retrieval_agent` | Query vector DB cho industry benchmarks; populate `industry_benchmarks` + `keyword_frequency_map` |
| `roast_agent` | Phân tích CV với con mắt recruiter; populate `roast_issues` + `roast_summary` |
| `rewrite_agent` | Áp dụng công thức Google XYZ để viết lại; populate `rewritten_sections` |
| `audit_agent` | So sánh bản viết lại với CV gốc; build `optimized_cv`, tính `overall_improvement_score` |

## Technology

| Component | Library |
|---|---|
| Multi-agent orchestration | **LangGraph** (`StateGraph`, `CompiledStateGraph`) |
| State schema | **TypedDict** & **Pydantic v2** (`BaseModel`, `Annotated`, `operator.add`) |
| LLM inference | `LLMConnector` (Ollama / Groq) |
| Vector search | `BaseVectorRepository` (ChromaDB / Qdrant) |
| PDF rendering | **WeasyPrint** (trong `render_template_pdf`) |
