# `service/agents/` — Tối ưu CV (LangGraph)

Pipeline: retrieval → roast → (hỏi bổ sung nếu cần) → rewrite → audit.

| Tệp | Vai trò |
|-----|---------|
| `state.py` | `CVOptimizationState` — dùng chung các node |
| `graph.py` | Dựng `StateGraph` |
| `retrieval_agent.py` | Benchmark / từ khóa (vector + **LLM** tùy thiết kế) |
| `roast_agent.py` | Góp ý, mức độ, có thể hỏi thêm |
| `rewrite_agent.py` | Viết lại theo công thức, không bịa số |
| `audit_agent.py` | So sánh bản sửa với dữ liệu gốc |

**LLM** inject qua `LLMConnector`. Sửa `state` phải đồng bộ mọi node.
