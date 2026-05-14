# Technical Roadmap

## Release Positioning

`v1.0.0` was the public-story stabilization milestone for `thesis-skills`.

`v3.3.0` is the current documented public release line: the stabilized `v1.0` workflow story plus the shipped Citation Integrity additions from `v1.1.0`, `v1.2.0`, the V2.0 external metadata verification layer, the V3.0 hallucination risk scoring layer, the V3.1 claim-citation support triage layer, and the V3.3 reference verification hardening layer.

```text
bibliography intake
-> Word-to-LaTeX migration
-> deterministic checking
-> report-driven fixing
-> review-first LaTeX-to-Word export
-> bounded review loop
-> compile-log diagnostics
-> readiness gate
-> defense-prep artifacts
-> reusable rule-pack creation and linting
```

`v1.0.0` did not mean a broad new feature expansion. It marked the point where the public contract became stable: README, roadmap, docs, site pages, manifests, examples, and actual code paths described the same capabilities with the same names and limits.

`v1.1.0` and `v1.2.0` build on that stabilized contract by extending the References workflow with local-first Citation Integrity reports, review-friendly Markdown/CSV outputs, and clean/broken demos. `v2.0.0` adds report-first CrossRef / OpenAlex / Semantic Scholar metadata verification as an advisory evidence layer.

## Product Direction

`thesis-skills` is not a general writing assistant and not a thesis template.

It is a deterministic, inspectable, report-driven workflow system for academic writing projects that need:

- bibliography intake from Zotero and EndNote
- Word-to-LaTeX migration
- bounded LaTeX-to-Word export for review-oriented workflows
- bounded review-loop workflows for revision rounds
- bounded compile-log parsing
- bounded pre-submission readiness gating
- bounded defense-prep artifact generation
- repeatable deterministic checks
- bounded report-driven fixes
- reusable rule packs for schools and journals
- starter-pack linting, baseline completeness checks, schema-consistency checks, and scorecard output

Design rules that stay in effect:

- keep workflows explicit
- keep outputs inspectable
- keep fixers bounded and reversible
- keep policy in rule packs, not hard-coded into runners
- avoid overstating unsupported capabilities
- prefer workflow contracts over magical behavior

## Current Workflow Status

All listed workflow families remain part of the current `v3.3.0` public contract:

| Workflow | Status | Entrypoint |
|---|---|---|
| Zotero bibliography sync | Stable | `00-bib-zotero/sync_from_word.py` |
| Zotero bibliography quality check | Stable | `00-bib-zotero/check_bib_quality.py` |
| EndNote import-first intake | Stable | `00-bib-endnote/import_library.py` |
| EndNote preflight check | Stable | `00-bib-endnote/check_endnote_export.py` |
| Word-to-LaTeX migration | Stable | `01-word-to-latex/migrate_project.py` |
| LaTeX-to-Word export (review-friendly) | Stable | `02-latex-to-word/migrate_project.py` |
| Review package and triage | Stable | `03-latex-review-diff/review_diff.py` |
| Feedback normalization | Stable | `04-word-review-ingest/feedback_ingest.py` |
| Reference checking | Stable | `10-check-references/check_references.py` |
| Final reference set | Stable advisory | `17-final-reference-set/build_final_reference_set.py` |
| External reference verification | Stable advisory | `18-verify-references/verify_external_references.py` |
| Hallucination risk scoring | Stable | `19-check-hallucination-risk/check_hallucination_risk.py` |
| Claim-citation support triage | Stable | `20-check-claim-citation/check_claim_citation.py` |
| Baseline language lint | Stable | `11-check-language/check_language.py` |
| Format checking | Stable | `12-check-format/check_format.py` |
| Content checking | Stable | `13-check-content/check_content.py` |
| Deep language review | Stable | `14-check-language-deep/check_language_deep.py` |
| Compile-log diagnostics | Stable | `15-check-compile/check_compile.py` |
| Pre-submission readiness gate | Stable | `16-check-readiness/check_readiness.py` |
| Defense outline | Stable | `17-defense-pack/generate_outline.py` |
| Defense chapter highlights | Stable | `17-defense-pack/generate_chapter_highlights.py` |
| Defense figure inventory | Stable | `17-defense-pack/generate_figure_inventory.py` |
| Defense candidate tables/diagrams | Stable | `17-defense-pack/generate_candidate_tables_diagrams.py` |
| Defense talk-prep notes | Stable | `17-defense-pack/generate_talk_prep_notes.py` |
| Reference fixing | Stable | `20-fix-references/fix_references.py` |
| Safe language fixing | Stable | `21-fix-language-style/fix_language_style.py` |
| Format fixing | Stable | `22-fix-format-structure/fix_format_structure.py` |
| Deep patch preview | Stable | `24-fix-language-deep/fix_language_deep.py` |
| Rule-pack creation | Stable | `90-rules/create_pack.py` |
| Draft rule-pack creation | Stable | `90-rules/create_draft_pack.py` |
| Rule-pack lint / scorecard | Stable | `90-rules/lint_pack.py` |

### Current Boundaries

| Capability | Current boundary |
|---|---|
| Submission-friendly Word export | `review-friendly` is the first-class implemented export profile; submission-friendly export remains a stricter future path |
| GUI or web editor | Repository is CLI-first |
| Natural-language advisor intent | Feedback ingest normalizes bounded inputs; it does not automatically understand all advisor intent |
| Full compile orchestration | Compile support parses existing logs; it does not replace `latexmk`, `xelatex`, or `bibtex` |
| Final reference set | Requires `.aux` / `.bbl` from a successful compile; otherwise falls back to TeX source citation parsing |
| External metadata verification | CrossRef / OpenAlex / Semantic Scholar evidence is advisory; unavailable networks degrade to `UNAVAILABLE` and do not rewrite local readiness blockers |
| URL verification | HEAD / GET only; checks reachability, not authenticity or full-text content |
| DOI candidates | Suggestions only; never auto-write to `.bib` |
| Pack publishing ecosystem | Rule packs have local/Git/handoff workflows; there is no formal registry or versioned export bundle yet |
| AI writing | The repository checks, organizes, and fixes bounded issues; it does not generate or rewrite thesis content |

## Release History (Compact)

| Release | Theme |
|---|---|
| v0.3.0 | Public repository restructure, bilingual README, CI, Zotero as primary bib path |
| v0.4.0 | EndNote XML/RIS/BibTeX import, DOI deduplication, `refNNN` stability |
| v0.5.0 | Deterministic language lint layer |
| v0.5.1 | Deep language review: sentence-aware, cross-file screening |
| v0.5.2 | Deep patch preview: span-based selective fixes |
| v0.6.0 | Review-friendly LaTeX-to-Word export, compile-log parsing, review-loop workflows |
| v0.7.0 | Pre-submission readiness gate (`PASS / WARN / BLOCK`), advisor-handoff and submission-prep modes |
| v0.7.1 | Review-summary hardening and richer review digest artifacts |
| v0.7.2 | Feedback-ingest and readiness-gate calibration |
| v0.8.0 | Bounded defense-prep artifacts and static showcase surfaces |
| v0.8.1 | Rule-pack ecosystem hardening: lint, completeness, schema consistency, scorecard, and concrete non-Tsinghua example pack |
| v1.0.0 | Stable public story across README, roadmap, site, manifest, rule-pack docs, and actual code paths |
| v1.1.0 | Local-first Citation Integrity engine and readiness integration |
| v1.2.0 | Citation Integrity Markdown/CSV reports, clean demo, and public-example expansion |
| v2.0.0 | CrossRef / OpenAlex / Semantic Scholar external verification, consensus candidates, and `external_verification` readiness advisory |
| v3.0.0 | Hallucination risk scoring, `hallucination-risk-report.json`, `high-risk-references.csv`, Chinese `UNSUPPORTED` handling, and three demo projects |
| v3.1.0 | Claim-citation support triage, `claim-citation-triage-report.json`, context extraction, deterministic triage scoring, and three demo projects |
| v3.2.0 | Readiness gate integration (hallucination risk + claim-citation dimensions), unified evidence pipeline runner `run_evidence_pipeline.py` |
| v3.3.0 | Final reference set, resumeable external verification, DOI candidates, URL verification, and evidence pipeline hardening |

## Current release-line focus

The current public alignment work should target `v3.3.0` consistency:

1. README, Chinese README, roadmap, examples, and site pages should present final reference set, hallucination risk scoring, claim-citation triage, and readiness gate integration as bounded deterministic workflows.
2. Citation Integrity, final reference set, external verification, hallucination risk, claim-citation triage, and readiness gate outputs must be described consistently across docs and examples:
   - `reports/check_references-report.json`
   - `reports/citation-integrity-report.json`
   - `reports/citation-integrity-report.md`
   - `reports/citation-issues.csv`
   - `reports/final-reference-set-report.json`
   - `reports/final-reference-set-report.csv`
   - `reports/external-verification-report.json`
   - `reports/hallucination-risk-report.json`
   - `reports/high-risk-references.csv`
   - `reports/missing-doi-candidates.json`
   - `reports/missing-doi-candidates.csv`
   - `reports/url-verification-report.json`
   - `reports/url-verification-flagged.csv`
   - `reports/claim-citation-triage-report.json`
   - `reports/claim-citation-triage.md`
   - `reports/claim-citation-triage.csv`
3. Public docs should distinguish local deterministic References blockers from final reference set evidence, external metadata evidence, hallucination risk scores, and claim-citation triage signals.
4. V4.0 should build on this evidence layer, not LLM-based citation rewriting.

## V1.0 Stabilization Scope

### Primary goal

Ship a stable public narrative covering intake, migration, export, review, compile diagnostics, readiness, defense prep, and extension contracts.

### Acceptance

`v1.0.0` was complete when:

1. README, roadmap, docs, landing page, manifest, and actual code paths all match.
2. The repository does not claim support that does not exist.
3. Output artifacts are inspectable and reproducible across main workflows.
4. English and Chinese public docs have parity on version, workflows, commands, limits, and links.
5. The site tells the same bounded story as the GitHub README.
6. Rule-pack docs describe the current lint/completeness/schema/scorecard behavior in present tense.

### Historical stabilization checklist

- [x] Align root `README.md` with the v1.0 public contract.
- [x] Align `README.zh-CN.md` with the same contract in native Chinese wording.
- [x] Align `skills-manifest.json` and package metadata with the v1.0 version.
- [x] Align `site/` pages and static copy sources with the v1.0 scope.
- [x] Align `90-rules/` docs with current lint and scorecard behavior.
- [x] Sweep public examples for stale CLI flags such as `--rules` instead of `--ruleset`.
- [x] Keep historical planning docs as history unless they are linked as current guidance.

## Showcase And Scenario Track

The repository has a scenario-first static site under `site/`:

| Surface | Status |
|---|---|
| Static landing page | Existing in `site/index.html` |
| Artifact demo gallery | Existing in `site/artifact-gallery.html` |
| Docs homepage | Existing in `site/docs-home.html` |
| Scenario hub | Existing in `site/scenario-entry.html` |
| Advisor handoff scenario | Existing in `site/advisor-handoff.html` |
| Submission prep scenario | Existing in `site/submission-prep.html` |
| Legacy copy source | Existing in `site/copy-source.md`; should be treated as editable source text, not as a separate release baseline |

Showcase work must follow the same bounded philosophy as code: no marketing copy that claims support the repo cannot prove.

## Priority Matrix

| Track | User Value | Strategic Value | Risk | Priority |
|---|---|---|---|---|
| Public-story consistency | High | High | Low-Medium | P0 |
| Bilingual README parity | High | High | Low | P0 |
| Site/README/roadmap alignment | High | High | Low | P0 |
| Rule-pack docs present-tense cleanup | Medium | High | Low | P1 |
| Link and command integrity sweep | Medium | High | Low | P1 |

## Suggested Execution Order

Given the current repository state, the next work should proceed in this order:

1. align roadmap and release positioning around `v1.2.0`
2. align English README as the primary public contract
3. align Chinese README with parity on workflows, commands, limitations, and Citation Integrity outputs
4. align `site/` pages with the same version and capability story
5. align `90-rules/` docs with current lint/completeness/schema/scorecard behavior
6. run grep/link/test verification before treating the cleanup as complete

## Cross-Release Acceptance Gates

Every release is only complete when:

1. docs, manifest, landing page, and actual code paths match
2. the repository does not claim support that does not exist
3. test fixtures cover the workflow boundary being described
4. output artifacts are inspectable and reproducible
5. README positioning still matches the actual repository philosophy
6. non-technical thesis users can understand the main value proposition without reading internal module names first

## Planning References

- `docs/plans/2026-04-27-post-sync-next-stage-plan.md` — internal handoff that identified `v1.0.0` as the coherence/stabilization gate
- `docs/plans/thesis-skills-roadmap-v2.md` — historical strategic roadmap after the public `v0.7.0` baseline
