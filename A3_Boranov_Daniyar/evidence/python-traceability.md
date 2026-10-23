# Python traceability (measured unittest results)

The values below were asserted by the actual 47-method suite for both implementations; complete execution records are in `test-results/python-v1.*` and `test-results/python-final.*`.

| AC ID | Implementation/file | Test input | Expected | V1 actual | Final actual |
| --- | --- | --- | --- | --- | --- |
| AC1 | `booking.py`, type/bounds/future checks | 540–570, now=540 | False | False (PASS) | False (PASS) |
| AC1 | `booking.py`, type check | start=660.0, end=720; and Boolean start/end | False | False (PASS) | False (PASS) |
| AC1 | `booking.py`, day bound | 1380–1441; 1439–1440 at now=1438 | False; True | False; True (PASS) | False; True (PASS) |
| AC1 | `booking.py`, ordering | 720–660; 720–720; -1–60 | False | False (PASS) | False (PASS) |
| AC2 | `booking.py`, duration check | 720–840; 720–841 | True; False | True; False (PASS) | True; False (PASS) |
| AC3 | `booking.py`, blocked check | 660–720 with blocked=True | False | False (PASS) | False (PASS) |
| AC4 | `booking.py`, half-open overlap | 660–720 against [(600,660)] | True | True (PASS) | True (PASS) |
| AC4 | `booking.py`, half-open overlap | 570–600 against [(600,660)] | True | True (PASS) | True (PASS) |
| AC4 | `booking.py`, half-open overlap | 630–690 against [(600,660)] | False | False (PASS) | False (PASS) |
| AC4 | `booking.py`, loop over every booking | 720–780 against [(600,660),(750,810)] | False | False (PASS) | False (PASS) |
| AC5 | `booking.py`, read-only checks | Success plus all six rejection paths with nested list inputs | Boolean; unchanged values and identities | PASS | PASS |
| AC6 | Frontend only | Browser feedback and mobile layout | Clear feedback and usable layout | See frontend evidence | See frontend evidence |
