# Python plan recorded before implementation

Date: 2026-10-23 (Asia/Almaty). Author: Codex sub-agent exchange 02.
Sources read: all 30 pages of the assignment extraction and the exact user request.
This is an implementation plan, not a claim of personal student approval.

1. AC1: reject `start` and `end` unless they are Python integers, excluding Boolean values. Require `0 <= start < end <= 1440` and `start > now`. Check equal/reversed times, invalid types, negative times, day bounds, starts-now, and the last valid minute of the day.
2. AC2: reject a duration above 120 minutes; test 1, 120, and 121 minutes.
3. AC3: reject a blocked room even for otherwise valid times.
4. AC4: scan every existing interval and reject when `start < booked_end and end > booked_start`. Test both touching endpoints, containment, identical intervals, and an overlap after earlier nonoverlapping bookings.
5. AC5: return only a Boolean, read input data without changing it, and never create a booking. Verify list contents, nested list contents, identities, and scalar inputs after allowed and rejected checks.

Assumptions: `now` is valid in 0–1439, `blocked` is a Boolean flag, and each existing interval is a well-formed pair of integer minutes. These are input contract assumptions; malformed existing data is outside this assignment. The Python function has no UI; AC6 is verified separately on the existing frontend.

Preserve the first implementation byte-for-byte before testing. Run the same complete unittest suite through the same runner against v1 and final. Store actual stdout, stderr, count, exit code and hashes. If no defect is found, keep v1 and final identical and say so.
