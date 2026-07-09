# Full Frontend Rebuild Plan

## Shared UI

| Target | Current Issue | Rebuild Direction | Files | Risk |
| --- | --- | --- | --- | --- |
| AppUI | Missing some requested primitives. | Add `SectionHeader`, `AIStatusPanel`, `InterviewStateCard`, `TimelineItem`, `ActionToolbar`, `SearchFilterBar`, `ReportPanel`, `MatchScoreCard`, `LoadingState`, `ErrorState`. | `AppUI.jsx`, `index.css` | Medium |
| Global CSS | Legacy pages need classes. | Add chat workspace, extraction, profile, about, recommendation, timeline, toolbar, report styles. | `index.css` | Medium |
| Theme | Some fixed colors remain. | Keep semantic tokens and convert hard-coded color leaks where touched. | `index.css`, legacy pages | Low |

## Pages

| Page | Current Issue | Direction | Risk |
| --- | --- | --- | --- |
| ChatPage | Legacy inline-heavy live interview UI. | Preserve logic, rebuild render around voice-first panels and class styles. | High |
| CVExtractionResultPage | Older dense extraction output. | Rebuild into extraction dashboard with summary, raw text, structured sections, next actions. | Medium |
| ProfilePage | Plain profile/history view. | Add profile hero, summary metrics, polished tables/empty states. | Low |
| JobRecommendationsPage | Lightweight recommendation list. | Add hero, search-like recommendation cards, score bars, actions. | Low |
| CVReviewPage | Simple saved reviews page. | Add hero and polished review list/empty state. | Low |
| AboutUsPage | Legacy static layout. | Rebuild as branded product/team page using panels and cards. | Low |
| Auth/Landing | Mostly improved. | Clean fixed colors and let global CSS lift visuals. | Low |

## ChatPage Specific Plan

1. Keep session creation state, recording/transcript handlers, API calls, and report navigation.
2. Replace legacy render with `Navbar`, `Page`, `PageHero`, `Panel`, `AIStatusPanel`, `InterviewStateCard`, timeline transcript, and voice control deck.
3. Do not expose textarea/manual typed answer submission.
4. Preserve retry/next/report actions and status/error displays.

## Validation

- Run `npm run build`.
- Scan for manual typed answer UI.
- Scan for mojibake and obvious fixed theme leaks.
