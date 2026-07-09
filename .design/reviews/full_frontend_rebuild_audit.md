# LancerAI Full Frontend Rebuild Audit

Date: 2026-07-07

## Routes And Pages

- `/` - `LandingPage`
- `/login`, `/signup` - `AuthPage`
- `/about` - `AboutUsPage`
- `/dashboard` - `MainDashboard`
- `/candidate` - `CandidatePage`
- `/profile` - `ProfilePage`
- `/settings` - `AccountSettingsPage`
- `/cv-upload` - `CVUploadPage`
- `/cv-extraction-result` - `CVExtractionResultPage`
- `/cv-optimization` - `CVOptimizationPage`
- `/cv-review` - `CVReviewPage`
- `/job-matching` - `JobMatchingPage`
- `/job-recommendations` - `JobRecommendationsPage`
- `/interview` - `InterviewPage`
- `/chat` - `ChatPage`
- `/interview-report` - `InterviewReportPage`
- `/question-bank` - `QuestionBankPage`
- `/reports` - `ReportsPage`

## Pages Requiring Rebuild

- `ChatPage`: legacy inline-style-heavy interview workspace. Highest priority. Keep live interview logic, rebuild UI with theme-aware classes and remove text-first affordances.
- `CVExtractionResultPage`: older extraction layout with heavy inline styling and weaker hierarchy.
- `ProfilePage`: functional but plain.
- `AboutUsPage`: older static page style, less aligned with app shell.
- `JobRecommendationsPage`: functional but lightweight and should feel like job intelligence.
- `CVReviewPage`: simple list page, needs polished empty/list states.
- `AuthPage` and `LandingPage`: mostly polished but still have inline styles and a few old tokens.

## Components To Reuse

- `Navbar`: collapsible workspace already exists.
- `AppUI`: `Page`, `PageHero`, `Panel`, `MetricCard`, `QuickActionCard`, `ProgressCard`, `EmptyState`, `AIResponsePanel`, `StatusBadge`, `ScoreBar`.
- `Visuals`: original CSS/SVG product mockups and AI/CV/voice visuals.

## Components To Expand

- Add `SectionHeader`, `AIStatusPanel`, `InterviewStateCard`, `TimelineItem`, `ActionToolbar`, `SearchFilterBar`, `ReportPanel`, `MatchScoreCard`.
- Add CSS classes for chat/interview workspace, extraction result, profile summary, about page, and recommendation cards.

## Theme Problems

- Most global tokens are now semantic, but some legacy pages still use inline `backgroundColor`, old aliases, or fixed rgba values.
- `ChatPage` still has legacy style objects and older token aliases.
- Some overlays and tiny badges were already moved to tokens, but all remaining legacy pages need class-based theme styling.

## Layout Problems

- Legacy pages use bespoke layout blocks rather than reusable page structure.
- `ChatPage` combines video, status, question, transcript, controls, and feedback in a dense custom layout.
- CV extraction output is information-rich but hard to scan.
- Profile/About/Recommendation pages feel less premium than Dashboard/Question Bank.

## Responsiveness Problems

- Global grids collapse, but legacy inline grids may not.
- Chat workspace needs a stable two-column desktop layout and one-column mobile layout.
- Extraction and profile tables need card-like mobile behavior.

## Risk Before Implementation

- `ChatPage` contains live interview state and API flow; logic must be preserved while replacing rendering.
- Avoid backend/API changes.
- Avoid removing JD/context textareas on `InterviewPage`; those are not manual answer inputs.
- Build must pass after every import/component expansion.

## Implementation Priority

1. Add reusable UI components and CSS for missing rebuild surfaces.
2. Rebuild `ChatPage` UI around existing state handlers.
3. Rebuild `CVExtractionResultPage`, `ProfilePage`, `JobRecommendationsPage`, `CVReviewPage`, `AboutUsPage`.
4. Clean remaining hard-coded colors that break theme.
5. Run `npm run build`.
