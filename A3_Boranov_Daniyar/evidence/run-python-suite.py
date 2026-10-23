"""Run the identical unittest suite against the selected saved implementation."""

import argparse
import importlib.util
from pathlib import Path
import sys
import unittest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("implementation", type=Path)
    arguments = parser.parse_args()
    repository = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository))
    spec = importlib.util.spec_from_file_location("booking", arguments.implementation.resolve())
    module = importlib.util.module_from_spec(spec)
    sys.modules["booking"] = module
    spec.loader.exec_module(module)
    suite = unittest.defaultTestLoader.loadTestsFromName("test_booking")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Tests run: {result.testsRun}; failures: {len(result.failures)}; "
          f"errors: {len(result.errors)}; skipped: {len(result.skipped)}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
