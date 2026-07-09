# LancerAI Full Visual Redesign Plan

## Assumptions

- No backend/API contracts will be changed.
- No new npm packages will be added.
- Existing routes must remain stable.
- Original CSS/SVG visuals are preferred over downloading third-party assets in this pass.

## Global Components

| Area | Current Problem | Redesign Direction | Files | Risk | Expected UX Benefit |
| --- | --- | --- | --- | --- | --- |
| Tokens/theme | Sidebar/topbar/modal/card tokens incomplete; light theme less rich. | Add semantic surface, overlay, feature accent, and gradient tokens for both themes. | `src/index.css` | Medium | Consistent light/dark switching and premium surfaces |
| App shell | Workspace improved but can feel static. | Stronger theme-aware sidebar/topbar backgrounds, active icons, compact motion. | `Navbar.jsx`, `index.css` | Low | More polished navigation and focus mode |
| Shared UI | PageHeader/cards are useful but flat. | Add `PageHero`, `IconBadge`, `QuickActionCard`, `ProgressCard`, `FilterPill`; upgrade card/panel CSS. | `AppUI.jsx`, `index.css` | Medium | More reusable, vivid product system |
| Visuals | Good original visuals, but feature icon accents are limited. | Add tone support and richer glow/outline treatment using CSS variables. | `Visuals.jsx`, `index.css` | Low | More memorable empty states and action cards |

## Pages

| Page | Current Issue | Proposed Improvement | Files | Risk | Expected UX Benefit |
| --- | --- | --- | --- | --- | --- |
| Dashboard | Heavy grid, weak first impression. | Add hero command center with readiness score and quick actions; improve feature cards through global styles. | `MainDashboard.jsx`, `AppUI.jsx`, `index.css` | Medium | Users immediately know next best actions |
| Voice Interview | Some copy still says text input; live model is generic. | Remove text-first copy, add voice state cards and waveform-style visual language. | `InterviewPage.jsx`, `index.css` | Low | Clearer voice-first workflow |
| Chat | Legacy inline style risk. | Keep logic stable; rely on token aliases and avoid large rewrite. | `ChatPage.jsx`, `index.css` | High | Safer theme compatibility without breaking live interview |
| Question Bank | Detail exists but can be more vivid. | Keep three-pane layout, strengthen tags/detail cards via global CSS and qbank classes. | `QuestionBankPage.jsx`, `index.css` | Low | Easier search, review, and voice-practice handoff |
| Job Matching | Mojibake and generic cards. | Fix copy, add job-intelligence card styles and richer score panel classes. | `JobMatchingPage.jsx`, `index.css` | Medium | Better scanability and trust |
| CV Upload | Clear but not premium. | Use hero/action system and richer upload card through shared card styles. | `CVUploadPage.jsx`, `index.css` | Low | Upload pipeline feels intentional |
| CV Optimization | Strong logic, mixed visual density. | Let global AI panels/cards/metrics provide more polish; avoid API changes. | `CVOptimizationPage.jsx`, `index.css` | Medium | Better readability of AI suggestions |
| Reports | Functional tables and metrics. | Improve metric/report panel styling globally; use analytics accent. | `ReportsPage.jsx`, `index.css` | Low | Faster scanning |
| Settings/Profile | Generic tabs/buttons. | Improve category buttons using segmented/card styles and stronger modal tokens. | `AccountSettingsPage.jsx`, `index.css` | Low | Simpler workspace configuration |

## Implementation Order

1. Patch docs and asset log.
2. Expand tokens and shared component CSS.
3. Add reusable components in `AppUI.jsx`.
4. Update Dashboard to use the stronger hero and progress components.
5. Update Interview copy and state cards.
6. Fix Job Matching mojibake and card classes.
7. Run `npm run build`.
8. Check theme-sensitive areas and scan for answer text input regressions.
