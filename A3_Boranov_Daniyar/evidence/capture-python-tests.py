"""Capture real processes without mixing test output with explanatory text."""

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


repository = Path(__file__).resolve().parents[2]
evidence = Path(__file__).resolve().parent
results = evidence / "test-results"
results.mkdir(parents=True, exist_ok=True)
runner = evidence / "run-python-suite.py"
suite = repository / "test_booking.py"

for label, implementation in (
    ("python-v1", evidence / "original-v1" / "booking-v1.py"),
    ("python-final", repository / "booking.py"),
):
    command = [sys.executable, str(runner), str(implementation)]
    completed = subprocess.run(command, cwd=repository, text=True, capture_output=True)
    (results / f"{label}.stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (results / f"{label}.stderr.txt").write_text(completed.stderr, encoding="utf-8")
    counts = re.search(
        r"Tests run: (\d+); failures: (\d+); errors: (\d+); skipped: (\d+)",
        completed.stdout,
    )
    record = {
        "command": command,
        "working_directory": str(repository),
        "observed_at_Asia_Almaty": datetime.now(timezone(timedelta(hours=5))).isoformat(),
        "python_version": sys.version,
        "implementation": str(implementation.relative_to(repository)),
        "implementation_sha256": hashlib.sha256(implementation.read_bytes()).hexdigest(),
        "suite_sha256": hashlib.sha256(suite.read_bytes()).hexdigest(),
        "tests_run": int(counts[1]) if counts else None,
        "failures": int(counts[2]) if counts else None,
        "errors": int(counts[3]) if counts else None,
        "skipped": int(counts[4]) if counts else None,
        "exit_status": completed.returncode,
        "stdout_file": f"{label}.stdout.txt",
        "stderr_file": f"{label}.stderr.txt",
    }
    (results / f"{label}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))
    if completed.returncode:
        print(completed.stderr, file=sys.stderr)

