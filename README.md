# Smart Campus Room Availability Checker - Assignment 04

A responsive React application for four fictional university rooms. Filter by capacity and ALL selected equipment, select a matching room, then check its own bookings. No booking is created or changed. The fixed demo time is 09:00 (540 minutes).

## Project access

- Existing Bolt project: https://bolt.new/~/sb1-bskzikuu
- Verified live A4 demo: https://smart-campus-room-av-j4pb.bolt.host/
- Publication verified anonymously: all 22 UI checks passed; public JavaScript/CSS are byte-identical to the tested local build. Details: `A4_Boranov_Daniyar/evidence/deployment-verification.json`.

## Technologies and setup

React 18, TypeScript, Vite, Tailwind CSS, Node's test runner and Playwright Chromium. The preserved Python reference uses the standard library only. Verified with Node 22.22.0, npm 10.9.4 and Python 3.11.9. Vite requires Node 20.19+ or 22.12+.

Run commands from the repository root (or from the packaged `source/` directory):

```sh
npm ci
npm run dev
```

Open the local URL printed by Vite. For a production build without changing the tracked deployment output:

```sh
npm run build -- --outDir output/a4-final-build
npm run preview -- --outDir output/a4-final-build
```

## Automated checks

```sh
python3 -m unittest -v test_booking
npm test
npm run lint
npm run typecheck
npx playwright install chromium
npm run test:ui -- --project=chromium
```

The UI configuration starts the local application on `127.0.0.1:4173` automatically; leave that port free. Each run stores logs/JSON/failure traces in a new run directory under `A4_Boranov_Daniyar/evidence/implementation-testing`. To give a run a stable evidence label:

```sh
A4_UI_RUN=my-review npm run test:ui -- --project=chromium
```

To repeat the same UI tests anonymously against a published URL:

```sh
A4_BASE_URL=https://smart-campus-room-av-j4pb.bolt.host/ A4_UI_RUN=my-live-review npm run test:ui -- --project=chromium
```

Recorded final local results are Python 47/47, Node 76/76 (37 original + 39 new), and Chromium 22/22. Lint, type checking and production build passed. Exact commands, exit codes, initial failed keyboard-test attempt/correction, and final results are retained in the evidence folder; these counts are not a claim about future runs.

## Source structure

- `src/data/rooms.ts`: four deeply frozen room records, equipment labels and fixed time.
- `src/data/exampleCases.ts`: six preserved A-102 demonstrations.
- `src/types.ts`: room, equipment, booking and feedback types.
- `src/utils/availability.ts`: unchanged AC1-AC5 availability rules.
- `src/utils/filtering.ts`: positive attendee validation, capacity and ALL-equipment matching.
- `src/state/checker.ts`: selected room, input transitions, immediate feedback invalidation and room-specific checks.
- `src/components/`: filter/selector and existing presentation components.
- `scripts/frontend-test.mjs`, `scripts/fixtures/`: unchanged original 37 frontend tests.
- `scripts/catalog-test.mjs`, `scripts/helpers/`: 39 additional tests importing real production modules.
- `tests/room-selection.spec.ts`, `playwright.config.ts`: 22 real browser/UI tests.
- `booking.py`, `test_booking.py`: unchanged Python reference and 47 tests.

## Rules and room catalog

AC1-AC6 remain: integer times with `0 <= start < end <= 1440`, start strictly after 540, duration at most 120 minutes, blocked rooms rejected, overlap rejected but touching endpoints allowed, immutable bookings and clear responsive feedback.

F1-F5 add capacity >= attendees, ALL required equipment, clear blocked labels, an empty state, and result/selection invalidation when switching rooms or changing filters. A filtered-out room cannot be checked. A-102 alone has a demonstration blocked toggle; D-404's catalog block cannot be removed. Original examples select A-102 only when it matches the filters.

| Room | Capacity | Equipment | Blocked | Bookings |
|---|---:|---|---|---|
| A-102 | 4 | Whiteboard, Projector | No | 10:00-11:00 |
| B-201 | 8 | Whiteboard, Display | No | 11:00-12:00 |
| C-303 | 12 | Projector, Display, Video conference | No | 12:00-13:00 |
| D-404 | 20 | Whiteboard, Projector, Video conference | Yes | 14:00-15:00 |

## Initial and final versions

A4 baseline: `55cab2a186df4107ab7189f509c259006af28f3f`, annotated tag `a4-baseline-2026-11-05`. The original earlier A3 `prototype-v1` tag is also retained. The final code reference is recorded in `A4_Boranov_Daniyar/evidence/source-references.json` and the report. The final submission includes an active source snapshot and baseline recovery bundle.

```sh
git bundle verify A4_Boranov_Daniyar/evidence/a4-baseline.bundle
git clone A4_Boranov_Daniyar/evidence/a4-baseline.bundle ../a4-baseline-review
git -C ../a4-baseline-review switch --detach a4-baseline-2026-11-05
```

From the submission folder itself, use `evidence/a4-baseline.bundle` in place of the longer path. Recovery uses a separate checkout and does not overwrite current work. Historical `A3_Boranov_Daniyar/` files and Task 1 evidence are unchanged.

## Submission and limits

`A4_Boranov_Daniyar/` contains the editable report, PDF report, separate AI evidence PDF, diagrams and their source, executable test copies, logs/screenshots, preserved Task 1 analysis and source/recovery references. The final ZIP includes those files and the source needed to reproduce the application, without dependencies, credentials or cache directories.

The data and time are fictional. There is no authentication, database, backend, live API, payment or reservation feature. Chromium keyboard/mobile tests do not replace a full screen-reader or cross-browser audit. Current dependency advisories are recorded in `evidence/final-dependency-audit.json`; no unrelated dependency upgrades were made.
