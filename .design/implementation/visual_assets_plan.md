# LancerAI Visual Assets Plan

Date: July 5, 2026  
Scope: Frontend visual assets, placeholders, illustrations, avatars, empty states, dashboard visuals, and product mockups.

This is a recommendation document only. No frontend implementation is included.

## Visual Direction

LancerAI should use a modern AI SaaS visual language: precise, calm, evidence-driven, and operational. The style should be inspired by the product qualities of Linear, ChatGPT, and Vercel without copying them directly.

Recommended visual personality:

- **Linear influence:** compact product surfaces, dark graphite UI, metadata-rich mockups, clean status systems.
- **ChatGPT influence:** calm AI presence, conversational panels, soft assistant states, readable content surfaces.
- **Vercel influence:** precise dashboards, technical charts, monochrome discipline, trustworthy system states.

Avoid:

- Generic stock photos of offices, laptops, handshakes, or smiling corporate people.
- Decorative gradient orbs as primary visual assets.
- Emoji as product icons in production UI.
- Overly playful cartoons.
- AI cliches such as glowing brains, robot heads everywhere, or random neural-network backgrounds.

Preferred visual categories:

- CSS/SVG product diagrams.
- Abstract interface mockups.
- Minimal data visualizations.
- Generated bitmap hero/product images only when a richer marketing asset is needed.
- Initial-based or generated geometric avatars for candidates.

## Current Frontend Inventory

### Existing Real Image Assets

| Asset | Current Usage | Recommendation |
| --- | --- | --- |
| `frontend/src/assets/landing_image.png` | Landing hero image in `LandingPage.jsx` | Replace or refresh with an actual LancerAI product mockup/hero visual. Current direct `src="src/assets/..."` usage should eventually become an imported asset. |
| `frontend/src/assets/Logo/lancerai_logo.png` | Auth logo, likely legacy branding | Keep if brand-approved; otherwise replace with simplified app mark matching the graphite/teal system. |
| Social logos: Google, Microsoft, GitHub, LinkedIn | Auth OAuth buttons | Keep as logo assets. Use monochrome contained buttons for consistency. |
| Member photos under `assets/Members` | About Us profile photos | Keep for About page only. Not suitable for candidate avatars or product UI. |
| Public favicons/app icons | Browser/site identity | Keep, but eventually align colors with new brand tokens. |

### Current Placeholder/Visual Patterns Found

| Location | Current Pattern | Issue |
| --- | --- | --- |
| `LandingPage.jsx` | Three dashed `[ Image Placeholder ]` boxes | Looks unfinished and not production-ready. |
| `LandingPage.jsx` | Emoji feature icons | Casual and inconsistent with the new enterprise AI direction. |
| `AuthPage.jsx` | Gradient orb backgrounds | Conflicts with the new design guidance that avoids decorative orbs. |
| `ChatPage.jsx` | Inline SVG robot avatar and wave bars | Useful direction, but should be refined into a reusable AI assistant visual system. |
| `ChatPage.jsx` | Candidate video placeholder text | Functional but visually thin; needs a proper camera-off/candidate placeholder. |
| `MainDashboard.jsx`, `CandidatePage.jsx`, `ReportsPage.jsx`, `CVUploadPage.jsx`, `JobMatchingPage.jsx` | Text-only empty states or panels | Should include restrained visual diagrams/icons for stronger affordance. |
| `ProfilePage.jsx`, `Navbar.jsx` | Initial/avatar circle | Good baseline, but should become a reusable avatar system. |
| `CVOptimizationPage.jsx`, `InterviewReportPage.jsx` | SVG score rings/progress bars and emoji headings | Keep score visuals, replace emoji headings with icons/status marks. |

## Reusable Visual Template Categories

### 1. Candidate Avatar

**Where it should appear**

- Candidate page table and future candidate cards.
- Candidate detail/inspector panel.
- Interview session candidate stream fallback.
- Reports and evaluation summaries.
- Profile-like candidate identity areas.

**Recommended style**

- Geometric initials avatar.
- Dark neutral circular or rounded-square base.
- Subtle two-tone accent based on candidate stage or source.
- Optional tiny status ring: invited, interviewing, evaluated, needs review.

**Type**

- Avatar.

**CSS/SVG vs image**

- Implement with CSS by default.
- Use generated bitmap only for user-uploaded candidate photos if the product later supports them.

**Template direction**

- Graphite background.
- Initials in high-contrast text.
- Small semantic status dot.
- Optional deterministic abstract pattern based on candidate ID.

### 2. Empty Interview State

**Where it should appear**

- `InterviewPage.jsx` when no sessions exist.
- Dashboard review queue when no interview data exists.
- Reports page when no report exists.

**Recommended style**

- Minimal product diagram: a voice waveform, transcript column, and evaluation score chip.
- Use graphite panels with teal/purple accents.
- Should feel like an empty workspace ready to start, not a mascot illustration.

**Type**

- Abstract product graphic or SVG illustration.

**CSS/SVG vs image**

- Prefer SVG or CSS. It can be built from cards, lines, dots, waveform bars, and status chips.

**Template direction**

- Small mock interview room card.
- Left side: voice waveform.
- Right side: transcript lines.
- Bottom: `Evaluating` status badge and confidence indicator.

### 3. Voice Interview Illustration

**Where it should appear**

- `ChatPage.jsx` AI stream card.
- `InterviewPage.jsx` lifecycle panel.
- Landing page voice interview section.

**Recommended style**

- Full product mockup rather than cartoon microphone.
- Show two stacked/side-by-side panes: AI interviewer and candidate.
- Animated waveform can be CSS.
- Voice state should be visually encoded: listening, processing, speaking, ended.

**Type**

- Product mockup with CSS/SVG.

**CSS/SVG vs image**

- Use CSS/SVG for app UI.
- A richer generated bitmap can be used on the marketing landing page if needed.

**Template direction**

- Dark video-card surface.
- AI avatar as abstract glowing core, not robot mascot.
- Candidate tile fallback with initials.
- Status strip: `Listening`, `Transcribing`, `Evaluating`.

### 4. CV Upload Illustration

**Where it should appear**

- `CVUploadPage.jsx` dropzone.
- Landing page CV analysis section.
- CV extraction empty state.
- CV review history empty state.

**Recommended style**

- Document-to-structured-data visual.
- A CV sheet on the left, extracted fields and skill chips on the right.
- Avoid generic upload cloud icons as the main visual.

**Type**

- SVG/product diagram.

**CSS/SVG vs image**

- Prefer SVG or CSS for the upload dropzone.
- Use product mockup image only for landing/marketing.

**Template direction**

- Thin document outline.
- Highlighted lines for name, experience, skills.
- Arrow or scan beam into structured field cards.
- Teal accent for completed extraction; purple for processing.

### 5. CV Extraction / Human Review Visual

**Where it should appear**

- `CVExtractionResultPage.jsx`.
- CV review pages.
- Candidate CV tab in future detail panel.

**Recommended style**

- Split document review mockup.
- Left: raw CV/document preview.
- Right: editable extracted fields.
- Confidence markers beside fields.

**Type**

- Product mockup.

**CSS/SVG vs image**

- CSS/SVG in-app.
- No bitmap needed unless used in marketing.

**Template direction**

- Monospace CV ID strip.
- Field confidence chips.
- Editable data rows.
- Evidence highlight overlays.

### 6. AI Assistant Panel

**Where it should appear**

- Global assistant drawer.
- Candidate assistant composer.
- CV assistant composer.
- Dashboard AI insight panel.
- Job matching explanation panel.

**Recommended style**

- ChatGPT-inspired calm conversation surface, but with LancerAI evidence cards.
- Avoid generic chat bubbles as the only visual.
- Include source/evidence chips and "working" phases.

**Type**

- Product pattern / panel visual.

**CSS/SVG vs image**

- CSS implementation preferred.

**Template direction**

- Composer at bottom.
- Suggested prompt chips.
- Streaming response line skeleton.
- Evidence cards with small source labels: CV, Transcript, JD, Rubric.

### 7. Job Matching Cards

**Where it should appear**

- `JobMatchingPage.jsx` before/after result states.
- `JobRecommendationsPage.jsx`.
- Candidate match tab.
- Landing job matching section.

**Recommended style**

- Ranked comparison cards with criteria bars.
- Candidate and job cards connected by fit lines or shared criteria chips.
- Avoid generic job board thumbnails.

**Type**

- Product mockup / abstract graphic.

**CSS/SVG vs image**

- CSS/SVG preferred.

**Template direction**

- Candidate card on left.
- Job card on right.
- Center match score ring or bar.
- Criteria chips: Skills, Experience, Location, Seniority.
- Gap chips in warning color.

### 8. Analytics / Report Mockup

**Where it should appear**

- `ReportsPage.jsx`.
- `MainDashboard.jsx`.
- `InterviewReportPage.jsx`.
- Landing analytics/reports section.

**Recommended style**

- Vercel-like structured dashboard mockup.
- KPI row, funnel chart, confidence distribution, and report table.
- Use restrained semantic colors.

**Type**

- Product mockup.

**CSS/SVG vs image**

- CSS/SVG in app.
- Generated bitmap acceptable for landing hero/marketing if it shows realistic UI.

**Template direction**

- Top KPI cards.
- Middle chart modules.
- Bottom report rows.
- Small `Evidence attached` / `Needs review` badges.

### 9. AI Evaluation Score Visual

**Where it should appear**

- `InterviewReportPage.jsx`.
- `CVOptimizationPage.jsx`.
- Dashboard evaluation quality panel.
- Candidate detail evaluation tab.

**Recommended style**

- Evidence-first score visualization.
- Keep circular score only for a single hero metric.
- Use criteria-level bars for the rest.

**Type**

- Data visualization.

**CSS/SVG vs image**

- CSS/SVG only.

**Template direction**

- Overall confidence metric.
- Criteria bars: Situation, Task, Action, Result, Role Fit.
- Evidence count indicator.
- Human override marker when applicable.

### 10. Camera-Off / Candidate Stream Placeholder

**Where it should appear**

- `ChatPage.jsx` candidate video tile when camera is unavailable or pending.
- Interview setup preview.

**Recommended style**

- Candidate initials/avatar in a video tile.
- Camera state label and subtle diagonal pattern.
- Avoid plain text-only placeholder.

**Type**

- Avatar + product state placeholder.

**CSS/SVG vs image**

- CSS/SVG only.

**Template direction**

- Dark inset panel.
- Center initials avatar.
- Bottom-left label: `Camera unavailable` or `Camera starting`.
- Tiny status dot.

### 11. Landing Hero Product Visual

**Where it should appear**

- `LandingPage.jsx` hero image.

**Recommended style**

- Full product composition, not a stock illustration.
- Show LancerAI as a live hiring intelligence workspace.
- Include dashboard, AI assistant panel, interview waveform, candidate score card.

**Type**

- Product mockup. Could be generated bitmap or hand-built HTML/CSS mockup.

**CSS/SVG vs image**

- Prefer generated bitmap or polished CSS mockup for landing hero.
- If used as an image, store as a real imported asset under `frontend/src/assets/visuals/`.

**Template direction**

- Dark graphite app shell.
- Teal intelligence signal.
- Purple voice/evaluation processing.
- Candidate table and right-side evidence inspector.
- No people photos.

### 12. Landing Section Visuals

**Where it should appear**

- `LandingPage.jsx` sections currently using `[ Image Placeholder ]`.

**Recommended style**

- Replace each dashed placeholder with a specific product mockup:
  - Problems section: ATS rejection/gap visualization.
  - Solutions section: AI interview + CV extraction workflow.
  - Differentiators section: evidence-backed evaluation comparison.

**Type**

- Product mockup / abstract product diagram.

**CSS/SVG vs image**

- CSS/SVG preferred for consistency and responsiveness.
- Generated bitmap acceptable if a more polished marketing surface is desired.

**Template direction**

- Use the same visual grammar as the app: panels, rows, badges, charts, transcripts.
- Avoid standalone decorative illustrations.

### 13. Auth Background Visual

**Where it should appear**

- `AuthPage.jsx`.

**Recommended style**

- Replace gradient orbs with subtle product grid or secure workspace texture.
- Keep auth focused and calm.

**Type**

- Abstract graphic or CSS background.

**CSS/SVG vs image**

- CSS preferred.

**Template direction**

- Very subtle grid lines.
- Low-opacity product panel silhouettes.
- Small brand mark.
- No animated orbs.

### 14. About / Team Avatars

**Where it should appear**

- `AboutUsPage.jsx`.

**Recommended style**

- Existing member photos are acceptable because this is a real team page.
- Add consistent crop, border, and fallback initials if an image fails.

**Type**

- Real avatar photo.

**CSS/SVG vs image**

- Keep image assets.

**Template direction**

- Circular or 8px-radius square avatars.
- Neutral border.
- Optional role badge.

## Page-by-Page Recommendations

### Landing Page

Current visual issues:

- Uses `landing_image.png` plus multiple dashed `[ Image Placeholder ]` boxes.
- Uses emoji icons in feature cards.
- Uses atmospheric orbs that no longer match the product design direction.

Recommended assets:

- Hero product mockup: dashboard + AI assistant + interview waveform.
- ATS problem mockup: rejected CV line, missing keyword chips, score warning.
- AI solution mockup: CV extraction, voice interview, evidence-backed score.
- Differentiator mockup: generic chat answer vs LancerAI evidence report.

Implementation style:

- Prefer CSS/SVG product mockups.
- Use one generated bitmap only for the hero if needed.

### Auth Page

Current visual issues:

- Decorative orbs and logo-only brand moment.
- Social icons are fine but should sit in a cleaner system.

Recommended assets:

- Subtle product-surface background.
- Small secure-workspace visual: stacked panels, shield/status chip, AI assistant mini-card.

Implementation style:

- CSS background and SVG/product-card composition.

### Dashboard

Current visual issues:

- Mostly cards/charts; no visual placeholder for empty analytics.

Recommended assets:

- Empty dashboard graphic.
- Analytics/report mockup for no-data state.
- Mini chart components for funnel, confidence distribution, and review queue.

Implementation style:

- CSS/SVG only.

### Interview Page

Current visual issues:

- Empty state is text/card-based.
- Lifecycle panel is useful but could use a compact voice-interview diagram.

Recommended assets:

- Empty interview state visual.
- Voice state diagram.
- AI interviewer tile mockup.

Implementation style:

- CSS/SVG only.

### Live Interview / Chat Page

Current visual issues:

- Inline robot SVG is serviceable but too mascot-like.
- Candidate camera-off placeholder is text-only.
- AI waveform can be formalized as a reusable visual.

Recommended assets:

- Abstract AI interviewer orb/core, not a robot face.
- Candidate camera-off avatar tile.
- Reusable waveform bars.
- Processing state strip.

Implementation style:

- CSS/SVG only.

### Candidate Page

Current visual issues:

- Candidate rows have no visual identity.
- Candidate inspector is text-led.

Recommended assets:

- Candidate avatar system.
- Candidate pipeline empty state.
- Candidate detail evidence mini-map.

Implementation style:

- CSS avatars and SVG mini diagrams.

### CV Upload / CV Analysis

Current visual issues:

- Upload surface is functional but visually sparse.
- CV extraction/review pages use forms and chips but no document-to-data visual.

Recommended assets:

- CV upload illustration.
- CV extraction visual.
- Evidence/highlight treatment.

Implementation style:

- CSS/SVG product diagram.

### Job Matching

Current visual issues:

- Input/result surfaces are clear but no match-specific visual language.

Recommended assets:

- Candidate-to-job matching cards.
- Criteria-fit graph.
- Gap chips with evidence icons.

Implementation style:

- CSS/SVG only.

### Reports / Analytics

Current visual issues:

- Report library is table-led.
- Empty report state needs visual explanation.

Recommended assets:

- Report preview mockup.
- Analytics dashboard mockup.
- Export/share visual state.

Implementation style:

- CSS/SVG product mockup.

### Settings

Current visual issues:

- Settings are intentionally utilitarian; visual assets should be minimal.

Recommended assets:

- Small category icons only.
- No large illustrations unless an integration category is empty.

Implementation style:

- SVG icons or CSS symbols.

## Recommended Asset Directory

If visual assets are added later, use this structure:

```text
frontend/src/assets/
  visuals/
    hero-product-mockup.png
    landing-ats-problem.png
    landing-ai-workflow.png
  illustrations/
    empty-interview.svg
    empty-dashboard.svg
    cv-upload.svg
    job-match.svg
    report-preview.svg
  avatars/
    candidate-patterns.svg
```

For CSS/SVG components, prefer:

```text
frontend/src/components/Common/Visuals/
  CandidateAvatar.jsx
  EmptyStateGraphic.jsx
  VoiceInterviewGraphic.jsx
  CVUploadGraphic.jsx
  JobMatchGraphic.jsx
  ReportMockupGraphic.jsx
  AIAssistantGraphic.jsx
```

## Priority Order

1. Replace landing page dashed `[ Image Placeholder ]` blocks.
2. Replace emoji feature icons with consistent SVG/icon marks.
3. Add reusable empty-state graphics for Dashboard, Interview, CV Upload, Candidate, Job Matching, and Reports.
4. Upgrade `ChatPage.jsx` AI/candidate video placeholders.
5. Add candidate avatar system.
6. Add report/dashboard mockup graphics.
7. Replace auth gradient orbs with subtle product-surface background.

## Final Recommendation

Use CSS/SVG for most in-app visuals because LancerAI is an operational SaaS product and needs crisp, theme-aware, responsive assets. Use generated bitmap images only for landing-page hero or marketing visuals where a richer first impression matters.

The strongest reusable visual language is not illustration-heavy. It should look like miniature LancerAI product surfaces: panels, transcripts, scorecards, evidence citations, job criteria, waveform states, and structured reports. That will make the product feel modern, trustworthy, and purpose-built for AI hiring workflows.
