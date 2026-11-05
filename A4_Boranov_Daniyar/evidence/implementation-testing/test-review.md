# A4 test implementation review

The original 37-case frontend runner and fixtures remain byte-identical to the A4 baseline. The npm test command now also executes a new catalog/state suite. The helper compiles the actual relative production import graph into a temporary directory and imports its exports; it does not copy availability or filtering algorithms. Final native Node run: 76/76.

The Chromium suite drives real form, checkbox, selection, button and keyboard events. Final full run: 22/22. The earlier 20/21 result, keyboard interaction correction and focused 1/1 rerun are retained, including the initial failure trace. The corrected native-select interaction uses type-ahead t to select Team Room B-201 on macOS Chromium. This was a test interaction correction, not a production defect repair.

Tests independently cover the known risks: room data isolation, ALL equipment matching, exclusion of an invalid selection, effective blocked state in both catalog and selected details, and no mutation of frozen catalog/bookings. UI checks additionally cover the original six examples, 120/121 minutes, end-only 24:00, empty state, keyboard events and narrow responsive layout.

Limits: one browser engine; no full screen-reader audit; local test success does not prove Bolt synchronization or a public deployment.
