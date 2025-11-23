# Code Review Status

## Current Review Cycle: 3
Date: 2025-11-07

## All Problems Identified
1. **Dashboards/reports still assume status-only semantics:** Now that approvals automatically obsolete the prior release (`apps/projects/services.py:140-214`), we need to verify the UI pages (e.g., project list filters, analytics cards) and any scheduled reports truly show the *latest* version instead of blindly listing every project with `status='Approved_Endorsed'`. Otherwise front-end views may still render multiple entries per group even though the backend enforces single ownership.

## Current Priority: Update every consumer of project lists/counts so it either asks the backend for “latest only” or deduplicates by `project_group_id`.
Rationale: The backend now enforces correctness, but until the UI/reporting layers reflect that invariant, users will continue to see duplicate “Approved” entries, inflated counts, or stale versions without guidance.

## Critical Thinking Errors That Led Here:
- Stopping at service-level correctness without tracing its impact on higher layers leads to inconsistent UX despite correct data.
- The assumption that “status is enough” in the UI ignored the subtle difference between “latest approved” and “all approved entries”.

## Incremental Refactoring Path to Fix Priority
### Inventory Results (Completed)
1. **React Dashboard (`frontend/src/pages/Dashboard.tsx`)** – Calls `projectService.getProjects()` (all versions) and counts statuses client-side, so superseded versions still inflate totals and appear in the “Recent Projects” list.
2. **React Projects list (`frontend/src/pages/projects/Projects.tsx`)** – Same data source; filtering by status/search operates on every version, so users see duplicates for each project group.
3. **React Project detail (`frontend/src/pages/projects/ProjectDetail.tsx`)** – Fetches a specific version and never indicates when it is `Obsolete`/superseded; lacks a link/button to jump to the latest approved version.
4. **Server-rendered dashboard (`templates/projects/dashboard.html` via `ProjectStatsService.get_user_project_stats`)** – Totals/pending/approved counts iterate over every historical version rather than the latest per group, so “Total Projects” and “Recent Projects” overcount after multiple releases.

### Full Sequence (Next Steps):
1. Introduce a backend-supported way to request only the latest project per `project_group_id` (e.g., query param on `/api/projects/` or dedicated endpoint).
2. Update React dashboard + projects list to consume the “latest only” feed (or group locally until the API lands) so counts/cards/showcases reflect a single active release.
3. Enhance the React project detail view to detect `status === 'Obsolete'` (or compare version to group max) and display a banner with a link to the latest version.
4. Refactor `ProjectStatsService.get_user_project_stats()` (and any other stats helpers) to compute counts based on the latest version per group so the Django dashboard matches the new data model.

### Current Step: 2
### Current Refactoring Task
Implement the backend filter (Step 1 above) and update the React dashboard to consume it, proving the end-to-end path before tackling the other consumers.

### Subtasks for Current Step:
- [ ] Extend `ProjectViewSet.get_queryset` (or add a serializer/query param) to select only the highest `version` per `project_group_id`.
- [ ] Expose/consume that variant inside `projectService.getProjects()` and `useProjects`.
- [ ] Recompute dashboard stats from the deduplicated array; add a regression test or storybook fixtures to prove duplicates are gone.

### What the Coder MUST NOT Do:
- MUST NOT hack around in the UI with “skip duplicates if project_name matches” – the grouping must key off `project_group_id`/`version`.
- MUST NOT remove visibility into historical versions entirely; the latest-only list should be complemented by an explicit history view (already available via the project detail sidebar).

### Validation Criteria:
- Hitting `/api/projects/?latest=true` (or equivalent) returns at most one entry per `project_group_id`.
- The React dashboard metrics and project listings no longer show multiple rows for the same project after approving a new version.
- Manual/automated checks confirm that older versions remain accessible through version history but don’t pollute default listings.

### Why This Step Matters:
Now that lifecycle data is accurate, failing to align the presentation layer would keep user trust low—they would still see conflicting information even though the backend guarantees correctness.

## Previous Cycle Validation
- ✅ Approval now retires the prior version: see `_retire_previous_version` in `apps/projects/services.py:186-214`.
- ✅ Regression tests guard both the version-cloning behavior and the approval-time obsoletion (`apps/projects/tests.py:74-193`).
- ✅ Consumer inventory complete (see “Inventory Results” above).

## Future Work (After Current Priority)
1. Implement UX cues (“Superseded by…”) once the audit identifies which views should show them.
2. Evaluate whether API endpoints need dedicated filters (e.g., `?latest=true`) to simplify client consumption.

## Overall Roadmap to Quality
- Where we are: Backend lifecycle transitions are accurate; presentation layers still need to catch up.
- Where we want to be: Every workflow stage—from backend services to dashboards—communicates a single source of truth for the latest release while offering clear access to historical versions.
- Path: Audit & align the UI/reports (current priority), then enhance UX affordances for navigating between superseded and current versions.
