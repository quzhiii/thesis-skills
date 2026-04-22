# Technical Roadmap

## Release Positioning

`v0.3.0` is the release where `thesis-skills` becomes a cleaner public repository instead of only an internal workflow snapshot.

This release keeps the stronger local engineering core while presenting a clearer external story:

- deterministic checks instead of prompt-only QA
- report-driven fixers instead of unconstrained rewriting
- reusable rule packs instead of one-off template hacks
- bibliography intake workflows with explicit support levels

## Product Direction

The repository follows five layers:

1. bibliography intake
2. Word-to-LaTeX migration
3. LaTeX-to-Word export
4. deterministic checking
5. report-driven fixing
6. ruleset onboarding and reuse

That means the project is not trying to be a general writing assistant. It is an infrastructure layer for academic writing workflows that need to be repeatable, inspectable, and extensible.

## Support Matrix

| Workflow | Status in v0.3.0 | Notes |
|---|---|---|
| Zotero BibTeX quality check | Stable | `00-bib-zotero/check_bib_quality.py` |
| Zotero Word citation sync | Stable | extract -> compare -> map -> `citation-lock.tex` |
| EndNote XML/RIS import | **Stable (v0.4)** | `00-bib-endnote/import_library.py` with dry-run/apply modes |
| EndNote BibTeX fallback | **Stable (v0.4)** | normalized import via same pipeline |
| EndNote preflight check | **Stable (v0.4)** | `00-bib-endnote/check_endnote_export.py` |
| EndNote direct sync | Planned (v0.5) | Word field-code extraction not implemented |
| Word -> LaTeX migration | Stable | explicit migration spec with structured metadata |
| LaTeX -> Word export | Stable (v0.6) | review-friendly export first, submission-friendly later |
| Compile log parsing | Stable (v0.6) | parse existing `.log` files into structured findings |
| Pre-submission gate | Stable (v0.7) | bounded `PASS/WARN/BLOCK` verdict from existing artifacts |
| Deterministic check -> fix loop | Stable | covered by regression tests |
| Rule pack generation | Stable | starter and draft-pack paths both exist |

## EndNote Support Status

**v0.4.0** delivers import-first EndNote support:

1. **XML import** - Recommended format, best field coverage
2. **RIS import** - Good alternative, standard interchange format
3. **BibTeX fallback** - Compatible but may have type pollution
4. **Preflight check** - Validate exports before import
5. **Deduplication** - DOI-based with low-confidence warnings
6. **Stable numbering** - `refNNN` persists across re-runs

The import path is:

```text
EndNote XML/RIS/BibTeX
  -> parse -> canonicalize -> dedupe
  -> allocate/ref reuse refNNN
  -> generate refs-import.bib
  -> update citation-mapping.json
  -> output JSON report
```

**Not yet implemented (planned for v0.5)**:
- EndNote Word field-code parser
- Traveling Library extraction
- Direct Word -> LaTeX sync

## Roadmap by Release

### v0.3.0

- publish the restructured repository
- ship bilingual README refresh
- expose the architecture as layered workflows
- keep Zotero sync as the strongest bibliography path
- position EndNote as an export-based intake workflow
- keep regression tests and CI in the public release

### v0.4.0

- ✅ EndNote XML/RIS/BibTeX import-first support
- ✅ Canonical reference model with DOI normalization
- ✅ Deduplication with DOI exact match and low-confidence warnings
- ✅ Stable `refNNN` allocation with mapping persistence
- ✅ Preflight checker for EndNote exports
- ✅ Comprehensive test suite (45 tests)
- ✅ User documentation (`00-bib-endnote/THESIS_BIB_ENDNOTE.md`)
- improve release docs for pack onboarding
- reduce pyright rough edges in runner typing
- improve example coverage for non-Tsinghua rulesets

### v0.5.0

#### Phase 0: baseline hardening

- align smoke workflows with the real runner fixture, flags, and ruleset ids
- isolate runner regressions from checked-in `reports/` artifacts
- make language-checker and fixer tests workspace-safe in sandboxed environments
- add a preflight acceptance gate before expanding language modules

#### Phase 1: basic language foundation

- expand `11-check-language` into a deterministic thesis-language lint layer
- expand `21-fix-language-style` into low-risk safe fixes only
- keep deep review and deep patching out of `v0.5.0`

### v0.5.1

- add `14-check-language-deep` as a report-only deep review layer
- support connector misuse, collocation misuse, terminology consistency, and acronym first-use
- extend finding payloads with span, evidence, suggestions, confidence, and review-required fields
- keep product positioning explicit: deep review is a thesis-screening assistant, not a final thesis sign-off layer

### v0.5.2

- add `24-fix-language-deep` for patch preview and selective apply
- validate `old_text`, reject overlapping patches, and skip review-required findings by default
- preserve the separation between safe fix and deep fix

### v1.0.0

- stable public architecture and packaging story
- clearer boundary between skills, runners, and optional Word-side tooling
- stronger test coverage for real-world bibliography and migration samples
- documented extension contract for third-party rule packs

### Planned next track after v0.5.2

- add `02-latex-to-word` as a review-first export workflow
- keep first-release export promises bounded and explicit
- introduce stricter submission-oriented export only after the review path is proven
- add `15-check-compile` as a bounded compile-log diagnostic translation layer
- add review-loop workflows for review diff, feedback ingest, and revision summaries

### v0.7.0

- ✅ add `16-check-readiness` as a bounded pre-submission gate
- ✅ reuse existing run, fix, check, compile, export, and review artifacts instead of re-running the whole toolchain
- ✅ emit explicit `PASS / WARN / BLOCK` verdicts with blockers, warnings, next actions, and source references
- ✅ keep advisor-handoff and submission-prep policy explicit and inspectable
- ✅ avoid overclaiming institutional compliance or replacing human judgement

## Repository Design Rules

- keep top-level folders user-comprehensible
- keep `core/` as the reusable implementation layer
- keep checkers deterministic
- keep fixers bounded and reversible
- keep policy in rule packs, not hard-coded into runners
- do not overstate EndNote support before direct sync exists

## Recommended Next Technical Work

1. complete the phased v0.5 language-quality program before expanding product surface area
2. harden typing in runner and checker entrypoints
3. add sample fixtures for malformed mapping files, noisy Word exports, and language edge cases
4. add more example packs beyond starter packs
5. define a formal bibliography intake contract shared by Zotero and EndNote paths
