# Software Engineering Assignment #03

**Boranov Daniyar** · **24B031718** · **Thursday 14:00–17:00** · **23 October 2026**

Smart Campus Room Availability Checker. This package continues the original Bolt.new React/TypeScript/Vite project. It checks one fictional room and never creates, confirms, changes or deletes bookings.

## Prototype access

- Bolt.new project/editor: [https://bolt.new/~/sb1-bskzikuu](https://bolt.new/~/sb1-bskzikuu)
- Public live demo: [https://bdaniyar.github.io/boltnew3assSE/](https://bdaniyar.github.io/boltnew3assSE/)
- GitHub repository: [https://github.com/bdaniyar/boltnew3assSE](https://github.com/bdaniyar/boltnew3assSE)

Public access and the latest version were verified. Mandatory published-page cases passed: 6. Checked: 2026-10-23T21:43:24.234769+05:00.

- GitHub main source e6e5da46857e19a2549a07fc38d362c7c66de8cf and the prototype-v1 tag were pushed and verified.
- The same production build is public on GitHub Pages. Anonymous requests returned HTTP 200 for HTML, JavaScript and CSS; each matched the local build byte for byte. The published browser passed all six mandatory cases and the 320 px layout check.
- Bolt showed a Synced badge, but its latest source could not be inspected after refresh. The startup error stated: WebContainer took longer than 1 minute to boot. Bolt synchronization and Bolt publication remain unverified.
- Remaining Bolt action: open the original project in a working Chromium session, load or sync the latest GitHub main source, confirm prototype v2 and no booking editing controls, then Publish and test the Bolt-hosted URL.
- The GitHub repository remains private. Complete source is included in this submission package.

The exact access record is `evidence/prototype-access.json`. GitHub source updates alone do not establish that Bolt has deployed the same version.

## Submission files

- `A3_Boranov_Daniyar_Report.pdf`: academic report, criteria, traceability, issues, evidence, agent analysis and reflection.
- `AI_Evidence.pdf`: exact genuine prompts and complete responses, actual approval record and review chain.
- `booking.py`, `test_booking.py`: Python implementation and 47 runnable unittest methods.
- `prototype/`: final existing React/Vite application source and frontend test harness.
- `evidence/original-v1/`: preserved source, ZIP archive, baseline metadata and the first Python implementation.
- `evidence/screenshots/`: genuine original/final browser captures and native detail captures.
- `evidence/test-results/`: actual stdout/stderr, TAP, JSON, quality checks, audit and browser records.
- `evidence/report-qa/`: final document render and layout-check metadata.

## Run Python checks

Use Python 3, standard library only, from this directory:

```sh
python3 -m unittest -v test_booking
```

The same full suite passed against v1 and final: **47/47**, exit 0, with no failures, errors or skips. Python v1 and final are byte-identical. `now` is valid in 0–1439; `blocked` is Boolean; existing intervals are well-formed integer-minute pairs. Start/end reject bool and other non-integer types.

## Run the prototype

Use Node.js and npm. From `prototype/`:

```sh
npm ci
npm run dev
```

Open the local URL printed by Vite. The fictional base fixture is room A-102, now 540 (09:00), blocked false and booking 600–660 (10:00–11:00).

```sh
npm test
npm run lint
npm run typecheck
npm run build
npm run preview
```

The frontend validator suite passed **37/37** for v1, after each focused repair and final. Lint, typecheck and production build exited 0. Browser tests passed the mandatory **6/6**, additional boundaries **10/10**, repair checks **8/8**, and all four layout widths **320, 375, 768, 1440 px** without horizontal overflow or outside controls. A separate review reran Python 47/47 and frontend 37/37.

## Recover original v1

The original commit is `687c5f7bbcb29590ad3030cf5e596431be5971b7`; tag `prototype-v1`. In a repository checkout, inspect without replacing current files:

```sh
git show prototype-v1:src/App.tsx
git worktree add ../prototype-v1-review prototype-v1
```

An archived copy is also in `evidence/original-v1/prototype-v1-source.zip`. Independent integrity review checked all 28 archive files against the tag with no mismatches. The current source commit is recorded in `evidence/prototype-access.json`; later documentation/package commits may follow it.

## Focused changes

1. Removed booking add/delete controls and state paths; frozen, readonly fictional data.
2. Cleared stale outcomes after either time or blocked-status changes; polite live status semantics.
3. Limited Start to 00–23; End supports 24:00 only with minute zero.
4. Removed unused Supabase and missing favicon reference; compatible transitive lockfile updates.

## Limitations and final checks

- Fixed fictional data and a supplied demo clock; no real campus data or booking service.
- Latest recorded dependency audit: 6 advisories (2 low, 3 moderate, 1 high, 0 critical). The remaining Tailwind/PostCSS chain proposes a Tailwind major migration; other residual advisories also need later review. A broad upgrade was not forced.
- Screen-reader and complete keyboard behavior were not executed; live-region attributes were checked.
- Publication and latest-version status are stated explicitly above. Follow the exact remaining action in the access notes if either is unverified.

All reported PASS results are supported by actual execution records. Original AI correctness statements are retained as historical evidence and are not substituted for the observed tests.
