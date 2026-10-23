# Evidence guide

All screenshots and executed test records were produced during this assignment session on 23 October 2026 (Asia/Almaty). V1 screenshots were captured from the preserved original source before application edits. They are not claimed to be screenshots taken at the moment Bolt first generated v1.

- `original-v1/prototype-v1-source.zip`: exact original 28-file Git archive of commit `687c5f7bbcb29590ad3030cf5e596431be5971b7`; the same source is extracted beside it. The tag `prototype-v1` was pushed to the original repository.
- `original-v1/booking-v1.py`: first Python generation, saved before tests; no defects were found, so final Python is identical.
- `ai-exchanges/01-*`: genuine original Bolt prompt and complete rendered final response, recovered from the open project. `01-bolt-observed-chat.txt` also retains opening messages and tool-status labels. Original AI assertions are historical evidence, not test certification.
- `ai-exchanges/02-*` through `06-*`: real delegated Codex prompt-response exchanges from this session. These are clearly identified as sub-agent interactions, not invented human conversations.
- `ai-exchanges/personal-plan-review.json`: actual plan review question and exact user answer.
- `screenshots/`: native browser captures. Detail images are genuine native screenshot clips. Original full images remain available.
- `test-results/`: raw stdout/stderr/TAP, browser observations, exit statuses, audit history and independent verification. Empty stdout files are retained where tools write results to stderr.
- `assignment-pdf-extracted.txt`: all 30 source pages. The original PDF path and SHA-256 are in `assignment-source.json`; all pages were read and visually inspected.

Python v1 and web v1 refer to different artifacts: Python v1 was generated in this session; web v1 is the initial Bolt repository commit. The frontend validator already passed the supplied functional cases in v1. The real fixes address booking-management scope, stale results and the Start-hour picker.
