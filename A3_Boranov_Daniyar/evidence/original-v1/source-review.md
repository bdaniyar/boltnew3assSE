# Original web prototype v1: source review

Review date: 23 October 2026. Reviewer: Codex sub-agent, delegated critique stage. The model identifier was not displayed in the delegated task. This is an AI source review, not a student's personal approval or an independent human review.

Baseline recorded in `baseline.json`: commit `687c5f7bbcb29590ad3030cf5e596431be5971b7`, tag `prototype-v1`, repository `https://github.com/bdaniyar/boltnew3assSE`.

## Evidence and limits

Before reviewing the implementation, I read all 30 pages of `evidence/assignment-pdf-extracted.txt` and the entire exact user request in `evidence/ai-exchanges/user-request-exact.txt`. I then inspected every original file under `src/components` and `src/utils`, plus `App.tsx`, `types.ts`, sample data, entry point, CSS, HTML, package metadata and build/typecheck/lint configuration.

This review uses code inspection. I did not run the original app, execute its functions, test its rendered controls, measure mobile overflow, or use a screen reader. Reproduction steps below are concrete procedures inferred from the source, to be confirmed by the parent agent's browser tests. Predicted outcomes must not be entered as executed PASS results. I changed no application file and introduced no defect.

## Framework and roles

- React 18 and TypeScript, built by Vite; Tailwind utility classes provide styling, and Lucide supplies icons.
- `src/main.tsx` mounts `App` in React StrictMode. `App.tsx` owns room, booking list, requested times and last result.
- `src/utils/availability.ts` exports the availability validator. `src/utils/time.ts` formats minutes, clamping displayed values into 0–1440.
- `src/data/sampleData.ts` contains the required fictional fixture: room A-102, now 540, booking 600–660, initially unblocked. It also defines the six required example cases.
- `TimeControls.tsx` uses hour/minute selects and invokes the parent's callbacks. `RoomCard.tsx` displays status and offers the blocked toggle. `CurrentTimeBadge.tsx` explains the fixed demo clock.
- `BookingsSection.tsx` renders existing intervals but also exposes add/remove actions. `ResultPanel.tsx` shows Available or Unavailable with an explanation. `ExampleCases.tsx` loads case times and blocked status. `Header.tsx` is presentation only.
- `package.json` provides dev/build/lint/typecheck/preview scripts, but no test script or testing dependency. An unused Supabase SDK dependency exists; I found no Supabase client or backend call in the inspected application source. Its presence alone does not establish use of a database.

## AC1–AC6 assessment by inspection

| AC | Source assessment | Evidence and practical limit |
| --- | --- | --- |
| AC1 | Validator is correct for candidate integers, day bounds, ordering and strictly-future start; time picker has a separate state/display defect. | `availability.ts:19–44` rejects nonintegers, lower/upper day violations, equal/reversed intervals, and start at/before now. `TimeControls.tsx:42,101` can create start 1470 when 24 is chosen with minute 30 retained. |
| AC2 | Correct in validator. | `duration > 120` rejects 121 and allows exactly 120. |
| AC3 | Correct when a fresh check is performed. | The `blocked` branch rejects every otherwise-valid request. Earlier branches may give a time-validation reason first, but still reject. Previously displayed results can remain stale after toggling status. |
| AC4 | Correct half-open interval condition; all bookings are considered. | The loop rejects `start < b.end && end > b.start`. Equality at either endpoint does not overlap. |
| AC5 | Validator itself is nonmutating; application violates availability-only scope. | The validator only reads inputs. App handlers add and remove booking records, and BookingsSection exposes both actions. Explicit Available/Unavailable labels exist, but stale results reduce their reliability. |
| AC6 | Specific validation messages, labels, focus rings and responsive grid classes are present. Usability has confirmed source defects and needs rendered verification. | Stale results and inconsistent end-of-day start state need repair. Narrow layout and no overflow cannot be established from CSS class inspection alone. ResultPanel has no live region; screen-reader announcement behavior was not tested. |

## Validator branch explanation

1. `!Number.isInteger(start) || !Number.isInteger(end)` returns Unavailable for fractional, NaN or infinite candidate times. This satisfies the integer part of AC1.
2. `start < 0 || end > 1440` enforces the outside limits. Together with `start < end`, it also excludes end below/equal zero and start at/above 1440; separate redundant checks are not necessary.
3. `start >= end` rejects equal or reversed intervals (AC1).
4. `start <= currentTime` rejects the past and starts-now, preserving the strictly-after rule (AC1). The contract assumes now is valid.
5. `end - start > 120` rejects only durations over 120; exactly 120 proceeds (AC2).
6. `blocked` returns Unavailable before any successful outcome (AC3).
7. For each existing interval, `start < b.end && end > b.start` rejects positive overlap and permits endpoint equality (AC4). Returning on the first overlap is sufficient; if none overlap the loop completes.
8. The final branch returns Available with formatted times and duration. Every path returns a result object and none assigns to an input, booking object or input array (AC5 at function level). AC5 must also hold at application level, where the booking controls fail it.

For the specified base fixture, inspection predicts the mandatory results True, False, False, True, False, False for touching, overlap, blocked, 120 minutes, 121 minutes, and starts-now respectively. These are predictions, not executed results from this review.

## F01 — Booking management contradicts availability-only scope

Priority: high. Affected rule: AC5 and the explicit scenario scope.

Source evidence: `App.tsx:23` stores editable bookings. `handleAddBooking` at lines 50–54 appends a new record. `handleRemoveBooking` at lines 57–58 filters a record out. `BookingsSection.tsx` exposes the corresponding add form and remove buttons. The text that these are only demo bookings does not satisfy the instruction that existing bookings must not be created, deleted or modified.

Reproduction to execute against v1:

1. Reload the original page and observe the single 10:00–11:00 booking.
2. In “Add a demo booking”, set Start to 11:00 and End to 12:00, then click Add. The source predicts a second visible booking.
3. Check the main 11:00–12:00 request. The source predicts Unavailable because the added record now overlaps it.
4. Reload, click “Remove booking 10:00 to 11:00”, then check 10:30–11:30. The source predicts Available because the original booking was deleted from page state.

Important distinction: these handlers replace the React state array; they do not mutate the exported original `SAMPLE_BOOKINGS` array in place. This is still prohibited booking management. A reload restoring the fixture does not resolve AC5.

Focused repair request: “Keep the required fictional existing booking list read-only. Remove add/delete controls and handlers, preserve the fixture, and retain only availability checking. Do not add a booking feature or change overlap logic.”

Suggested change: render `BookingsSection` from read-only bookings and remove its add/remove props, local form state, icons and handlers; remove `setBookings` and related handlers from App. Keep the existing visual list.

Retest: verify no create/remove controls exist; run the six mandatory scenarios and several-booking/endpoint tests; compare the fixture before and after checks. Status/time changes must not alter bookings.

## F02 — Last result remains after input or status changes

Priority: high for misleading blocked status; medium for other input changes. Affected rules: AC5's unambiguous result and AC6's understandable feedback. The fresh validator itself still implements AC1–AC4 correctly.

Source evidence: direct `setStart` and `setEnd` callbacks are passed at `App.tsx:91–92`; `handleToggleBlocked` at lines 46–48 only changes room state. These paths leave `result` intact. Only checking, resetting, or applying an example replaces/clears the result.

Reproduction to execute against v1:

1. Reload; leave 11:00–12:00 with room open and select Check Availability. The source predicts Available.
2. Select Mark as blocked. The room badge changes to Blocked while the earlier Available panel remains visible. Selecting Check again would then reject the request.
3. Alternatively, after the initial available result, change Start to 10:30 and End to 11:30 using the selects. The previous available result for 11:00–12:00 remains until another check.

The old message includes its checked times, which helps interpretation for time changes, but it has no checked blocked-status snapshot or stale-result notice. Keeping a positive result under a blocked badge is especially confusing.

Focused repair request: “Clear the displayed availability result whenever the requested start, requested end, or room blocked status changes. Keep explicit Check Availability behavior and the existing result messages. Preserve AC1–AC4.”

Suggested change: wrap the two input callbacks and blocked handler to also call `setResult(null)`. Existing reset/example behavior can remain. Automatic rechecking or a new workflow is unnecessary.

Retest: produce Available; change each input independently and toggle blocked; confirm the old outcome is cleared. Recheck overlap/blocked values and verify Unavailable. Check that reset and example loading still clear results.

## F03 — Start hour 24 can retain a nonzero minute

Priority: medium. Affected rule: AC6 and correct presentation of the AC1 domain. No evidence that this causes an invalid interval to be accepted.

Source evidence: `HOURS_24` includes 0–24 and is used for both pickers (`TimeControls.tsx:12,42`). `allowEndOfDay={false}` changes only helper text, not hour options. The Start hour handler at line 101 retains `sMinute`, while the End handler explicitly resets it to zero for hour 24. The minute select has only option zero and is disabled at hour 24. `minutesToHHMM` clamps out-of-range values before displaying them.

Reproduction to execute against v1:

1. Set Start to 11:30.
2. Change only Start hour to 24.
3. The source computes 24 * 60 + 30 = 1470. The helper formatter displays 24:00 beside “1470 min”, and the minute select has no matching option for its controlled value of 30. The exact native-select appearance needs browser confirmation.
4. Select Check Availability. The source predicts rejection; the validator prevents successful out-of-domain booking.

Focused repair request: “Offer start hours 00–23 only; allow 24:00 only for End, with minute zero. Remove the inconsistent start-24 state without changing the validator or adding controls.”

Suggested change: filter hour options using the existing `allowEndOfDay` flag. Retain End's minute-zero behavior and allow valid 23:00–24:00 checking.

Retest: Start has no 24 option; End 24 forces minute zero; 23:00–24:00 is Available with the base fixture; verify no time value or label exceeds 1440.

## Additional preventive observations and boundaries

- The unused Supabase dependency can be removed as dependency cleanup if desired, but must not be described as an observed database/API leak. No such behavior was found in the app code.
- Consider a polite status live region for the result. Missing `aria-live`/`role=status` is visible in code, but no screen-reader failure was executed or established in this review.
- Desktop/mobile screenshots, layout overflow measurements, actual UI outcomes, and complete final tests remain execution work. Responsive classes are encouraging evidence of intent, not proof of a usable narrow layout.
- Keep changes limited to the existing React/Vite app. Do not introduce login, backend, database, external API, payments, booking confirmation, a second room, or unrelated functionality. Preserve the original source evidence and use final-version files for repairs.

The minimum required cleanup is F01 and F02; F03 is a small related input correctness/usability repair. Preserve the correct validator and demonstrate each final outcome through actual test logs and screenshots.
