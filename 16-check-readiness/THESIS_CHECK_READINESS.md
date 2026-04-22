# Thesis Check Readiness

## Purpose

`16-check-readiness` is a bounded pre-submission gate for `thesis-skills`.

It summarizes existing structured workflow artifacts into a readiness verdict instead of re-running or replacing lower-level checkers, fixers, compile parsing, export, or review-loop workflows.

## Verdict Model

- `PASS`: no configured blocker remains for the selected gate mode
- `WARN`: the package is usable, but meaningful risk or manual-review debt remains
- `BLOCK`: the package should not proceed for the selected gate mode

## Gate Modes

- `advisor-handoff`
- `submission-prep`

Current first-release policy differences are intentionally small and explicit:

- `advisor-handoff` tolerates missing compile evidence as `WARN`
- `submission-prep` upgrades missing compile evidence to `BLOCK`
- `advisor-handoff` keeps unresolved review debt as `WARN`
- `submission-prep` upgrades unresolved review debt to `BLOCK`

These rules are meant to stay inspectable. The gate is not a scoring engine and does not hide why a stricter verdict was chosen.

## Relationship To Existing Reports

The gate is downstream of existing artifacts such as:

- checker reports
- `run-summary.json`
- `fix-summary.json`
- compile summaries/reports when present
- export summaries/reports when present
- review-loop artifacts when present

## First-Release Limits

This workflow does not claim universal institutional compliance, scholarly quality judgement, or full replacement of human review.

It is a bounded decision layer that explains blockers, warnings, and next actions using available evidence.
