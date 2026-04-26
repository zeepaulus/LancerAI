# `service/` — Nghiệp vụ

Điều phối luồng LancerAI: **auth**, trích xuất **CV**, tối ưu **LangGraph**, matching
**JD**, phỏng vấn (**REST** + pipeline **interview/**).

Mỗi service nhận dependency qua **FastAPI** `Depends`; gọi **repository** và
**connector** trong `core/`, không mở **HTTP** **LLM** thủ công ngoài `LLMConnector`.

**Phụ:** `agents/` (graph tối ưu CV), `interview/` (realtime **STT**/**TTS**/**LLM**).
