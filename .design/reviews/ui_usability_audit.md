# UI Usability Audit

Date: 2026-07-07

## Executive Summary

LancerAI already has a strong AI SaaS foundation: consistent tokens, a real sidebar/topbar shell, reusable cards, AI response panels, status badges, score bars, and lightweight product visuals. The main usability gaps are not about basic styling; they are about user orientation, workspace flexibility, and making the live interview unmistakably voice-first.

Highest-impact issues:

- Sidebar is fixed-width and cannot collapse, so dense pages lose focus space.
- Voice interview still exposes a manual text-answer form, which conflicts with the product promise of voice-first practice.
- Dashboard is metric-heavy but needs a clearer feature launcher for first-time users.
- Some pages explain results well, but users need more explicit "what to do next" actions after AI output.
- Responsive behavior is mostly solid through global grids, but inline grids in some pages can still feel crowded.

## Page-by-Page Review

### Dashboard

- Confusing: "Operations dashboard" is serviceable but does not immediately guide a new candidate to the main flows.
- Visually weak: metrics and flow are clear, but feature discoverability depends on sidebar/topbar.
- Hard to use: users need to infer where to start for Question Bank, Job Matching, CV Analysis, or Interview.
- Redundant: none severe.
- Feels unfinished: lacks a concise feature/action hub.
- Improve: add a feature launcher with icons, descriptions, status, and primary actions.
- Keep: metrics, recent sessions, evaluation quality panels.

### Voice Interview Setup

- Confusing: improved IT-role selector is good; modal is still long and needs clearer "voice practice" framing.
- Visually weak: setup is functional but can feel form-heavy.
- Hard to use: users with question-bank/job context need reassurance that context is loaded.
- Redundant: broad industry fields have already been removed.
- Improve: keep context alerts and role/level clarity.
- Keep: CV validation, JD fetch, IT role scope, mode cards.

### Live Interview / Chat

- Confusing: text input suggests the interview can be typed, conflicting with the voice-first requirement.
- Visually weak: state card works, but it should explicitly say what the AI is doing and what the user should do next.
- Hard to use: no clear voice-only cue when listening/recording.
- Redundant: manual text answer form.
- Feels unfinished: retry/next action language is underdeveloped, but backend does not expose retry controls yet.
- Improve: remove typed input, replace with voice-first guidance panel and clearer phase labels.
- Keep: transcript, AI/candidate visual panes, session integrity signals, report button.

### Question Bank

- Confusing: page is discoverable after route addition; filters are useful.
- Visually weak: cards can benefit from stronger metadata and clearer selected state.
- Hard to use: selected practice action exists, but first-time users need a simple route back to Interview.
- Redundant: none severe.
- Improve: keep detail panel and selected session actions; ensure sidebar entry is visible.
- Keep: search, filters, tag chips, question detail, practice actions.

### CV Upload / CV Extraction

- Confusing: flow is understandable.
- Visually weak: some older extraction result sections still use legacy inline styles and old spacing aliases.
- Hard to use: extraction result can be dense after parsing.
- Redundant: none severe.
- Improve: future pass should align extraction result with new Panel/AppUI primitives.
- Keep: upload validation, extraction progress, route continuity.

### CV Optimization

- Confusing: clear "review before accepting" workflow.
- Visually weak: inline comparison cards are useful but dense on small screens.
- Hard to use: export buttons are clear; missing "practice gaps" connection could be stronger.
- Redundant: none severe.
- Improve: keep IT-only domains and review-first AI summary; future pass can add responsive compare CSS.
- Keep: scorecard, weak points, rewrite compare, export actions.

### Job Matching

- Confusing: redesigned job collection makes the flow clearer.
- Visually weak: result cards are strong enough for MVP.
- Hard to use: users should clearly see "match -> missing skills -> prepare interview/questions".
- Redundant: none severe.
- Improve: keep candidate-side action handoffs to Interview and Question Bank.
- Keep: collection, filters, JD input modes, match score, missing skills table.

### Practice History / My Records

- Confusing: route name `/candidate` is legacy, but visible label is now "My Records".
- Visually weak: table is clear; inspector panel is a placeholder.
- Hard to use: records derive only from interview sessions.
- Redundant: candidate-management language was removed.
- Improve: future pass could rename route if backward compatibility allows.
- Keep: report access and evidence-first positioning.

### Reports / Analytics

- Confusing: generally clear for demo analytics.
- Visually weak: should continue using score cards and AI insight panels.
- Hard to use: no severe issue found.
- Redundant: none severe.
- Improve: future pass can add trend explanations and "what changed since last session".
- Keep: metrics, report cards, evidence-oriented copy.

### Navigation / Workspace

- Confusing: labels are clear, but fixed sidebar lacks focus mode.
- Visually weak: collapsed state does not exist.
- Hard to use: on content-heavy pages users cannot reclaim horizontal space.
- Redundant: saved views are helpful but should hide in compact mode.
- Improve: implement collapsible sidebar with icon-only compact mode, active route retention, smooth layout resize.
- Keep: route grouping, topbar actions, user menu.

## Accessibility Notes

- Strengths: global focus styles, semantic buttons, accessible alerts in newer components.
- Issues: live interview typed answer input should be removed; some old inline sections still need explicit labels/regions.
- Improve: keep `aria-live` for AI/interview status and alerts; add aria labels/titles to icon-only sidebar controls.

## Responsive Notes

- Strengths: global breakpoints collapse dashboard grids and hide desktop sidebar below 1120px.
- Issues: desktop collapsed sidebar state is missing; inline grid styles in a few pages may still crowd at mid widths.
- Improve: collapsed sidebar width variable and topbar/page resizing; avoid content hidden behind fixed nav.

## What Should Stay Unchanged

- Current React/Vite stack and route structure.
- Reusable AppUI primitives.
- Lightweight SVG/CSS visuals.
- Existing backend API contracts.
- Voice transcript/report flow.

