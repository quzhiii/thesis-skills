# Thesis Skills Commercialization v0.1

## Purpose

This document turns the current product discussion into a practical commercialization split for Thesis Skills.

It is not a fundraising deck, not a pricing promise, and not a final strategy memo.

Its job is to answer four operational questions:

1. What should remain open-core?
2. What is most realistic to charge for?
3. Which customer segment should be validated first?
4. What should be built next if commercialization becomes a priority?

## Current Product Reality

Thesis Skills is currently strongest as a:

- deterministic thesis finishing workflow engine
- pre-submission audit and handoff toolchain
- citation-risk and reference-quality review system
- local, inspectable, report-first CLI product

It is not currently strongest as a:

- mass-market student writing app
- general AI writing assistant
- broad academic SaaS platform
- collaborative cloud editor

The most commercially meaningful part of the current stack is not "Python scripts" themselves. It is the ability to reduce final-stage thesis delivery risk through:

- rule-based checking
- evidence aggregation
- readable review artifacts
- workflow standardization

## Strategic Positioning

Recommended positioning:

```text
Thesis Skills = thesis delivery and final-audit workflow product
```

Not:

```text
Thesis Skills = general student writing tool
```

Commercially, this matters because the first group that pays reliably is usually not "everyone who writes a thesis." It is people who already experience repeated delivery pain.

## Priority Customer Segments

### Segment A: Thesis editing / formatting / advisory service teams

This is the most promising first-paying segment.

Why:

- clear ROI from reduced rework
- repeated use across many projects
- strong need for standardized delivery
- stronger willingness to pay than individual students
- immediate value from HTML handoff surfaces and audit artifacts

What they likely buy:

- team workflow standardization
- school-specific rule packs
- final-audit delivery bundles
- batch processing and project management later

Risks:

- they need stability, not just clever features
- they may want support and customization quickly

### Segment B: Near-graduation individual students

This is the highest-demand segment, but not automatically the highest-value segment.

Why demand is high:

- time pressure is intense
- fear of rejection / rework is real
- formatting, references, and audit issues are painful near deadlines

Why monetization is harder:

- price sensitivity is high
- support burden can be high
- onboarding must be much simpler than a CLI-first developer experience

What they likely buy:

- school-specific graduation pack
- submission-prep audit pack
- one-time or short-term access

### Segment C: Labs / research groups

This is a plausible second-stage B2B-light segment.

Why:

- repeated internal thesis workflows
- need for consistency across members
- likely to value local/offline workflows

What they likely buy:

- group rule pack
- internal thesis checking workflow
- annual local-use license later

### Segment D: University / department procurement

This should not be the first target.

Why not now:

- long decision cycle
- higher procurement barriers
- more demand for support, compliance, training, and proof of adoption

This is a later-stage possibility, not the first monetization path.

## Recommended Business Model

Recommended model:

```text
Open core + paid rule packs + paid delivery workflow + service layer
```

### Why this model fits Thesis Skills

- the open core helps build trust
- the rule-pack layer is naturally differentiated
- delivery UX is commercially meaningful but not required to prove the engine
- service work can monetize before the product is fully polished

## Product Split

### Community (open-core)

Should remain public:

- intake workflows (Zotero / EndNote / Word / LaTeX)
- deterministic checkers
- baseline fixers
- readiness gate
- citation evidence line
- final-audit foundation checkers
- base JSON / CSV / Markdown / HTML artifacts
- generic rule packs
- examples and docs for public trust

Why keep this open:

- builds credibility
- helps user acquisition
- makes the engine inspectable
- encourages real-world feedback

### Pro (paid product layer)

Best candidates for paid product differentiation:

- school-specific rule packs
- discipline-specific rule packs
- stronger non-technical workflow packaging
- better guided review and export bundles
- batch processing / multi-project workflow
- project history and delivery management
- local desktop workflow later

This is where the real product differentiation should accumulate over time.

### Service (high-touch revenue layer)

High-value services that can coexist with software sales:

- school rule-pack customization
- final thesis audit service
- citation authenticity audit service
- workflow deployment for teams
- training and support for editing/advisory teams

This layer may produce revenue earlier than a polished paid app.

## What To Charge For First

### Strongest first paid offer: school-specific rule packs

This is the most natural first monetization direction.

Why:

- high student pain
- hard to replace with generic tooling
- naturally maintainable as an updateable asset
- can be sold without building a full new application

Examples:

- Tsinghua final submission pack
- Peking University thesis pack
- SJTU thesis pack
- USTC thesis pack
- medical thesis submission pack
- Chinese social-science thesis pack
- English journal submission pack

### Second strong paid offer: final-audit delivery bundles

This is not just a checker. It is a structured delivery outcome.

Example offers:

- submission-prep audit bundle
- advisor handoff audit bundle
- reference risk review bundle
- claim-citation review bundle

These can be sold either as:

- software features
- packaged workflow templates
- or service-backed deliverables

### Third paid offer: team workflow layer

Good for service teams and labs later:

- multiple project queue
- standardized client/project report export
- internal SOP workflow integration

## What Not To Prioritize First

### Not first: full desktop EXE as the main monetization thesis

A desktop app is useful, but packaging format is not the core commercial value.

Users do not pay because something is an EXE.
They pay because it:

- removes setup friction
- saves time
- reduces submission risk
- matches their school workflow
- produces better handoff artifacts

So the better framing is:

```text
CLI engine first
desktop shell later
```

### Not first: broad university procurement

Too early. Too slow. Too many requirements.

## Pricing Logic (Early Hypothesis)

This is a starting hypothesis, not a final price sheet.

### Individual students

Most likely pricing styles:

- one-time purchase
- short-term access
- school-pack add-on

Best fit offer:

- graduation final-audit pack
- school rule pack

### Service teams

Most likely pricing styles:

- annual license
- per-seat team license
- per-project package in early stage

Best fit offer:

- workflow standardization pack
- multi-project review bundle
- custom rule-pack support

### Institutions / labs

Most likely pricing styles:

- annual local deployment fee
- custom support + update contract

## Push / Open-Source Boundary Guidance

### Safe to push publicly now

The current final-audit, report-UX, and claim-citation review surface commits are safe to push publicly.

Why:

- they strengthen the engine and trust layer
- they do not expose future institution-specific paid moats
- they improve the public story and adoption funnel

That includes:

- final-audit foundation checkers
- final-audit report HTML
- reference ledger HTML
- claim-citation HTML
- conservative support-risk signals
- v3.4.1 public alignment

### Better held for future private layers

Future work that should probably stay private or move to a paid repo/product layer:

- school-specific premium rule packs
- institution-tuned calibration data
- batch review / project queue UX
- commercial desktop app shell
- customer delivery dashboards
- internal service workflow tooling

## Recommended Near-Term Product Plan

### Phase 1: strengthen open-core credibility

Keep improving:

- rule reliability
- examples
- HTML report quality
- claim-citation calibration

Goal:

- make the free engine trusted enough that premium layers feel like a natural upgrade

### Phase 2: launch premium rule-pack concept

Do not start with many packs.
Start with 1-2 very specific packs.

Best first experiments:

- one top-tier Chinese university pack
- one discipline-specific thesis pack

Goal:

- validate willingness to pay for direct applicability

### Phase 3: add workflow packaging for non-technical users

This can begin before a full desktop app.

Possibilities:

- guided runner script
- bundled report exporter
- simplified launcher
- premium starter package

### Phase 4: consider desktop product shell

Only after:

- paid use cases are validated
- onboarding pain is clearly limiting growth
- you know which user segment matters most

## Validation Questions To Ask Real Users

For students:

- What is the most stressful part of final submission?
- Have you ever been forced to rework due to formatting, references, or missing sections?
- Would you pay to avoid that in the final 2-4 weeks before submission?
- Would you care more about a school-specific pack or a general checker?

For editing/service teams:

- What percentage of projects require repetitive format/review cleanup?
- How much reviewer or client rework comes from preventable issues?
- Would a standardized audit bundle save staff time?
- Would you pay more for team workflow consistency or for school-specific rules?

## Recommended Next Business Step

The best next commercialization step is:

```text
Define Community / Pro / Service boundaries explicitly and choose the first premium rule-pack experiment.
```

Not:

```text
Build a full desktop app immediately.
```

## Initial Product Recommendation

If forced to choose one commercial wedge first, choose:

```text
Premium school-specific rule packs + final-audit submission bundle
```

This matches:

- the strongest user pain
- the clearest differentiation
- the lowest incremental build cost
- the best fit with the current repository strengths

## Working Decision Summary

- Keep the engine open-core.
- Push current public engine/report improvements.
- Treat school-specific rule packs as the first paid layer.
- Treat desktop packaging as a later convenience layer, not the first business model.
- Validate service teams and near-graduation students first.
