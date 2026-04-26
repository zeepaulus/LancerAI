# `frontend/` — LancerAI Web (Next.js)

Ứng dụng **Next.js 16** (App Router), **React 19**. Trang mặc định: danh sách
**GET** tới backend (kiểm thử nhanh **API**).

## Chạy

```bash
npm install
npm run dev
```

`NEXT_PUBLIC_API_BASE_URL` — URL **API** (mặc định thường `http://localhost:8000`).

## Cấu trúc

- `src/app/` — `layout`, `page`, `globals.css`
- `public/` — tài tĩnh (nếu có)

Mở rộng: auth, upload **CV**, màn tối ưu, phỏng vấn (**WebSocket** + audio) — bám
bề mặt **API** trong `app/router/v1/`.
