# Compile Log Fixtures

These fixtures are trimmed LaTeX compile logs used to verify the bounded compile parser.

Covered cases include:

- undefined control sequence
- missing file or package
- missing citation and reference warnings
- bibliography backend ordering issues
- overfull box warnings
- engine/font mismatch hints
- encoding-related failures
- rerun stabilization warnings

They are intentionally partial: enough to exercise realistic parsing behavior without claiming universal TeX-engine coverage.
