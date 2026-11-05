# Independent final source and regression review

Reviewed source commit: `4b2631f8519cb62321314d8c4b77c0d909c056f7`. Date: 5 November 2026 (Asia/Almaty).

Result: **PASS for the inspected application, tests and preservation contract. No correctness or requirement defect requiring a source change was found.** This review does not certify documents or the public deployment, which are handled separately.

## Review inputs

- Complete 30-page Assignment 04 extraction (`assignment-04-complete-extracted.txt`).
- Exact approved implementation request (`ai-exchanges/02-user-approval-and-request-exact.txt`).
- Active production TypeScript/React source, Node catalog/state tests, original regression fixtures and Playwright UI specification/configuration.
- Recorded fresh execution results in `final-checks/summary.json` and `implementation-testing/test-summary.json`; these were inspected, not rerun by this reviewer.
- Task 1 and A3 hash manifests.

## Functional findings

- `src/data/rooms.ts` contains the four approved records A-102/B-201/C-303/D-404 with the approved capacities, equipment, blocked values and separate booking intervals. All nested catalog collections and booking records are frozen. Demo time stays 540.
- `src/utils/filtering.ts:8-17` implements capacity >= requested attendees AND every selected equipment item. Empty equipment adds no constraint; invalid attendee counts yield no matches and explanatory UI feedback.
- `src/state/checker.ts:34-50,78-86` derives selection only from matching rooms. The check receives that room's bookings/blocked flag, clears invalid selections, and never falls back to a filtered-out room.
- `updateInputs` clears old results synchronously for room/filter/time/demo changes. `RoomSelector` shows a clear empty state; `App` disables checking without selection. F4/F5 do not retain hidden-room checks or stale results.
- Catalog-blocked D-404 cannot be unblocked through UI/reducer. The A-102 demonstration override changes only effective status and cannot leak to another room. Its effective status agrees between matching catalog and selected details.
- Original availability and time modules are byte-identical to the baseline. Integer/range/future-time checks, 120-minute maximum, blocked rejection, half-open overlap and nonmutation remain unchanged. Original A-102 values and all six demonstration outcomes remain covered.
- Rendering uses the existing application style, labelled controls, one shared result live-region wrapper and responsive layout. Local UI coverage includes keyboard events and 320px no-overflow checking; this is not a full accessibility audit.
- Runtime room data, domain types, availability rules, filtering, selected-room state and presentation are separate production modules. No backend, database, authentication, external runtime API or booking creation was added.

## Executable coverage and actual logs

The inspected logs record Python 47/47, Node 76/76 (37 original +39 new), and local Chromium UI 22/22; lint, typecheck and redirected production build exit 0. The Node runner imports actual production modules. UI tests execute real controls and cover F1-F5, chosen-room booking isolation, original mandatory cases, 120/121, touching/current-time rejection, end-only 24:00, unchanged visible bookings and mobile layout. The earlier keyboard-test failure and its correction remain preserved rather than replaced with a false all-success history.

No additional execution counts are claimed by this review. Public Bolt verification remains a separate required final gate.

## Preservation verification performed independently

SHA-256 comparison checked **215 protected files**, including **184 A3 submission/evidence files**, all previously recorded Task 1 files and baseline logs, the recoverable bundle, the original Python source/tests, original Node harness/fixtures, and original availability/time rules. **Zero differences or missing protected files.**

`git diff` from the A4 baseline to the inspected commit is empty for the A3 directory and six protected rule/reference/test paths. The Task 1 analysis and evidence are preserved byte-for-byte. This review created only this new audit document.

## Remaining limits

Chromium is the only exercised browser engine. Fictional fixed-time data and no full screen-reader audit remain explicit limits.

At the time of this source review, public deployment, report rendering, final README/package inventory and final ZIP completeness were still pending separate checks. They have since been checked by the main workflow and recorded below; this does not extend the independent source review.

## Completion checks recorded after the source review

On 5 November 2026, the existing Bolt.new project was synchronized and the existing Bolt.host site was updated. Anonymous HTTP returned status 200; the published JavaScript and CSS matched the tested production build byte for byte; all 22 public Chromium UI checks passed. Evidence is in `deployment-verification.json`, `public-bolt-http-assets.json`, and `implementation-testing/ui-public-bolt-final/`.

The editable DOCX and both PDFs were regenerated. The report PDF's 10 pages and the AI evidence PDF's 17 pages were rendered and visually inspected. `tools/verify_documents.py` passed: both URLs are clickable in DOCX and PDF, the historical prompt/response texts remain present in full, all 10 images preserve their aspect ratios, the DOCX has 9 native tables and editable text, and the reflection contains 269 words. Final ZIP inventory and recovery checks are recorded in `final-checks/` after packaging.
