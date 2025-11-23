# Analyzed Workflows Sidebar

This document captures the requirements and implementation approach for exposing previously analyzed workflows inside the frontend UI.

## User Problem

Users can upload a workflow file and immediately view its analysis, but there is no way to revisit earlier analyses without digging into Firestore manually. They want fast access to any prior run, selectable directly within the app.

## Solution Overview

Add a persistent left-side panel that lists the most recent workflow analyses. The main area of the page continues to display the currently selected report.

- **Component**: `AnalyzedWorkflowsList`
- **Placement**: Left column in the main layout next to the existing upload/results content
- **Data Source**: `GET /workflows` (existing backend endpoint) for list, `GET /workflows/{id}` for detail
- **Behavior**:
  - Fetch the list on load and whenever a new analysis is saved
  - Clicking an item loads its report and highlights the selection
  - Most recent analyses appear first, showing ID, created timestamp, and approval status badge

## Implementation Notes

1. Add new component `AnalyzedWorkflowsList` with props `workflows`, `selectedWorkflowId`, `onSelect`, and `loading`.
2. Extend `App.js` state:
   - Track `workflows`, `selectedWorkflowId`, and a sidebar loading/error state
   - Fetch workflow list inside `useEffect` and after successful uploads
   - `handleWorkflowSelect` fetches `/workflows/{id}` and updates `analysisResult`
3. Layout changes:
   - Wrap content in `.app-shell` flex container (`sidebar` + `content`)
   - Adjust existing styles to accommodate sidebar width
4. Styling:
   - Create CSS for the sidebar, list items, selection state, scroll behavior, and badges

## Open Questions

- Should we eventually rename workflows to friendly titles (from `workflow_name`)? For now we only show IDs plus dates.
- Is pagination needed? Current API upper bound (100) should suffice for MVP.
