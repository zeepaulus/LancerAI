# LancerAI Component Plan

Date: July 5, 2026  
Source design system: `.design/design-system/design-system.md`

## Purpose

This document maps the LancerAI design system to the application pages:

- Dashboard
- Interview
- Candidate
- CV Analysis
- Job Matching
- Reports
- Settings

It defines page goals, flows, actions, information hierarchy, components, responsive behavior, and a complete component tree. This is not React code.

## Product Shell

### Global Goal

Create a persistent operational workspace where recruiters and hiring teams can move between candidates, interviews, AI evaluations, job matching, and analytics without losing context.

### Global Layout

- **App shell:** dark neutral application frame.
- **Primary sidebar:** persistent desktop navigation.
- **Top bar:** page title, global search, command menu trigger, notifications, workspace/user controls.
- **Main content:** page-specific work surface.
- **Optional right panel:** candidate, interview, evaluation, evidence, or assistant context.
- **Global AI composer:** available as a drawer or contextual panel, never replacing the main workflow by default.

### Global Navigation

Primary sidebar order:

1. Dashboard
2. Interview
3. Candidate
4. CV Analysis
5. Job Matching
6. Reports
7. Settings

Supporting sidebar groups:

- Inbox / Review Queue
- Saved Views
- Pinned Jobs
- Recent Candidates

### Global Components

- AppShell
- PrimarySidebar
- SidebarSection
- SidebarItem
- SidebarBadge
- TopBar
- Breadcrumbs
- GlobalSearch
- CommandMenu
- NotificationCenter
- UserMenu
- WorkspaceSwitcher
- PageHeader
- PageToolbar
- FilterBar
- ViewSwitcher
- DateRangePicker
- EmptyState
- LoadingState
- ErrorState
- Toast
- Modal
- Drawer
- RightInspectorPanel
- AIComposer

## Dashboard Page

### Goal

Give hiring teams a fast operational overview of recruiting health, pending work, interview progress, AI evaluation quality, and bottlenecks.

### User Flow

1. User opens Dashboard.
2. User scans urgent work: pending reviews, interviews today, low-confidence evaluations, blocked jobs.
3. User reviews funnel and hiring velocity metrics.
4. User drills into a metric, such as "Needs review" or "Interview no-shows."
5. Dashboard applies a filter and opens the relevant candidate/interview list.
6. User takes action or navigates into a candidate/job detail.

### Main Actions

- Review pending evaluations.
- Start or resume an interview.
- Open candidate queue.
- Filter dashboard by job, department, owner, and date range.
- Drill into funnel, interview, and AI quality metrics.
- Export dashboard snapshot.
- Ask AI to summarize hiring health.

### Information Hierarchy

1. Page title and timeframe.
2. Urgent work strip.
3. KPI cards.
4. Recruiting funnel.
5. Interview operations.
6. AI evaluation quality.
7. Job matching insights.
8. Recent activity and recommended actions.

### Components

- PageHeader
- DateRangePicker
- DashboardFilterBar
- UrgentWorkStrip
- KPICard
- FunnelChart
- TrendChart
- DistributionChart
- InsightCard
- DrillDownTable
- ActivityTimeline
- AIInsightSummary
- EmptyAnalyticsState
- ChartLoadingSkeleton

### Responsive Behavior

- Desktop: 12-column dashboard grid with KPI row, charts, and tables.
- Tablet: KPI cards become 2 columns; charts stack into wider rows; right-side summaries move below charts.
- Mobile: urgent work first, then KPI cards, then simplified charts, then drill-down lists.
- Dashboard filters collapse into a filter drawer on mobile.
- Drill-down tables become stacked list rows on mobile.

## Interview Page

### Goal

Support scheduled, live, and completed voice interviews with clear state handling for recording, transcription, AI evaluation, evidence review, and human decision-making.

### User Flow

1. User opens Interview page.
2. User chooses Today, Upcoming, Completed, or Needs Review.
3. User opens an interview session.
4. Before the session, user reviews candidate, job, rubric, and suggested questions.
5. During the session, user monitors voice state, transcript, and question progress.
6. After completion, system transcribes and evaluates.
7. User reviews AI evaluation, evidence, and confidence.
8. User approves, overrides, or sends for review.

### Main Actions

- Schedule interview.
- Start voice interview.
- Join/resume interview.
- Generate interview questions.
- View transcript.
- Run or rerun AI evaluation.
- Add human notes.
- Approve evaluation.
- Mark candidate outcome.
- Share interview report.

### Information Hierarchy

1. Interview status and schedule.
2. Candidate and job context.
3. Live voice controls or completed session summary.
4. Interview question guide.
5. Transcript.
6. AI evaluation.
7. Evidence and notes.
8. Activity and audit history.

### Components

- InterviewTabs
- InterviewQueueTable
- InterviewCalendarStrip
- InterviewSessionHeader
- CandidateContextCard
- JobContextCard
- VoiceSessionPanel
- VoiceStateIndicator
- AudioLevelMeter
- QuestionGuidePanel
- LiveTranscriptPanel
- TranscriptSearch
- SpeakerTurn
- EvaluationStatusBanner
- EvaluationReportPanel
- EvidencePanel
- NotesPanel
- HumanDecisionPanel
- InterviewActivityTimeline

### Responsive Behavior

- Desktop: split session view with voice/question panel left and transcript/evaluation right.
- Desktop review mode: main transcript with right evaluation inspector.
- Tablet: transcript and evaluation become tabs; session controls stay sticky.
- Mobile: voice controls dominate the first screen; transcript, notes, and evaluation are separate stacked sections.
- Interview controls must remain reachable without scrolling during a live session.

## Candidate Page

### Goal

Provide a central workspace for managing candidates across pipeline stages, CV data, interviews, evaluations, matches, notes, and decisions.

### User Flow

1. User opens Candidate page.
2. User chooses table, board, or saved view.
3. User filters candidates by job, stage, score, owner, source, risk, or evaluation status.
4. User selects a candidate row or card.
5. Candidate detail panel opens.
6. User reviews summary, CV, interview history, evaluation, job matches, and activity.
7. User takes action: invite, shortlist, reject, assign, add note, request review.

### Main Actions

- Add candidate.
- Upload CV.
- Import candidates.
- Filter and search candidates.
- Switch table/board views.
- Invite to interview.
- Move pipeline stage.
- Assign owner.
- Add note.
- Compare candidates.
- Shortlist or reject.
- Ask AI about candidate.

### Information Hierarchy

1. Candidate list controls and saved views.
2. Candidate table or pipeline board.
3. Candidate status, stage, and match score.
4. Candidate detail overview.
5. CV summary.
6. Interviews.
7. Evaluations.
8. Job matches.
9. Notes and activity.

### Components

- CandidatePageHeader
- SavedViewTabs
- CandidateFilterBar
- CandidateViewSwitcher
- CandidateBulkActionBar
- CandidateTable
- CandidateTableRow
- CandidateBoard
- CandidateStageColumn
- CandidateCard
- CandidateDetailPanel
- CandidateProfileHeader
- CandidateScoreStrip
- CandidateMetadataGrid
- CandidateTimeline
- CandidateNotesPanel
- CandidateAIComposer
- CandidateCompareDrawer

### Responsive Behavior

- Desktop: table/board with right candidate inspector.
- Tablet: inspector becomes a drawer; board supports horizontal scroll.
- Mobile: default to candidate list cards; filters open in drawer; detail becomes full page.
- Bulk actions collapse into a bottom action bar when rows are selected on mobile.

## CV Analysis Page

### Goal

Turn uploaded CVs into structured candidate intelligence: skills, experience, role fit, gaps, risks, evidence, and recommended next steps.

### User Flow

1. User opens CV Analysis.
2. User uploads one or more CVs or selects existing candidates without analysis.
3. System extracts structured data.
4. User reviews parsed profile, skills, experience, education, and evidence.
5. User chooses a target job for role-specific analysis.
6. System generates match explanation, gaps, and interview focus areas.
7. User saves analysis to candidate record or sends candidate to job matching/interview.

### Main Actions

- Upload CV.
- Select candidate.
- Run CV analysis.
- Choose target job.
- Compare CV against job requirements.
- Edit extracted fields.
- Save to candidate profile.
- Generate interview questions from CV.
- Flag missing evidence.
- Export CV analysis report.

### Information Hierarchy

1. Upload/selection state.
2. Processing status.
3. Parsed candidate identity.
4. Skills and experience summary.
5. Job-specific match analysis.
6. Evidence excerpts from CV.
7. Gaps, risks, and interview recommendations.
8. Save/export actions.

### Components

- CVAnalysisHeader
- CVUploadDropzone
- CVProcessingState
- CVQueueList
- ParsedProfilePanel
- SkillsMatrix
- ExperienceTimeline
- EducationPanel
- CertificationPanel
- JobSelector
- CVMatchSummary
- GapAnalysisCard
- EvidenceCitationList
- EditableExtractedField
- CVAssistantComposer
- AnalysisSaveBar

### Responsive Behavior

- Desktop: document/evidence preview on left, structured analysis on right.
- Desktop with target job: three-part layout when space allows: CV preview, analysis, match/evidence inspector.
- Tablet: CV preview and analysis become tabs.
- Mobile: upload and analysis cards stack; evidence excerpts open in bottom sheet.
- Batch upload view becomes a vertical queue on mobile.

## Job Matching Page

### Goal

Help users match candidates to jobs with explainable scores, criteria-level evidence, confidence, gaps, and alternative role suggestions.

### User Flow

1. User opens Job Matching.
2. User selects a job or candidate-first matching mode.
3. System shows ranked candidates or ranked jobs.
4. User filters by score, stage, location, skills, experience, availability, and confidence.
5. User opens match detail.
6. User reviews criteria fit, missing requirements, evidence, and AI explanation.
7. User shortlists, invites, rejects, or requests human review.

### Main Actions

- Select job.
- Select candidate.
- Run matching.
- Adjust criteria weighting.
- Filter ranked matches.
- Open match explanation.
- Compare candidates.
- Shortlist candidate.
- Invite to interview.
- Save match view.
- Export match report.

### Information Hierarchy

1. Matching mode and selected context.
2. Match summary metrics.
3. Ranked results.
4. Criteria breakdown.
5. Evidence and gaps.
6. Alternative recommendations.
7. Decision actions.

### Components

- MatchingModeToggle
- JobSelector
- CandidateSelector
- CriteriaWeightPanel
- MatchRunStatus
- MatchSummaryCards
- MatchResultsTable
- MatchResultRow
- MatchScoreBadge
- CriteriaFitChart
- MatchExplanationPanel
- RequirementGapList
- EvidencePanel
- AlternativeRolesList
- CandidateComparePanel
- MatchDecisionBar

### Responsive Behavior

- Desktop: ranked table with right match explanation panel.
- Tablet: criteria weighting becomes collapsible; explanation opens as drawer.
- Mobile: ranked matches appear as cards; criteria details expand inline.
- Comparison mode is desktop-first; mobile comparison should be limited to two candidates.

## Reports Page

### Goal

Provide exportable, shareable, and review-ready reporting for candidates, interviews, jobs, evaluations, hiring performance, and AI decision quality.

### User Flow

1. User opens Reports.
2. User selects report type or existing saved report.
3. User configures scope: job, candidate, date range, owner, stage, or department.
4. System previews report sections.
5. User edits included sections and visibility.
6. User exports, shares, schedules, or saves report.

### Main Actions

- Create report.
- Choose report template.
- Filter report scope.
- Preview report.
- Include/exclude sections.
- Export PDF/CSV.
- Share link.
- Schedule recurring report.
- Ask AI to summarize report.

### Information Hierarchy

1. Report library and templates.
2. Report scope controls.
3. Report preview.
4. Key findings.
5. Supporting tables/charts.
6. Export/share settings.
7. Report history.

### Components

- ReportsHeader
- ReportTemplateGrid
- SavedReportsList
- ReportScopeFilterBar
- ReportBuilderPanel
- ReportSectionToggleList
- ReportPreviewCanvas
- ReportInsightSummary
- ReportChartBlock
- ReportTableBlock
- ExportOptionsPanel
- ShareReportModal
- ScheduleReportModal
- ReportHistoryTable

### Responsive Behavior

- Desktop: template/library left, preview center, configuration right.
- Tablet: configuration becomes drawer; preview remains primary.
- Mobile: report creation becomes step-based: template, scope, sections, preview, export.
- Large report tables become downloadable or horizontally scrollable on mobile.

## Settings Page

### Goal

Let administrators configure workspace, users, roles, integrations, interview settings, AI evaluation rules, data privacy, billing, and notification preferences.

### User Flow

1. User opens Settings.
2. User selects a settings category from the settings sidebar.
3. User reviews current configuration.
4. User edits fields, toggles, integrations, or rules.
5. System validates changes.
6. User saves changes.
7. For high-risk changes, user confirms and audit event is recorded.

### Main Actions

- Update workspace profile.
- Manage users and roles.
- Configure interview defaults.
- Configure AI evaluation rubrics.
- Manage integrations.
- Set privacy and retention rules.
- Configure notifications.
- Manage billing.
- View audit logs.

### Information Hierarchy

1. Settings category navigation.
2. Section title and description.
3. Current configuration.
4. Editable controls.
5. Validation and warnings.
6. Save/cancel actions.
7. Audit or history when relevant.

### Components

- SettingsLayout
- SettingsSidebar
- SettingsSectionHeader
- SettingsCard
- FormField
- TextInput
- SelectInput
- MultiSelectInput
- ToggleRow
- CheckboxGroup
- RolePermissionsTable
- UserManagementTable
- IntegrationCard
- RubricEditor
- PrivacyRetentionPanel
- NotificationPreferenceList
- BillingSummaryCard
- AuditLogTable
- SaveChangesBar
- ConfirmDangerModal

### Responsive Behavior

- Desktop: settings sidebar plus main settings form.
- Tablet: settings sidebar becomes category dropdown or drawer.
- Mobile: settings categories become a list first; each section opens as a full page.
- Save bar sticks to bottom when unsaved changes exist.
- Large permission tables become grouped role cards on mobile.

## Complete Component Tree

```text
LancerAIApp
  AppShell
    PrimarySidebar
      WorkspaceSwitcher
      SidebarSection: Main
        SidebarItem: Dashboard
        SidebarItem: Interview
        SidebarItem: Candidate
        SidebarItem: CV Analysis
        SidebarItem: Job Matching
        SidebarItem: Reports
        SidebarItem: Settings
      SidebarSection: Review Queue
        SidebarItem: Pending Evaluations
        SidebarItem: Low Confidence
        SidebarItem: Interview Issues
      SidebarSection: Saved Views
        SavedViewItem
      SidebarSection: Pinned Jobs
        PinnedJobItem
      UserMenu
    TopBar
      Breadcrumbs
      GlobalSearch
      CommandMenuTrigger
      NotificationCenter
      GlobalAITrigger
    MainRouter
      DashboardPage
        PageHeader
          PageTitle
          DateRangePicker
          DashboardActions
        DashboardFilterBar
          JobFilter
          DepartmentFilter
          OwnerFilter
          StageFilter
        UrgentWorkStrip
          UrgentWorkItem
        DashboardGrid
          KPIRow
            KPICard
          RecruitingFunnelSection
            FunnelChart
            DrillDownTable
          InterviewOperationsSection
            TrendChart
            DistributionChart
            InsightCard
          AIEvaluationQualitySection
            ConfidenceDistributionChart
            OverrideRateChart
            LowEvidenceTable
          JobMatchingSection
            MatchDistributionChart
            TopMatchesTable
          RecentActivitySection
            ActivityTimeline
          AIInsightSummary
      InterviewPage
        PageHeader
          PageTitle
          InterviewPrimaryActions
        InterviewTabs
          Tab: Today
          Tab: Upcoming
          Tab: Completed
          Tab: Needs Review
        InterviewFilterBar
        InterviewQueueView
          InterviewCalendarStrip
          InterviewQueueTable
            InterviewTableRow
        InterviewSessionView
          InterviewSessionHeader
          SessionContextRail
            CandidateContextCard
            JobContextCard
            RubricSummaryCard
          VoiceSessionPanel
            VoiceStateIndicator
            AudioLevelMeter
            VoiceControlBar
          QuestionGuidePanel
            QuestionCard
            FollowUpSuggestionList
          LiveTranscriptPanel
            TranscriptSearch
            SpeakerTurn
          EvaluationReportPanel
            EvaluationStatusBanner
            CriteriaScoreList
            RecommendationSummary
          EvidencePanel
            EvidenceCitationList
          NotesPanel
          HumanDecisionPanel
          InterviewActivityTimeline
      CandidatePage
        CandidatePageHeader
          PageTitle
          CandidatePrimaryActions
        SavedViewTabs
        CandidateFilterBar
          SearchInput
          JobFilter
          StageFilter
          ScoreFilter
          OwnerFilter
          SourceFilter
          RiskFilter
        CandidateViewSwitcher
        CandidateBulkActionBar
        CandidateWorkSurface
          CandidateTable
            CandidateTableHeader
            CandidateTableRow
          CandidateBoard
            CandidateStageColumn
              CandidateCard
        CandidateDetailPanel
          CandidateProfileHeader
          CandidateScoreStrip
          CandidateMetadataGrid
          CandidateDetailTabs
            Tab: Overview
              CandidateSummary
              NextBestActions
            Tab: CV
              CVSummaryPanel
              SkillsMatrix
            Tab: Interviews
              CandidateInterviewList
            Tab: Evaluation
              EvaluationReportPanel
            Tab: Matches
              MatchSummaryList
            Tab: Activity
              CandidateTimeline
          CandidateNotesPanel
          CandidateAIComposer
        CandidateCompareDrawer
      CVAnalysisPage
        CVAnalysisHeader
          PageTitle
          CVAnalysisActions
        CVAnalysisWorkspace
          CVUploadDropzone
          CVQueueList
            CVQueueItem
          CVProcessingState
          CVPreviewPanel
          ParsedProfilePanel
            EditableExtractedField
            SkillsMatrix
            ExperienceTimeline
            EducationPanel
            CertificationPanel
          JobSelector
          CVMatchSummary
          GapAnalysisCard
          EvidenceCitationList
          CVAssistantComposer
          AnalysisSaveBar
      JobMatchingPage
        PageHeader
          PageTitle
          MatchingPrimaryActions
        MatchingControlBar
          MatchingModeToggle
          JobSelector
          CandidateSelector
          CriteriaWeightPanel
        MatchRunStatus
        MatchSummaryCards
          KPICard
        MatchWorkspace
          MatchResultsTable
            MatchResultRow
              MatchScoreBadge
          MatchExplanationPanel
            CriteriaFitChart
            RequirementGapList
            EvidencePanel
            AlternativeRolesList
            MatchDecisionBar
          CandidateComparePanel
      ReportsPage
        ReportsHeader
          PageTitle
          ReportsPrimaryActions
        ReportsWorkspace
          ReportsLibraryPanel
            ReportTemplateGrid
            SavedReportsList
          ReportScopeFilterBar
          ReportBuilderPanel
            ReportSectionToggleList
          ReportPreviewCanvas
            ReportInsightSummary
            ReportChartBlock
            ReportTableBlock
          ExportOptionsPanel
          ReportHistoryTable
        ShareReportModal
        ScheduleReportModal
      SettingsPage
        SettingsLayout
          SettingsSidebar
            SettingsNavItem: Workspace
            SettingsNavItem: Users & Roles
            SettingsNavItem: Interview
            SettingsNavItem: AI Evaluation
            SettingsNavItem: Integrations
            SettingsNavItem: Privacy
            SettingsNavItem: Notifications
            SettingsNavItem: Billing
            SettingsNavItem: Audit Logs
          SettingsContent
            SettingsSectionHeader
            SettingsCard
              FormField
              TextInput
              SelectInput
              MultiSelectInput
              ToggleRow
              CheckboxGroup
            UserManagementTable
            RolePermissionsTable
            IntegrationCard
            RubricEditor
            PrivacyRetentionPanel
            NotificationPreferenceList
            BillingSummaryCard
            AuditLogTable
            SaveChangesBar
            ConfirmDangerModal
    GlobalOverlays
      CommandMenu
        CommandSearchInput
        CommandResultList
        CommandActionList
      GlobalAIComposerDrawer
        AIContextHeader
        AIComposer
        StreamingResponse
        EvidenceCitationList
      NotificationDrawer
      ToastRegion
      ModalLayer
      DrawerLayer
```

## Shared State Patterns

### Object Status

All major objects should use consistent status badges:

- Candidate stage.
- Interview state.
- Transcript state.
- Evaluation state.
- Match confidence.
- Report export state.
- Integration health.

### AI Transparency

Any AI-generated output should expose:

- Confidence.
- Source evidence.
- Generation timestamp.
- Model/evaluation version when relevant.
- Human override state.
- Rerun action when applicable.

### Empty States

Each page should have a page-specific empty state:

- Dashboard: no activity yet; prompt to add job or import candidates.
- Interview: no interviews scheduled; prompt to schedule or invite.
- Candidate: no candidates; prompt to upload CVs or import.
- CV Analysis: no CV selected; prompt to upload.
- Job Matching: no job or candidate selected; prompt to choose matching mode.
- Reports: no saved reports; prompt to create from template.
- Settings: no special empty state except integrations/audit logs.

### Loading States

- Dashboard: skeleton KPI cards and chart panels.
- Interview: session state banner, transcript processing, evaluation running.
- Candidate: skeleton table rows and detail panel.
- CV Analysis: file upload progress and extraction phases.
- Job Matching: match run progress and criteria evaluation phases.
- Reports: preview generation skeleton.
- Settings: inline save/loading indicators.

## Implementation Notes for Future Frontend Work

- Use the design system tokens from `design-system.md` consistently before creating page-specific styles.
- Start with AppShell, Sidebar, TopBar, PageHeader, FilterBar, Table, Card, Badge, Drawer, Modal, and AIComposer as foundational components.
- Build Candidate and Interview components early because most other pages depend on their object patterns.
- Treat Dashboard, Reports, and Job Matching as data composition pages using shared charts, tables, filters, and detail panels.
- Keep responsive behavior planned at the component level, especially for tables, detail panels, transcript views, and dashboards.
