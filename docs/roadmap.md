# Technical Roadmap

## Release Positioning

`v1.0.0` was the public-story stabilization milestone for `thesis-skills`.

`v3.4.0` is the current documented public release line: the stabilized `v1.0` workflow story plus the shipped Citation Integrity additions from `v1.1.0`, `v1.2.0`, the V2.0 external metadata verification layer, the V3.0 hallucination risk scoring layer, the V3.1 claim-citation support triage layer, the V3.3 reference verification hardening layer, and the V3.4 final-audit / report-UX layer.

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

All listed workflow families remain part of the current `v3.4.0` public contract:

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
| Final cleanup residue scanning | Stable advisory | `23-check-final-cleanup/check_final_cleanup.py` |
| Statistical expression consistency | Stable advisory | `25-check-statistical-consistency/check_statistical_consistency.py` |
| Manual anchor / contents jump check | Stable advisory | `26-check-manual-anchor/check_manual_anchor.py` |
| Final audit JSON aggregation | Stable advisory | `27-final-audit-report/build_final_audit_report.py` |
| Reference audit ledger | Stable advisory | `28-reference-audit-ledger/build_reference_audit_ledger.py` |
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
| v3.4.0 | Final-audit foundation checkers, final-audit/report HTML surfaces, reference-audit ledger, and conservative claim-citation support-risk signals |

## Post-v3.4 Product Roadmap

`v3.4.0` is the current product baseline, not a stepping stone that forces the next feature to become `v4.0.0` or `v5.0.0`.

Future work should be organized as product tracks. Reserve a new major version only when the public contract changes in a large way: a new user workflow, a new artifact family, a new distribution model, or a capability that materially changes user expectations. Smaller improvements should stay in the current release line or become minor/patch releases.

### Track A: Citation Evidence Line

The citation integrity line remains the highest-value product path. The shipped stack is:

- local Citation Integrity: `reports/check_references-report.json`, `reports/citation-integrity-report.json`, `reports/citation-integrity-report.md`, `reports/citation-issues.csv`
- final reference set: `reports/final-reference-set-report.json`, `reports/final-reference-set-report.csv`
- external metadata evidence: `reports/external-verification-report.json`, `external_verification` readiness advisory, CrossRef / OpenAlex / Semantic Scholar evidence
- DOI candidates: `reports/missing-doi-candidates.json`, `reports/missing-doi-candidates.csv`
- URL verification: `reports/url-verification-report.json`, `reports/url-verification-flagged.csv`
- V3.0 hallucination risk scoring: `reports/hallucination-risk-report.json`, `reports/high-risk-references.csv`
- Claim-citation support triage: `20-check-claim-citation/check_claim_citation.py`, `reports/claim-citation-triage-report.json`, `reports/claim-citation-triage.md`, `reports/claim-citation-triage.csv`
- unified orchestration: `run_evidence_pipeline.py`

The next citation work should make **claim-citation support review** easier to consume without claiming automatic truth judgment:

- improve claim-citation HTML / presentation so support signals, risk signals, citation-needed candidates, and clusters are easier to review
- continue calibrating claim extraction and citation-cluster grouping with fixtures from real thesis projects
- continue using bibliography metadata, hallucination risk labels, and optional abstract/keyword evidence as explicit signals
- keep likely topic mismatch, overclaim, outdated support, weak support, orphaned citation, and citation-needed cases conservative
- keep every finding conservative: "needs manual review", not "this is false"
- keep outputs report-first and human-confirmed; no automatic citation rewrite and no automatic bibliography insertion

This is a major-version candidate only if it introduces a materially new public workflow or output contract. Otherwise it should be treated as the next incremental citation-evidence improvement.

### Track B: Candidate Reference Support

Candidate reference support is a later product track, not the immediate next release promise.

The safe order is:

1. recommend from the user's existing BibTeX / Zotero library first
2. use seed papers and external scholarly databases second
3. deduplicate candidates against the current bibliography
4. explain why a candidate may support a claim
5. require explicit user confirmation before anything enters `.tex` or `.bib`

The repository must not generate fake references or treat LLM output as a source of bibliographic truth. If this track ships, its artifact should be candidate-oriented, for example `candidate-references.json`, not an automatic patch.

### Track C: Rule-Pack And Packaging Ecosystem

Rule packs are the distribution layer for schools, journals, and service workflows. The next improvements should make packs easier to trust and hand off:

- add more concrete school/journal packs only when their assumptions are documented
- improve pack lint coverage and completeness checks
- extend scorecard dimensions where the existing schema allows
- define a versioned export bundle for sharing rule packs outside a local checkout
- keep policy in rule packs, not hard-coded into checkers

### Track D: Final-Audit And Evidence Handoff

The next missing product layer is a **final-audit workflow** that turns the existing deterministic checks into a clearer pre-submission deliverable.

This track should absorb the highest-value parts of `thesis-skills-final-audit-rules.md` that fit the current product philosophy:

- final cleanup residue scanning (`TODO`, `FIXME`, `\textcolor{blue}`, `draft`, `debug`, `???`, and similar process traces)
- statistical expression consistency checks (`p值/P值`, `P=`, `95%CI`, `Bootstrap`, `SMD`, and related mixed notation)
- manual anchor / `\phantomsection` / `\addcontentsline` checks for table-of-contents, list-of-figures, and list-of-tables jump integrity
- reference audit consolidation across local citation integrity, final reference set, external verification, DOI candidates, URL verification, and hallucination risk
- final-audit readiness presentation that is easier for students, advisors, and service workflows to review

Initial foundation now available:

- final cleanup residue scanning: `23-check-final-cleanup/check_final_cleanup.py`, writing `reports/final-cleanup-report.json` as a deterministic report-only artifact
- statistical expression consistency: `25-check-statistical-consistency/check_statistical_consistency.py`, writing `reports/statistical-consistency-report.json` as a dominant-style/deviation artifact
- manual anchor / contents jump check: `26-check-manual-anchor/check_manual_anchor.py`, writing `reports/manual-anchor-report.json` for `\addcontentsline` / `\phantomsection` review
- final audit JSON aggregation: `27-final-audit-report/build_final_audit_report.py`, writing `reports/final-audit-report.json` by aggregating existing JSON evidence without rerunning checks or rewriting source files
- reference audit ledger: `28-reference-audit-ledger/build_reference_audit_ledger.py`, writing `reports/reference-audit-ledger.csv` from existing reference evidence without bibliography edits or external lookups

Recommended outputs for this track:

- `reports/final-audit-report.json`
- `reports/reference-audit-ledger.csv`
- `reports/final-audit-report.html`
- `reports/reference-audit-ledger.html`

This track should stay conservative:

- report-first, not auto-rewrite-first
- no large-scale wording changes
- no automatic conclusion-strength edits
- no automatic bibliography insertion or replacement

### Track E: Human-Readable Report Surfaces

The current machine-readable artifacts are strong, but the human-reading experience is still too rough. Future work should improve report UX without replacing the existing JSON / CSV source of truth.

Preferred direction:

- keep JSON / CSV as the machine-readable contract
- generate static HTML as the primary human-readable review surface
- make HTML work as a local artifact bundle, not a required web app or hosted service
- keep the visual system consistent with the repository's existing editorial/static-site language where it helps

The HTML layer should eventually support:

- report index / landing page for one project run
- severity-grouped issues (`P0` / `P1` / `P2` / `P3` or equivalent review groupings)
- issue cards with file, line, evidence, rationale, and suggested action
- cross-links between readiness, references, claim-citation review, and final-audit artifacts
- better mobile and desktop reading experience
- cleaner advisor / lab / service handoff screenshots and exports

This is a UX and packaging track, not a replacement for the CLI-first architecture.

Initial HTML surface now available:

- static report index: `29-report-index/build_report_index.py`, writing `reports/index.html` as a local landing page over JSON / CSV source artifacts
- final audit detail page: `30-final-audit-html/build_final_audit_html.py`, writing `reports/final-audit-report.html` from `final-audit-report.json` as a local reading surface
- reference ledger detail page: `31-reference-ledger-html/build_reference_audit_ledger_html.py`, writing `reports/reference-audit-ledger.html` from `reference-audit-ledger.csv` as a local reading surface
- claim-citation detail page: `32-claim-citation-html/build_claim_citation_html.py`, writing `reports/claim-citation-triage.html` from `claim-citation-triage-report.json` as a local reading surface

### Track F: Public Surface And Verification Discipline

Every roadmap item must keep the public surface aligned with shipped behavior:

- README, Chinese README, roadmap, examples, and site pages should describe the same workflows, artifact names, and boundaries
- public docs should distinguish local deterministic References blockers from final reference set evidence, external metadata evidence, hallucination risk scores, and claim-citation triage signals
- tests should cover the workflow boundary being described
- links, commands, and version strings should be checked before any release is considered complete

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
| Citation support review depth | High | High | Medium | P0 |
| Final-audit checker foundation | High | High | Low-Medium | P0 |
| Human-readable report UX | High | High | Medium | P0 |
| Public-surface / docs / examples consistency | High | High | Low | P0 |
| Rule-pack and packaging ecosystem | Medium | High | Low-Medium | P1 |
| Candidate reference support | High | Medium-High | High | P2 |

## Suggested Execution Order

Given the current repository state at `v3.4.0`, the next work should proceed in this order:

1. **Build claim-citation HTML**: add a static local `reports/claim-citation-triage.html` surface for support-review labels, risk signals, clusters, and citation-needed candidates.
2. **Polish cross-report navigation**: link claim-citation, readiness, final-audit, reference ledger, and raw JSON / CSV artifacts consistently.
3. **Calibrate support-risk heuristics**: add more fixtures for `possible_topic_mismatch`, `possible_outdated_support`, and `possible_overclaim` without turning them into truth claims.
4. **Harden rule-pack packaging**: improve pack lint, completeness, scorecard, and export-bundle workflows so packs can be shared safely.
5. **Evaluate candidate reference support later**: only start recommendation work after support-review presentation, final-audit, and handoff tracks are stable.
6. **Run cross-release verification**: grep, link, command, and test verification remain mandatory before treating any roadmap item as complete.

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
- `docs/plans/thesis-skills-citation-integrity-roadmap.md` — historical citation-integrity product path; future work should absorb its support-review and candidate-reference ideas without assigning major-version labels prematurely
