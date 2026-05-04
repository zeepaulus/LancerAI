# `app/service/agents/` — LangGraph CV Optimization Pipeline (Module 2)

Sub-package triển khai **multi-agent CV intelligence pipeline** sử dụng **LangGraph**. Đây là core của Module 2 — phân tích CV bằng nhiều AI agents chạy tuần tự trong một compiled state graph.

## Pipeline Architecture

```
START → [retrieval] → [roast] → [rewrite] → [audit] → END
```

Mỗi node là một async function nhận `CVOptimizationState` + `LLMConnector`, trả về `dict` chứa state updates. LangGraph merge updates vào shared state theo reducer rules.

## Files

### `state.py` — Shared State Schema

`CVOptimizationState` (Pydantic `BaseModel`) là object duy nhất chảy qua toàn bộ pipeline.

**State sections:**

| Section | Fields | Owner Agent |
|---|---|---|
| Input | `cv_id`, `raw_cv_data`, `target_job_title`, `target_industry` | Caller |
| Retrieval outputs | `industry_benchmarks`, `keyword_frequency_map` | `retrieval_agent` |
| Roast outputs | `roast_issues: list[RoastIssue]`, `roast_summary` | `roast_agent` |
| Inquiry outputs | `inquiry_questions`, `inquiry_needed`, `inquiry_complete` | (future) |
| Rewrite outputs | `rewritten_sections: list[RewrittenSection]` | `rewrite_agent` |
| Audit outputs | `audit_flags: list[AuditFlag]`, `audit_passed` | `audit_agent` |
| Final output | `optimized_cv`, `overall_improvement_score` | `audit_agent` |
| Control | `current_step`, `error_message`, `pipeline_complete` | All agents |

**Append-only fields** (LangGraph reducer `operator.add`):
- `roast_issues`, `inquiry_questions`, `rewritten_sections`, `audit_flags`
- LangGraph tự động merge lists khi nhiều nodes cùng append — tránh race conditions.

**Sub-schemas:**

| Schema | Description |
|---|---|
| `RoastIssue` | Một vấn đề được phát hiện: `field`, `severity` (Literal), `issue_type` (Literal), `original_text`, `explanation`, `needs_clarification` |
| `InquiryQuestion` | Câu hỏi để hỏi user khi cần thêm context |
| `RewrittenSection` | Một section được viết lại: `field`, `original`, `rewritten`, `formula_used` (xyz/star/car/direct), `improvement_score` |
| `AuditFlag` | Truthfulness issue: `field`, `rewritten_text`, `original_text`, `issue`, `verdict` (Literal) |

### `graph.py` — LangGraph Assembly

```python
def build_cv_optimization_graph(llm: LLMConnector) -> CompiledStateGraph:
```

- Khởi tạo `StateGraph(CVOptimizationState)`.
- Đăng ký 4 nodes: `retrieval`, `roast`, `rewrite`, `audit`.
- Kết nối linear edges: `retrieval → roast → rewrite → audit → END`.
- Compile và trả về `CompiledStateGraph`.

**Design**: Graph được build **lazily** (on first request, không phải tại import time) để tránh eager LLM connector initialization.

`_make_node(agent_fn, llm)` là helper closure inject `LLMConnector` vào từng agent function mà không cần global state.

### `retrieval_agent.py` — Node 1: Context Retrieval
First node trong pipeline. Pulls grounding data cho downstream agents.

**Responsibilities:**
- Query vector DB cho similar JDs / role profiles.
- Optionally call LLM để synthesize industry benchmarks khi vector data sparse.
- Populate `industry_benchmarks` và `keyword_frequency_map` trên state.

### `roast_agent.py` — Node 2: CV Analysis
Phân tích CV với góc nhìn của recruiter/ATS system.

**Issue types detected** (`issue_type` Literal):
- `vague_claim` — "Experienced in Python" không có metric
- `buzzword` — "synergy", "leverage", "passionate"
- `missing_metric` — impact không được quantified
- `weak_verb` — "helped", "assisted" thay vì action verbs
- `generic_statement` — copy-paste từ template

**Output**: list of `RoastIssue` với `severity` 4 cấp và `needs_clarification` flag.

### `rewrite_agent.py` — Node 3: CV Rewriting
Viết lại các sections yếu sử dụng **Google XYZ formula**:
> *"Accomplished X, as measured by Y, by doing Z"*

**Constraint**: không được invent metrics — phải grounded trong `raw_cv_data`. Nếu metric bị thiếu và `inquiry_complete=False`, defer sang Inquiry agent (future).

**Output**: list of `RewrittenSection` với `formula_used` và `improvement_score`.

### `audit_agent.py` — Node 4: Truthfulness Gate
Final compliance check — verify rewrites không exaggerate hay fabricate.

**Responsibilities:**
- Compare từng `RewrittenSection` với `raw_cv_data`.
- Verdict mỗi section: `approved` / `needs_revision` / `rejected`.
- Merge approved rewrites vào `optimized_cv`.
- Compute `overall_improvement_score` từ tỷ lệ approved sections.

## Technology

| Component | Library |
|---|---|
| Agent orchestration | **LangGraph** (`StateGraph`, `CompiledStateGraph`) |
| State schema | **Pydantic v2** (`BaseModel`, `Annotated`, `operator.add`) |
| LLM inference | `LLMConnector` (Ollama `qwen2.5:3b` / Groq) |
| Async | Python `asyncio` (all agent functions are `async`) |
