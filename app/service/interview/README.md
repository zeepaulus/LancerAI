# `service/interview/` — Phỏng vấn **voice**

`InterviewPipeline`: thu **PCM** → **STT** (PhoWhisper) → **LLM** streaming → **TTS**
streaming; kết thúc có thể chấm **STAR** (prompt tiếng Việt tùy thiết lập).

- `state.py` — trạng thái buổi, điểm **STAR**
- `pipeline.py` — vòng xử lý audio / lượt nói
- `agents.py` — bước câu hỏi / đánh giá tách nhỏ nếu cần

Router **WebSocket** tại `app/router/v1/interview_api.py` tạo pipeline và gắn
callback gửi byte/JSON. Tham số **STT**/**TTS**/**LLM** trong `settings` / `.env`.
