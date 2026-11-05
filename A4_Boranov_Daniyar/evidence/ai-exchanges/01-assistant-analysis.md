# Assignment 04 - Task 1: Codebase Analysis

Status: analysis complete; implementation requires user approval. Date: 5 November 2026 (Asia/Almaty).

## 1. Source of truth and scope

All 30 pages of the supplied `Lesson 08 - Software Engineering - Assignment 04.pdf` were read, including visual inspection of the rendered pages. Requirements below come from this PDF, not from the outdated publication notes in the repository README. The repository source was inspected at the baseline below. Lesson 07/08 materials listed on PDF page 23 were not supplied or read in this task; their listing is not evidence of using them.

The PDF requires evolution of the existing Smart Campus checker, preservation of AC1-AC6, four or more fictional rooms, F1-F5, refactoring, executable tests, evidence-based quality evaluation and a 200-300-word reflection (pages 9-19). The present authorization covers Task 1 only. No application, test, configuration, historical A3 evidence or deployment file has been edited. No new Bolt project, SKILL.md or Practice 08 debugging exercise is part of this work. No login, payments, live APIs, database or booking creation is proposed.

## 2. Recorded and recoverable baseline

- Repository: `bdaniyar/boltnew3assSE`.
- Actual local location: `/Users/daniarboranov/Documents/code_materials/se/boltassignmnet/boltnew3assSE` (the older Python directory no longer exists).
- `HEAD`, local `main`, `origin/main` and GitHub `main` checked in this session: **55cab2a186df4107ab7189f509c259006af28f3f**.
- Initial working tree: clean. No applicable AGENTS.md was found in the repository or its inspected ancestors.
- Annotated local tag: **a4-baseline-2026-11-05**. It resolves to the same commit.
- Recoverable bundle: [evidence/a4-baseline.bundle](evidence/a4-baseline.bundle), containing the main history and baseline tag. `git bundle verify` passed; full output is saved.
- [Baseline manifest](evidence/baseline.json) records the PDF hash, bundle hash and SHA-256 hashes of all 223 pre-existing tracked files. The original A3 `prototype-v1` tag is unchanged; it is an earlier baseline, not the A4 starting point.
- No remote refs were changed and no commit was added to main.

Recovery can be inspected in a separate checkout without overwriting current work:

```sh
git bundle verify A4_Boranov_Daniyar/evidence/a4-baseline.bundle
git clone A4_Boranov_Daniyar/evidence/a4-baseline.bundle ../a4-baseline-review
git -C ../a4-baseline-review switch --detach a4-baseline-2026-11-05
```

### Actual baseline checks

Existing dependencies were installed with `npm ci --ignore-scripts --no-audit --no-fund`, exit 0, using the existing lockfile. Node v22.22.0, npm 10.9.4 and Python 3.11.9 were used. This installed dependencies only; no dependency declarations or lockfile changed. No Playwright dependency was added.

| Actual command | Result |
|---|---|
| `python3 -m unittest -v test_booking` | 47 passed / 47, exit 0 |
| `npm test` | 37 passed / 37, no failures or skips, exit 0 |
| `npm run lint` | Exit 0 |
| `npm run typecheck` | Exit 0 |
| `npm run build -- --outDir output/a4-analysis/build-baseline` | Exit 0 |

Commands, local timestamps, stdout/stderr and totals are in [evidence/baseline-checks.json](evidence/baseline-checks.json) and adjacent logs. These are fresh Task 1 runs, not reused A3 results. No new A4 feature or UI test has been executed because that functionality is not implemented. Dependency audit results and historical public-demo checks were not rerun or relabelled as current results.

## 3. Concise repository map

Line references below refer to the recorded baseline.

| File/function | Responsibility and important reference |
|---|---|
| `src/main.tsx` | React application entry point |
| `src/App.tsx:21` - `App` | Single-room state and composition; `handleCheck` at 27; reset at 39; blocked/time/example handlers at 45-64 |
| `src/types.ts:1,8,14` | Readonly `Booking`, small `Room` interface, discriminated availability result |
| `src/data/sampleData.ts:3,9,13,25` | A-102, frozen booking 600-660, fixed now=540, six example cases |
| `src/utils/availability.ts:12` - `checkAvailability` | Pure time, duration, blocked and overlap rules |
| `src/utils/time.ts:3,10` | `minutesToHHMM`, `hhmmToMinutes`, day-end constant |
| `src/components/RoomCard.tsx:9` | Room information and demonstration blocked toggle |
| `src/components/TimeControls.tsx:16,73` | `TimePicker`, time inputs, Check and Reset |
| `src/components/BookingsSection.tsx:9` | Readonly booking list |
| `src/components/ResultPanel.tsx:8` | Initial, available and unavailable status feedback |
| `src/components/ExampleCases.tsx:9` | Buttons for the six original demonstrations |
| `src/components/Header.tsx`, `CurrentTimeBadge.tsx` | Existing presentation components |
| `scripts/frontend-test.mjs:17,29,39`; `scripts/fixtures/availability-cases.mjs:8` | Transpile actual rules and run 37 regression fixtures with immutability assertions |
| `booking.py:4` - `can_book`; `test_booking.py:13` - `CanBookTests` | Python reference and 47-test regression suite |
| `package.json:6`; `vite.config.ts`; `tsconfig.app.json`; `eslint.config.js` | Run/test/quality tooling |
| `A3_Boranov_Daniyar/` | Historical submission, source snapshot and evidence: preserve, do not refactor |
| `dist/` | Already tracked generated deployment snapshot: do not overwrite during analysis |

## 4. Maintainability risks supported by source

| Priority | Genuine risk | Source evidence and consequence |
|---|---|---|
| High | Global booking coupling | `App.handleCheck`, `src/App.tsx:27-35`, always checks `SAMPLE_BOOKINGS`; line 95 displays the same global list. `Room`, `types.ts:8-12`, has no capacity, equipment or bookings. A selector alone would check/display the wrong room data. |
| High | Repeated result invalidation | `App.tsx:42,47,52,57,64` clears results in five separate handlers. A new room/filter path can omit this and leave a previous result visible, violating F5. |
| High | No executable UI coverage | `frontend-test.mjs:17-29` loads only time/availability modules; lines 39-49 call only the rule function. Historical browser JSON does not form an executable UI suite and cannot catch new wiring errors. |
| Medium | Examples assume one room | `sampleData.ts:15-32`, `ExampleCases.tsx:19-28` and `App.handleApplyCase:60-64` combine A-102-specific expected booking outcomes with changing the current room's blocked flag. New rooms need explicit example scope. |
| Medium | Repeated status wrapper | `ResultPanel.tsx:11-16,27-32,49-54` repeats the same section label, status role and live-region attributes three times. A later accessibility change could update only one branch. |
| Medium | Verification can modify deployment artifacts | `git ls-files dist` lists generated assets, while README proposes ordinary `npm run build`. A verification build can dirty tracked deployment files. Use an ignored output path during analysis. |

These are maintainability and evolution risks, not claims that the current one-room checker is failing its acceptance tests.

## 5. AC1-AC6 implementation and preservation contract

| AC | Current implementation | What must remain unchanged |
|---|---|---|
| AC1: valid time | `availability.ts:19-44`; `TimeControls.tsx:12-14,97-111`; `booking.py:12-17` | Integer minutes, `0 <= start < end <= 1440`, start strictly after fixed now=540. Start picker 00-23; end may be 24:00 only. Retain validation ordering and understandable errors. |
| AC2: maximum duration | `availability.ts:46-53`; `booking.py:18-19` | Exactly 120 minutes allowed if otherwise valid; 121 rejected. |
| AC3: blocked room | `availability.ts:55-61`; `booking.py:20-21` | Selected room's effective blocked flag rejects availability even without a conflict. |
| AC4: overlap | `availability.ts:63-71`; `booking.py:22-24` | `start < booked.end && end > booked.start`; endpoints may touch. Use only selected room bookings. |
| AC5: immutable bookings | `types.ts:1-6`; `sampleData.ts:9-11`; `BookingsSection.tsx:5-6,19-20`; frozen-input assertions in `frontend-test.mjs:32-47` | Readonly/frozen arrays and booking records per room; checking, filtering and switching create or modify no bookings. |
| AC6: clear responsive feedback | `ResultPanel.tsx:8-64`; `App.tsx:71,80,85`; labelled inputs in `TimeControls.tsx:36-55` | Preserve visible status/reason, live region, labels and responsive layout; add clear no-match/no-selection feedback. UI switching must not retain another room's result. |

Retain the existing Python reference, all original regression fixtures and original A-102 time/booking values. Availability remains a pure function with the same input/result contract; orchestration supplies the chosen room's data. AC3/F3 share the same blocked guard rather than introducing a second independent availability implementation.

## 6. Proposed minimal feature extension - not implemented

Keep A-102 as the default. The following additional attributes and rooms are fictional proposals; A-102's ID, name and original booking remain unchanged.

| ID / name | Capacity | Equipment IDs | Blocked | Own bookings (minutes) |
|---|---:|---|---|---|
| A-102 / Study Room A-102 | 4 | whiteboard, projector | false | b1: 600-660 |
| B-201 / Team Room B-201 | 8 | whiteboard, display | false | b201-1: 660-720 |
| C-303 / Seminar Room C-303 | 12 | projector, display, video-conference | false | c303-1: 720-780 |
| D-404 / Project Room D-404 | 20 | whiteboard, projector, video-conference | true | d404-1: 840-900 |

Each record contains ID, name, capacity, equipment, blocked status and its own readonly bookings. Use stable equipment IDs rather than free text. Proposed default attendee requirement is 1 and equipment selection is empty; require a positive whole attendee count. This input policy is a review decision, not an extra requirement claimed from the PDF.

- **F1:** include a room only when `capacity >= attendees`.
- **F2:** require every selected equipment item; combine equipment and capacity with AND. Empty equipment selection adds no equipment constraint.
- **F3:** matching blocked rooms remain visible and clearly labelled, so their rejection can be demonstrated. A capacity/equipment match is not an availability promise; the existing blocked rule still rejects the check.
- **F4:** if no rooms match, show a clear message, clear selection/result and disable checking. Never fall back to a hidden room.
- **F5:** changing room clears the old result immediately; the next explicit check uses its blocked state and bookings. Filters also clear old results; if they remove the selection, require a new visible selection. Selection persists when it remains a valid match.

Keep the blocked toggle as a demonstration control with state scoped by room ID, without mutating catalog bookings. Keep the six original demonstrations explicitly scoped to A-102; if current filters exclude A-102, disable those examples with a short explanation rather than silently using a hidden room or clearing the user's requirements.

Examples for later verification: 660-720 is available in A-102 but conflicts in B-201; projector plus video-conference matches C-303/D-404, but D-404 remains blocked; 13 attendees plus display produces the empty state.

## 7. Proposed refactoring and design decisions

Keep the existing React/TypeScript/Vite/Tailwind stack and useful component paths. Proposed files, not files created in this task:

```text
src/types.ts                    Room adds capacity, equipment, readonly bookings
src/data/rooms.ts               Four fictional rooms + fixed demo time
src/data/exampleCases.ts        Original A-102 demonstrations
src/utils/availability.ts       Existing pure AC1-AC5 rules, same contract
src/utils/filtering.ts          Pure capacity + all-equipment filtering
src/utils/time.ts               Existing formatting helpers
src/components/RoomFilters.tsx  Attendees + equipment controls
src/components/RoomSelector.tsx Visible matching rooms + empty state
src/components/RoomCard.tsx     Existing details + capacity/equipment
src/components/ResultPanel.tsx  One shared accessible section, conditional content
src/components/*               Reuse remaining presentation
src/App.tsx                    Selected ID, filters, time and check orchestration
```

1. **Separate matching from availability.** Pure filtering has no time/status mutation and can be tested directly. The existing checker remains the only place enforcing availability; this preserves AC boundaries and avoids inconsistent blocked rules.
2. **Store selected ID and derive one selected record.** Check and booking display receive the same selected room. One input-update/invalidation path clears results for time, status, room and filter changes; this reduces repeated state logic and avoids an after-render stale-result window.
3. **Share the status wrapper.** Consolidate the three repeated `section` wrappers without changing available/unavailable wording, styling distinctions or live-region behavior. This gives a concrete reduction in duplicated rendering logic required by Task 3.

Current and proposed diagrams are [before.mmd](diagrams/before.mmd) and [proposed-after.mmd](diagrams/proposed-after.mmd). The second is a design proposal, not proof of completed refactoring. Final diagrams and at least two design justifications must later be checked against the implemented diff.

## 8. Executable regression and integration/UI plan

Preserve all existing 47 Python and 37 frontend tests. After approval, extend the current Node transpile harness to load actual production room/filter modules and execute new catalog/filter tests through `npm test`; do not copy the filtering algorithm into tests. The current runner's two-module loading loop requires an explicit update. Add a Chromium UI spec and configuration; these do not exist yet.

| Planned cases | Traceability / expected outcome |
|---|---|
| Fixed-now equality rejected; future start accepted; equal/reversed/invalid/day-boundary inputs | AC1, retain existing executable cases |
| Exactly 120 accepted; 121 rejected | AC2, two separate existing cases |
| Chosen blocked matching room rejected without overlap | AC3/F3 |
| Touch either endpoint accepted; one-minute overlap rejected | AC4, retain distinct boundary cases |
| Frozen catalog and nested bookings identical after filtering/checks/repeated switches | AC5 |
| Attendees equal capacity included; capacity one below request excluded | F1, separate cases |
| All required equipment present included; partial match excluded; empty selection accepted | F2, separate cases |
| Capacity and equipment both required | F1/F2 combined |
| Same interval in A-102 vs B-201 gives different correct results | Chosen-room isolation / AC4 |
| No matches produces message, no selected room and disabled Check | F4, real UI check |
| Check A-102, switch B-201, old feedback disappears, check shows B-201 conflict | F5, integration/UI |
| Filtering removes a selected room; hidden room cannot be checked | F4/F5, integration/UI |
| Switching away/back does not leak blocked overrides or change bookings | AC3/AC5/F5 |
| Original six demonstrations and Reset retain their documented effects | AC1-AC6 UI regression |
| Labels, keyboard selection, status feedback, no horizontal overflow at 320/1440 px | AC6 UI checks; no claim of a full accessibility audit |

There are more than ten planned executable scenarios across the old/new requirements. Actual runner-reported totals, not table rows or assertions, will be used for the final count. At least one UI test must execute real selection/filter events against the rendered application.

Proposed commands after approval and creation of the named tests/configuration:

```sh
# One-time proposed UI-test dependency setup; NOT performed in Task 1:
npm install --save-dev @playwright/test
npx playwright install chromium

# Existing and extended checks:
python3 -m unittest -v test_booking
npm test
npm run lint
npm run typecheck
npm run build -- --outDir output/a4-analysis/build-final
npx playwright test tests/room-selection.spec.ts --project=chromium --reporter=line
```

Proposed `playwright.config.ts` defines only the Chromium project, local base URL `http://127.0.0.1:4173`, and `webServer.command = 'npm run dev -- --host 127.0.0.1 --port 4173 --strictPort'`. This makes the future UI command self-contained and prevents attaching to an unintended port. Preserve exact commands, versions, timestamps, stdout/stderr, exits, test totals and initial/final commits. Retry/failure evidence must not be discarded. No arbitrary fixed browser sleeps.

Playwright runner/install and web-server behavior were checked against the official documentation: https://playwright.dev/docs/intro and https://playwright.dev/docs/test-webserver. This is a small proposed dev dependency, not an existing project dependency or an assignment requirement.

## 9. Review decisions and AI suggestions

These are AI-assisted technical review decisions for the user's consideration. They are not a claim that the student independently reviewed or approved the implementation.

| Decision | Recommendation / reason |
|---|---|
| Adopt, pending approval | Extend the existing active source and preserve A3 snapshots; avoid a rewrite or new project. |
| Adopt, pending approval | Four local room records; pure all-item filtering; existing availability contract; derived selected room; explicit result invalidation. |
| Modify an actual AI recommendation | The AI testing reviewer included ordinary `npm run build` in the verification checklist. The analysis changed it to `npm run build -- --outDir output/a4-analysis/build-baseline` because `dist/` contains tracked deployment files. That command passed without overwriting the deployment snapshot. |
| Narrow the proposed test tooling | Use the reviewer's Playwright suggestion only for a small Chromium UI suite while retaining the Node regression runner. Add no generated project scaffold or unrelated CI configuration. Dependency installation waits for approval. |
| Reject if suggested | Inclusive overlap comparisons (`<=`/`>=`) would reject touching endpoints and break AC4. |
| Reject if suggested | Equipment ANY/OR matching would break F2's ALL rule. Filtering is capacity AND equipment. |
| Reject if suggested | A selector that leaves `SAMPLE_BOOKINGS` in either check/display path would violate room isolation. |
| Reject if suggested | Live clock, backend, login, database or booking creation exceed scope; live time makes the fixed-time fixtures unstable and booking mutation breaks AC5. |
| Reject if suggested | Counting historical screenshots as newly executed UI tests or claiming student verification from an AI audit would misrepresent evidence. |

Possible bad suggestions are identified as hypothetical; they are not invented historical AI outputs. User approval and personal verification remain unrecorded until actually provided.

## 10. Prioritized plan and approval gates

| Priority | Work | Review/verification gate |
|---|---|---|
| P0 - done | Record clean main, tag/bundle/hashes, inspect all requirements and rerun original suites | Verified bundle; 47/47 Python, 37/37 frontend, quality checks pass; tracked files unchanged |
| P1 - after approval | Introduce readonly room catalog/types and focused catalog/filter tests; preserve original fixture | Diff review: all required fields, A-102 unchanged, no booking mutation |
| P2 - after approval | Add pure F1/F2 filtering and reuse unchanged availability checker; wire selected ID into check/display | New unit tests + original regression suites pass, selected-room isolation demonstrated |
| P3 - after approval | Add filter/selector UI, F4/F5 and one invalidation path; scope examples; share status wrapper | Real UI checks for switching/empty state, responsive feedback, no hidden room fallback |
| P4 - after approval | Execute final suites, review diff and produce final evidence/report | Actual totals, before/after diagrams, measured quality table, remaining limitation and truthful reflection |

After each small source change, run the affected tests and inspect its diff; run the full gate before finalizing. No implementation commit, UI test creation, new dependency or publication occurs before approval.

## 11. Complete Assignment 04 deliverable inventory

The following content is required by the supplied PDF. Suggested filenames are an organization proposal, not prescribed submission names.

| Deliverable | Required content / proposed files | PDF pages |
|---|---|---|
| Initial and final source OR Git references | Preserved A4 baseline SHA/tag/bundle; later final SHA and source diff. Active `src/`, package/config files and original Python reference; keep A3 originals. | 20,26 |
| Runnable project README | Setup prerequisites, install, dev, build, regression and UI commands; correct current prototype information. Update root `README.md` later; do not overwrite historical A3 README. | 26 |
| Feature/refactoring source | Proposed `types.ts`, `data/rooms.ts`, `data/exampleCases.ts`, `utils/filtering.ts`, updated App/components; unchanged availability/time and Python unless a verified necessity is reviewed. Package/lock/config changes only for agreed test wiring. | 11-16 |
| Executable tests and real results | Retained `test_booking.py`, `scripts/frontend-test.mjs`, fixtures; new room/filter tests in the executable Node suite; `tests/room-selection.spec.ts`, `playwright.config.ts`; exact logs and result summaries. | 17,26-27 |
| Brief analysis/refactoring report | Repository map, >=3 sourced risks, prioritized plan, one real rejected/modified AI recommendation; implementation explanation; >=2 design decisions; traceability; limitations. This Task 1 document is its analysis starting point. | 14,16,18,26 |
| Before/after diagrams | Module or component diagrams with readable versions and source. Current before and proposed-after Mermaid files exist; final after diagram remains future work. | 16,26 |
| Quality comparison table | Baseline/final passed/total tests; repeated logic locations removed; modules/components and responsibilities; >=1 remaining limitation; explain each measurement. Final values must come from logs/diff, not estimates. | 18 |
| 200-300-word reflection | Context supplied, useful/incorrect AI suggestions, actual personal verification, tests' influence, next improvement. Write later using real completed actions; the A3 151-word reflection is not sufficient for A4. | 19 |
| AI-use record and evidence appendix | Tool/model where known, date, prompt summary, outputs used, problems, changes, decisions, verification sources and real human review. Keep exact Task 1 user prompt and full response per the user's stronger request. Preserve later exchanges; do not rewrite A3 AI_Evidence.pdf. | 25-27 |
| Feature demonstrations | Successful/unsuccessful capacity/equipment filters, switching, selected-room availability and responsive feedback. Screenshots/UI traces are useful supporting evidence, not a separately prescribed PDF/file type. | 15,27 |

Measured baseline quality: Python 47/47; Node 37/37; three repeated status-wrapper locations in ResultPanel and five handler result-clear locations in App, found by source inspection. Removed locations = 0 at Task 1 because no refactoring has happened. Later measure removal from the actual diff and record new shared locations; do not count preserved A3 copies as removable duplication. Existing seven presentation components and their responsibilities are mapped above. The current executable UI gap is a remaining limitation; fictional fixed-time data and lack of full accessibility auditing also remain limits.

The PDF deadline is 8 November 2026 at 23:59:59 (page 28); it does not state a timezone. Page 29 warns about formatting, but gives no specific filename, archive structure, required PDF/DOCX type or style. Do not carry A3 formatting rules over as invented A4 requirements. Other course/LMS instructions may need checking before final submission.

## 12. Evidence retained now

- `evidence/baseline.json`, verified `a4-baseline.bundle` and bundle verification output.
- Complete 30-page assignment extraction; PDF hash and full-page visual read confirmed.
- Fresh baseline install/check logs and structured results; tracked-file preservation check.
- `diagrams/before.mmd` and `diagrams/proposed-after.mmd` (proposal only).
- `evidence/ai-exchanges/01-user-prompt.txt`, `01-assistant-response.md`, full analysis and AI-use metadata.
- A3 evidence and report files remain historical, unchanged documents.

**STOP: awaiting the user's approval of this plan. Tasks 2-6 are planned, not performed.**
