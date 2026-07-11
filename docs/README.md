# LancerAI Documentation Hub

Thư mục `docs/` là trung tâm tài liệu cấp project cho LancerAI: kiến trúc, luồng nghiệp vụ, báo cáo hiện trạng, kế hoạch team và checklist vận hành. README chính ở root dùng để onboarding nhanh; các file trong `docs/` đi sâu hơn theo từng mục đích đọc.

**Cập nhật:** 2026-07-11

## 🧭 Reading Paths

| Bạn muốn... | Đọc theo thứ tự |
|---|---|
| Chạy project lần đầu | [../README.md](../README.md) -> [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) -> [../infra/README.md](../infra/README.md) |
| Hiểu kiến trúc | [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) -> [../app/README.md](../app/README.md) -> [../app/service/README.md](../app/service/README.md) |
| Review trạng thái project | [PROJECT_REPORT.md](PROJECT_REPORT.md) -> [FLOW_STUDY_CASES.md](FLOW_STUDY_CASES.md) -> [../TODO.md](../TODO.md) |
| Làm backend/API | [../app/router/v1/README.md](../app/router/v1/README.md) -> [../app/service/README.md](../app/service/README.md) -> [../app/schema/README.md](../app/schema/README.md) |
| Làm AI/CV/interview | [../app/service/optimization/README.md](../app/service/optimization/README.md) -> [../app/service/interview/README.md](../app/service/interview/README.md) |
| Chuẩn bị demo/deploy | [PROJECT_REPORT.md](PROJECT_REPORT.md) -> [TEAM_PLAN.md](TEAM_PLAN.md) -> [../infra/README.md](../infra/README.md) |
| Cải thiện UI/UX | [../DESIGN.md](../DESIGN.md) -> [FLOW_STUDY_CASES.md](FLOW_STUDY_CASES.md) |

## 📌 Core Documents

| Document | Purpose |
|---|---|
| [../README.md](../README.md) | Project overview, features, tech stack, setup, API summary and operations notes |
| [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) | Runtime components, backend layering, frontend organization and main flows |
| [FLOW_STUDY_CASES.md](FLOW_STUDY_CASES.md) | Product flow study cases, failure modes and backlog priorities |
| [PROJECT_REPORT.md](PROJECT_REPORT.md) | Current implementation snapshot, risks, quality status and roadmap |
| [TEAM_PLAN.md](TEAM_PLAN.md) | Team allocation, milestones and quality gates |
| [../DESIGN.md](../DESIGN.md) | Product personality, UX principles, frontend surfaces and known UX gaps |

## 🧩 Module Documents

| Area | Document |
|---|---|
| Backend root | [../app/README.md](../app/README.md) |
| Core infrastructure | [../app/core/README.md](../app/core/README.md) |
| Models | [../app/models/README.md](../app/models/README.md) |
| Schemas | [../app/schema/README.md](../app/schema/README.md) |
| Repositories | [../app/repository/README.md](../app/repository/README.md) |
| Router layer | [../app/router/README.md](../app/router/README.md), [../app/router/v1/README.md](../app/router/v1/README.md) |
| Service layer | [../app/service/README.md](../app/service/README.md) |
| CV optimization | [../app/service/optimization/README.md](../app/service/optimization/README.md) |
| Voice interview | [../app/service/interview/README.md](../app/service/interview/README.md) |
| Workers | [../app/workers/README.md](../app/workers/README.md) |
| Migration | [../migration/README.md](../migration/README.md) |
| Infrastructure | [../infra/README.md](../infra/README.md) |
| Tests | [../tests/README.md](../tests/README.md) |

## 🛠️ Maintenance Checklist

Use this checklist whenever API behavior, environment variables, deployment shape or major product flows change.

| Check | Files to update |
|---|---|
| New endpoint or changed request/response | [../README.md](../README.md), [../app/router/v1/README.md](../app/router/v1/README.md), related schema/service docs |
| New environment variable | [../README.md](../README.md), [../.env.example](../.env.example), [../.env.production.example](../.env.production.example) |
| New frontend route or workflow | [../README.md](../README.md), [../DESIGN.md](../DESIGN.md), [FLOW_STUDY_CASES.md](FLOW_STUDY_CASES.md) |
| New worker or background job | [../README.md](../README.md), [../app/workers/README.md](../app/workers/README.md), [../infra/README.md](../infra/README.md) |
| New dependency or library | [../README.md](../README.md), [../pyproject.toml](../pyproject.toml), [../frontend/package.json](../frontend/package.json) as applicable |
| New risk, known gap or production caveat | [PROJECT_REPORT.md](PROJECT_REPORT.md), [../TODO.md](../TODO.md), [../DESIGN.md](../DESIGN.md) if UX-related |

## ✅ Documentation Health

| Area | Status |
|---|---|
| Root README | Professional overview, badges, setup, API surface, libraries and operations notes |
| System architecture | Covered in [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) |
| Project status | Covered in [PROJECT_REPORT.md](PROJECT_REPORT.md) and [../TODO.md](../TODO.md) |
| Backend module docs | Present across `app/*/README.md` |
| Test docs | Covered in [../tests/README.md](../tests/README.md) |
| Deployment docs | Covered in [../infra/README.md](../infra/README.md) and compose files |

## 🤝 Contribution Flow

1. Start with [../CONTRIBUTING.md](../CONTRIBUTING.md).
2. Update the relevant code and matching docs in the same change.
3. Run the quality gates listed in [../README.md](../README.md#-quality-gates).
4. Keep root README concise; put deep implementation notes in the closest module README.
