# Claim-Citation Support Review Plan

## Positioning

This is a post-`v3.3.0` product-track plan for deepening the existing claim-citation evidence layer.

It does **not** assign a new major version number. A future major version should only be used if this work becomes a materially new public workflow, output contract, or distribution model. Until then, this is an incremental improvement to the current citation evidence line.

The product goal is to move from basic structural triage toward a more useful **claim-citation support review** while keeping the existing thesis-skills philosophy:

- report-first
- deterministic where possible
- human-confirmed
- no automatic citation rewrite
- no automatic bibliography insertion
- no LLM as a final evidence source

## Current State

Implemented entrypoint:

- `20-check-claim-citation/check_claim_citation.py`

Core implementation:

- `core/citation_integrity/claim_citation.py`
- `core/citation_integrity/tex_parser.py`
- `core/citation_integrity/models.py`

Current outputs:

- `reports/claim-citation-triage-report.json`
- `reports/claim-citation-triage.md`
- `reports/claim-citation-triage.csv`

Current labels:

- `WELL_SUPPORTED`
- `SUPPORTED`
- `WEAK`
- `ORPHANED`
- `UNVERIFIABLE`

Current evidence signals:

- citation key exists in bibliography or not
- basic bibliography metadata completeness (`title`, `author`, `year`)
- hallucination risk label from `reports/hallucination-risk-report.json`
- citation frequency
- grouped citation size
- whether the local citation context is empty

Current demo coverage:

- `examples/claim-citation-mixed/`
- `examples/claim-citation-orphaned/`
- `examples/claim-citation-chinese/`

Current tests:

- `tests/test_claim_citation.py`
- `tests/test_claim_citation_cli.py`
- `tests/test_claim_citation_docs.py`
- readiness adapter coverage in `tests/test_readiness_adapter_v3.py` and `tests/test_readiness_gate.py`

## Current Gaps

The current implementation is useful, but it is still a structural triage layer rather than a true support-review layer.

### Gap 1: Claim Extraction Is Shallow

`extract_citation_contexts()` currently extracts a cleaned sentence around each citation. It does not identify which part of the sentence is the claim, whether the sentence contains a substantive claim, or whether the citation is only background.

Examples that need better handling:

- "Prior work explored similar architectures \cite{...}" is background, not a strong empirical claim.
- "The method significantly improves accuracy \cite{...}" is a stronger support claim.
- A bare citation line is detected, but there is no classification beyond missing context.

### Gap 2: Citation Cluster Semantics Are Minimal

Grouped citations are represented only by `group_size`. The report does not explain whether a citation belongs to a cluster, what the peer keys are, or whether the cluster mixes strong and weak evidence.

### Gap 3: No Citation-Needed Detection

The current runner only sees existing citations. It cannot flag high-assertion sentences without nearby citations.

This should be added carefully because false positives can be noisy. Start with conservative heuristics only.

### Gap 4: No Topic / Field Mismatch Signals

The current scorer does not compare claim context with reference metadata. It can detect high-risk references via hallucination labels, but it cannot flag likely topic mismatch between claim text and title/abstract/keywords.

### Gap 5: No Overclaim Or Outdated-Support Signals

The current scorer does not distinguish:

- weak support
- overclaim
- outdated support
- generic background citation
- citation key missing

Everything collapses into `WEAK`, `SUPPORTED`, or `WELL_SUPPORTED`.

### Gap 6: Next Actions Are Too Generic

`recommended_action` is currently tied mostly to the triage label and hallucination risk. It should become more actionable:

- "Check whether this reference actually supports the claimed improvement."
- "Add a closer source or soften the wording."
- "Verify the citation key or add the missing `.bib` entry."
- "Manual verification required because this reference is unsupported by current evidence."

## Product Goals

The next iteration should answer a more practical reviewer question:

```text
Does this citation plausibly support the nearby claim, and what should a human check next?
```

It should expose evidence, not pretend to decide academic truth.

## Non-Goals

- Do not rewrite thesis text.
- Do not replace citation keys.
- Do not insert new bibliography entries.
- Do not claim a paper is fake.
- Do not claim a citation definitely supports or does not support a claim.
- Do not require external network calls for the basic support-review pass.
- Do not introduce a new major version label unless the public contract changes materially.

## Proposed Output Model

Keep the existing output files for compatibility:

- `reports/claim-citation-triage-report.json`
- `reports/claim-citation-triage.md`
- `reports/claim-citation-triage.csv`

Add fields incrementally rather than renaming the artifact family.

Suggested new per-entry fields:

```json
{
  "claim_type": "empirical_result | method_claim | background | definition | literature_review | unclear",
  "support_signals": ["metadata_title_overlap", "low_hallucination_risk", "complete_metadata"],
  "risk_signals": ["bare_context", "high_risk_reference", "possible_topic_mismatch"],
  "support_review_label": "STRONG_REVIEW | ADEQUATE_REVIEW | WEAK_REVIEW | NEEDS_MANUAL_REVIEW | ORPHANED | UNVERIFIABLE",
  "support_review_reason": "Short human-readable reason",
  "next_actions": ["Human action 1", "Human action 2"]
}
```

Keep current `triage_label` during the transition. Treat `support_review_label` as a richer interpretation layer, not a breaking replacement.

## Proposed Labels

The current labels remain valid for backward compatibility.

Add a support-review label layer:

| Label | Meaning | Blocking |
|---|---|---|
| `STRONG_REVIEW` | Evidence is structurally strong and low-risk, but still human-reviewable | No |
| `ADEQUATE_REVIEW` | Evidence appears adequate with minor caveats | No |
| `WEAK_REVIEW` | Evidence is weak, vague, incomplete, or mixed | No by default |
| `NEEDS_MANUAL_REVIEW` | Specific mismatch, overclaim, outdated-support, or citation-needed risk is suspected | Optional WARN |
| `ORPHANED` | Citation key is missing from bibliography | Yes |
| `UNVERIFIABLE` | Current evidence cannot verify this source type | No by default |

The label names deliberately avoid final truth claims.

## Evidence Signals To Add

### 1. Claim Type Heuristics

Start with deterministic phrase-level heuristics:

- empirical result: "improve", "increase", "decrease", "significant", "outperform", "achieve"
- method claim: "propose", "introduce", "use", "based on", "framework"
- background / literature review: "prior work", "studies", "literature", "has explored"
- definition / concept: "defined as", "refers to", "means"
- unclear: fallback

This can live in `core/citation_integrity/claim_citation.py` first. Move to a separate module only if it grows.

### 2. Citation Cluster Details

Add evidence fields:

- `cluster_size`
- `cluster_keys`
- `cluster_has_high_risk_reference`
- `cluster_has_orphaned_reference`

This lets the report explain mixed clusters instead of scoring each key in isolation.

### 3. Metadata Overlap

Start with cheap local signals:

- normalized token overlap between claim context and bibliography `title`
- optional overlap with `abstract` or `keywords` if present in `.bib`
- ignore stopwords and very short tokens

This is not semantic similarity. It is a weak signal that should be reported as evidence only.

### 4. Outdated-Support Heuristic

If the claim context contains recent-year wording or explicit current-year references and the cited reference is old, flag `possible_outdated_support`.

Keep this conservative and opt-in by rule-pack threshold later if needed.

### 5. Citation-Needed Candidate Detection

Add a separate future pass after entry-level support review is stable.

Candidate heuristic:

- scan sentences without citations
- flag only strong empirical or universal claims
- avoid headings, figure captions, equations, and very short sentences

Output should be advisory and separate, for example an additional `citation_needed_candidates` array in the same JSON report.

## Implementation Phases

### Phase 1: Report Enrichment Without Behavior Breakage

Goal: add useful fields while preserving current labels, exits, and output filenames.

Tasks:

1. Add claim type heuristics.
2. Add support/risk signal arrays.
3. Add richer `next_actions` list while keeping `recommended_action`.
4. Add metadata title-token overlap as a weak evidence signal.
5. Extend JSON/Markdown/CSV writers to expose the new fields.
6. Add tests without changing existing expected labels.

Acceptance:

- Existing claim-citation tests still pass.
- New tests cover claim type, metadata overlap, next actions, and markdown rendering.
- CLI exit behavior remains unchanged: only `ORPHANED` exits 1.

### Phase 2: Cluster-Aware Review

Goal: make grouped citations inspectable.

Tasks:

1. Track cluster keys for each citation occurrence.
2. Add cluster-level risk summary.
3. Flag mixed clusters where one key is high-risk or orphaned.
4. Improve markdown grouping for cluster findings.

Acceptance:

- Mixed demo shows why grouped citations are not all equally safe.
- CSV includes enough fields for spreadsheet review.

### Phase 3: Citation-Needed Candidates

Goal: identify uncited strong claims conservatively.

Tasks:

1. Add sentence scanner for uncited claims.
2. Add `citation_needed_candidates` to JSON.
3. Add Markdown section for citation-needed candidates.
4. Add demo fixture with obvious uncited empirical claims.

Acceptance:

- No exit-code change by default.
- Findings are advisory only.
- False-positive-sensitive cases are covered by tests.

### Phase 4: Optional Abstract / Keyword Evidence

Goal: use richer bibliography metadata when present.

Tasks:

1. Read `abstract` and `keywords` fields from `.bib` entries.
2. Add token overlap against title + abstract + keywords.
3. Keep source evidence explicit: title overlap vs abstract overlap vs keyword overlap.
4. Avoid network calls in this phase.

Acceptance:

- Works with local `.bib` only.
- Report clearly says this is weak lexical evidence, not semantic verification.

## Test Plan

Add or extend tests in:

- `tests/test_claim_citation.py`
- `tests/test_claim_citation_cli.py`
- `tests/test_claim_citation_docs.py`

Recommended new tests:

1. empirical-result sentence gets `claim_type = empirical_result`.
2. background sentence gets `claim_type = background`.
3. title-token overlap appears in evidence when claim and title share meaningful tokens.
4. missing title/author produces metadata risk signal.
5. high hallucination risk produces high-risk signal and specific next action.
6. grouped citation includes `cluster_keys` and `cluster_size`.
7. support-review fields do not change legacy `triage_label` behavior.
8. Markdown includes new support review reason.
9. CSV includes new fields or preserves backward-compatible columns with appended columns.

## Documentation Plan

Update after Phase 1 implementation:

- `README.md`
- `README.zh-CN.md`
- `docs/examples.md`
- `docs/modules.md`
- `docs/roadmap.md` only if the public direction changes again
- `site/artifact-gallery.html` only if screenshots/copy need the richer output story

Docs must keep the same boundary language:

- "support review" not "truth detection"
- "possible mismatch" not "incorrect citation"
- "manual review recommended" not "fake"

## Release And Versioning Guidance

Do not bump to a new major version for Phase 1 or Phase 2.

Use a normal incremental release only after the public docs and examples are aligned. Consider a major version only if the shipped behavior becomes a new public workflow with new artifact contracts, such as a full support-review packet or candidate-reference workflow.

## Recommended Next Action

Start with **Phase 1: Report Enrichment Without Behavior Breakage**.

It is the lowest-risk step because it improves user value while preserving current labels, output filenames, readiness integration, and CLI exit behavior.
