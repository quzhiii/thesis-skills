# THESIS_CHECK_COMPILE

This checker translates raw LaTeX compile logs into structured, friendlier findings.

Use it to:

- parse existing `.log` files into machine-readable findings
- surface build-blocking errors and softer warnings with clearer categories
- preserve raw compile evidence without pretending to replace the TeX toolchain

Boundaries:

- this is a diagnostic parser, not a full build framework
- it does not promise perfect coverage for every engine, class, or package
- it does not mutate thesis source files

Expected CLI shape:

```bash
python 15-check-compile/check_compile.py \
  --project-root <latex-project> \
  --ruleset tsinghua-thesis \
  --report reports/check_compile-report.json
```

Relationship to `--skip-compile`:

- `run_check_once.py --skip-compile` still skips compile diagnostics entirely
- without `--skip-compile`, the runner will try to discover a compile log and parse it if present
- if no log is available, the runner should return a clear structured compile status rather than crashing
