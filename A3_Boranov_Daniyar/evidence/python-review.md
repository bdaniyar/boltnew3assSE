# Python conditional review and executed results

Codex sub-agent review, 2026-10-23 (Asia/Almaty). This records an AI review, not personal student approval.

## Actual execution

Python 3.11.9 ran the same `test_booking` suite through `evidence/run-python-suite.py` twice: once with the preserved original `booking-v1.py`, then with final `booking.py` loaded as the `booking` module. Each run executed **47 unittest test methods**, including parameterized subtests. Each reported **0 failures, 0 errors, 0 skipped**, and **exit status 0**. Raw unittest detail is in the `.stderr.txt` files because `unittest.TextTestRunner` uses stderr by default; the `.stdout.txt` files contain the measured count summary. JSON records preserve the commands, Python version, timestamps, hashes and exit status.

No Python defect was found in these executed cases. No fix was made and no defect was introduced. The first generated implementation is identical to the final implementation (SHA-256 `3ab2168a0228edf8742789ce320304e902024e70d301db82d15291e8410c60c7`). The identical test suite SHA-256 for both runs is `413073eca71d57194b32c1b7bcf6af132747ea54bf95514bb3c0fd5bb10d70b1`.

## Every conditional branch

| Branch | Acceptance criterion and reason | Executed boundary evidence |
| --- | --- | --- |
| `type(start) is not int or type(end) is not int` → False | AC1: candidates must be integer minutes. Exact type checks exclude Boolean values as well as float, string, None and collection values, before arithmetic or comparison. | Invalid start and invalid end tested separately; True and False tested in each position; integer subclasses rejected explicitly. Ordinary ints continue. |
| `not 0 <= start < end <= 1440` → False | AC1: start cannot be negative; equal/reversed requests fail; end must be within the day. | Negative start/end, equal/reversed times, start/end beyond day and start=1440 fail. End=1440 and start=1 pass with suitable now and free intervals. |
| `start <= now` → False | AC1: strictly future start; equality must fail. | Base 540–570 at now=540 fails; start=539 fails; start=541 succeeds; midnight start at now=0 fails; 1439–1440 at now=1438 succeeds and at now=1439 fails. |
| `end - start > 120` → False | AC2: 120 minutes permitted; longer intervals fail. | Durations 1, 119 and 120 succeed when otherwise valid; 121 fails including a request ending at 1440. |
| `if blocked` → False | AC3: the room cannot be available when blocked. | 660–720 with blocked=True fails and with False succeeds; blocked=True also fails with an empty booking list. |
| `for booked_start, booked_end in existing` | AC4: visit each booking unless an overlap already establishes rejection. The empty collection performs zero iterations and may succeed. | Empty, one, several and unsorted booking collections tested; overlap only with the second or last entry fails. |
| `start < booked_end and end > booked_start` → False | AC4: two strict comparisons implement half-open overlap. If the request is after an interval, the first term is false; if before it, the second is false; equality at either endpoint permits touching. | Both touches pass; touching two surrounding intervals passes; one-minute overlaps at both ends, equal intervals, containment in both directions, and overlap with a later booking fail. |
| Final `return True` | AC5: reached only after every condition passes; the function returns a Boolean and never creates or confirms a booking. | Every helper check asserts `type(actual) is bool`; repeated successful checks do not add bookings. |

## Input preservation

Source review found no assignment to an argument, list item or interval, no mutating method, and no sorting. Loop unpacking creates local scalar names. The suite checks nested list contents and interval identities after a successful check and after each of the six rejection paths. It also checks the scalar argument values and original requests, tuple input, and repeated checks. These tests passed in v1 and final.

## Scope and limitations

`now`, `blocked` and the existing interval structure follow the stated input assumptions. This function does not attempt to repair malformed existing data. The automated cases support the specified rules, but do not establish correctness for every possible Python object. AC6 concerns the rendered frontend and is outside the Python function. Browser evidence is maintained separately.
