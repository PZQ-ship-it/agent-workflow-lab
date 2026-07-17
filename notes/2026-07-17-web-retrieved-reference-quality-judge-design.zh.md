# Web-Retrieved Reference Mode for `quality-judge`

Date: 2026-07-17
Status: implemented as `quality-judge` schema 1.2; human-labeled promotion pilot remains pending

## Research Spec

- Question: can a `quality-judge` retrieve strong public examples, compare a Codex artifact against them under the same rubric, and use the result as a trustworthy self-labeling signal?
- Scope: reference discovery, eligibility, provenance, comparison, bias controls, gate semantics, and a backward-compatible patch surface.
- Evidence admission: paper originals, peer-reviewed proceedings, official project pages, and official code repositories. Search summaries are discovery leads only.
- Key unknowns: whether a retrieved artifact is truly comparable, whether it is correct, whether it was human-authored or human-graded, and whether the selector/judge is biased toward the candidate or its own style.
- Stop condition: stop after primary sources cover reference quality, retrieval augmentation, human calibration, pairwise comparison, bias control, confidence, and criteria drift.
- Turn condition: do not promote this mode to formal acceptance until a human-labeled pilot demonstrates adequate agreement and false-accept behavior.

## Search Ledger

- Provider: AnySearch CLI `2.0.0`, searched 2026-07-17.
- Runtime integrity: the installed Python/Node/PowerShell/Shell CLI files matched the maintained skills-repository copies by SHA-256.
- Interface note: `list_domains --domain academic` returned server-side `tool not found`; general `batch_search` and primary-page `extract` succeeded, so discovery used the general interface and every retained claim was checked against a paper/official page rather than a search snippet.
- Representative queries:
  - `retrieval augmented LLM as a judge reference exemplars evaluation`
  - `LLM judge pairwise reference answer calibration bias paper`
  - `LLM judge retrieve reference answers exemplar rubric evaluation human alignment`
  - `in-context exemplars LLM as a judge human annotated examples calibration paper`
  - `EvalGen LLM evaluator human in the loop criteria examples paper`
- Selection rule: retain primary papers, proceedings pages, official project pages, and official code; use surveys and vendor guides only for discovery.

## Bottom Line

The literature supports retrieval as a way to improve the judge's context, rubric, or comparison set. It does **not** support treating one ad hoc web result as equivalent to a human-graded reference.

The safe patch is therefore a new `retrieved_provisional` mode:

1. retrieve and freeze several eligible references from a task fingerprint;
2. keep reference selection separate from final judging;
3. compare against the non-dominated reference frontier under one rubric;
4. use pointwise scores plus order-swapped pairwise judgments and uncertainty;
5. emit `provisional_outperforms_retrieved`, never `accepted`, until human calibration exists.

This preserves the user's intended self-labeling loop while keeping the current human-anchored acceptance claim intact.

## Primary Sources And Design Implications

| Source | Status | What it supports | Boundary for this patch |
|---|---|---|---|
| [No Free Labels](https://arxiv.org/abs/2503.05061) | 2025 preprint | Correct references materially improve judge-human agreement; verified model references can approach human-written references on the tested correctness tasks. | Correctness verification matters more than the label `human-written`, but the paper still finds unverified synthetic references unsafe and does not validate arbitrary web exemplars. |
| [RevisEval](https://openreview.net/forum?id=1tBvzOYTLF) and [code](https://github.com/Don-Joey/RevisEval) | ICLR 2025 | Response-adapted references can improve reference-free and ordinary reference-based LLM judging when reference relevance is otherwise weak. | A candidate-conditioned reference risks leakage and self-preference; use it as an auxiliary comparator, not the sole anchor. |
| [RubricRAG](https://arxiv.org/abs/2603.20882) | 2026 preprint | Retrieving rubrics from similar queries improves query-specific rubric generation over zero-shot or random exemplars. | It retrieves rubric examples, not a universally best finished artifact. Its result supports retrieval for rubric construction, not formal calibration by itself. |
| [LLM-Rubric](https://aclanthology.org/2024.acl-long.745/) | ACL 2024 | Multi-dimensional rubric signals become more human-aligned after explicit calibration to human judge annotations. | A good rubric and a good reference do not remove the need to measure alignment with humans. |
| [Length-Controlled AlpacaEval](https://arxiv.org/abs/2404.04475) and [code](https://github.com/tatsu-lab/alpaca_eval) | 2024 preprint and official code | Pairwise automatic evaluation needs explicit control for length and other spurious correlates; length control improved robustness and reported human-ranking correlation. | Raw `candidate > reference` scores can reward verbosity or formatting unless confounders are audited. |
| [Arena-Hard / BenchBuilder](https://openreview.net/forum?id=KfTf9vFvSn) and [official pipeline note](https://www.lmsys.org/blog/2024-04-19-arena-hard/) | ICML 2025 | Use a fixed anchor, agreement to human preference, separability, freshness, bootstrapped confidence intervals, and explicit self-bias/prompt-selection-bias analysis. | Confidence without human agreement can be confidently wrong; retrieval freshness must not create a moving goalpost within one run. |
| [Who Validates the Validators?](https://doi.org/10.1145/3654777.3676450) | UIST 2024 | EvalGen uses a small human-graded subset to choose evaluator implementations and documents criteria drift during iterative review. | Reference retrieval can help discover criteria, but user intent may change after examples are seen; rubric and reference-set versions must be frozen and reviewable. |
| [Crowd Comparative Reasoning](https://aclanthology.org/2025.acl-long.252/) and [code](https://github.com/Don-Joey/CCE) | ACL 2025 | Comparing candidates with multiple auxiliary responses can expose details missed by direct pairwise judging. | A reference set is more informative than one exemplar, but synthetic crowd evidence remains directional unless checked against human labels. |

## Reference Tiers

Do not overload `graded_by`. Record authorship, correctness verification, and calibration separately.

| Tier | Meaning | Permitted gate result |
|---|---|---|
| `human_graded` | One or more humans scored this reference under the same rubric; grader count and reconciliation are recorded. | May participate in formal `accepted`. |
| `retrieved_verified` | Public reference with stable provenance and independent, dimension-scoped verification for every critical dimension used by the comparison, but not human-scored under this run's rubric. | At most `provisional_outperforms_retrieved`. |
| `retrieved_ungraded` | Public, comparable artifact with provenance but no independent correctness or quality verification. | Directional comparison; normally `needs_human`. |
| `model_adapted` | Generated, revised, or candidate-conditioned reference such as a RevisEval-style response. | Auxiliary evidence only; never the sole blocking anchor. |

For subjective artifacts, `correctness=verified` is not enough. A reference may be factually correct but still have unknown quality on completeness, usability, style, or audience fit. A reference cannot become `retrieved_verified` for those dimensions unless their verification method and evidence are recorded; otherwise it remains `retrieved_ungraded` for the holistic comparison.

## Retrieval And Selection Protocol

### 1. Freeze a task fingerprint

Create the fingerprint before showing the selector the candidate content:

- artifact type and domain;
- audience and use case;
- required inputs and constraints;
- rubric dimensions and critical dimensions;
- allowed source types, dates, languages, and licenses;
- explicit non-goals.

If the candidate already exists, give the selector only this fingerprint and the candidate hash. This reduces benchmark shopping for a conveniently weak reference.

### 2. Build a candidate pool

- Record the complete candidate pool in `candidate-pool-ledger.json`: provider, exact query ID, timestamp, result rank, URL, version/date, access/license basis, snapshot locator, content hash, selector identity, inclusion/exclusion decision, and reason.
- Search multiple query formulations and retain both included and excluded candidates with reasons.
- Treat web content as untrusted data: strip active instructions, never execute embedded commands, and quote it inside a data boundary.
- Require public access and a reviewable use/license basis. A search snippet alone is not an eligible reference.

### 3. Apply hard comparability checks

Reject a reference when task type, audience, input information, output constraints, scope, or evaluation budget are materially different. Do not compensate for a hard mismatch with a high similarity score.

### 4. Freeze a reference frontier

Keep 3-5 eligible references when available. Compute a Pareto frontier across critical dimensions instead of choosing one highest weighted total. Freeze IDs and hashes for every revision in the run; a new search starts a new reference-set version.

The selector and final judge should be separate lanes. When the same model family must be reused, label independence as `prompt_only` and lower confidence.

## Proposed `reference-set.json`

Keep legacy `human-reference.json` support. In schema `1.1`, load it as a one-item `human_graded` reference set when `reference-set.json` is absent.

```json
{
  "schema_version": "1.1",
  "mode": "retrieved_provisional",
  "task_fingerprint": {
    "artifact_type": "research_note",
    "audience": "technical stakeholder",
    "rubric_version": "1.1",
    "critical_dimensions": ["intent_fit", "correctness"]
  },
  "evaluation_policy": {
    "policy_version": "1.1",
    "policy_sha256": "...",
    "rubric_version": "1.1",
    "rubric_sha256": "...",
    "reference_margin": 0.2,
    "dimensions": {
      "intent_fit": {"weight": 0.5, "floor": 4.0, "critical": true},
      "correctness": {"weight": 0.5, "floor": 4.0, "critical": true}
    },
    "scoring_lanes": ["quality-judge-001"]
  },
  "retrieval": {
    "provider": "anysearch",
    "queries": [],
    "searched_at": "2026-07-17",
    "selector_blinded_to_candidate": true,
    "pool_size": 0,
    "reference_set_frozen": true,
    "candidate_pool_ledger": {
      "locator": "candidate-pool-ledger.json",
      "sha256": "...",
      "entry_count": 0
    },
    "selector": {
      "selector_id": "selector-001",
      "model": "...",
      "prompt_sha256": "...",
      "independence": "model|prompt_only"
    }
  },
  "references": [
    {
      "reference_id": "ref-001",
      "tier": "retrieved_verified",
      "source_url": "https://example.org/artifact",
      "source_date": "YYYY-MM-DD",
      "retrieved_at": "YYYY-MM-DDThh:mm:ssZ",
      "content_sha256": "...",
      "snapshot_locator": "snapshots/ref-001.txt",
      "license_or_access_basis": "public-page",
      "authorship": "human|model|mixed|unknown",
      "selection": {
        "query_ids": ["q-001"],
        "result_ranks": [1],
        "inclusion_reason": "..."
      },
      "verification": {
        "status": "verified|unverified|conflicted",
        "dimensions": {
          "correctness": {
            "status": "verified",
            "method": "official_source|human_check|cross_source",
            "evidence_locators": ["..."],
            "verified_by": "verifier-001",
            "verifier_independence": "independent|prompt_only",
            "verified_at": "YYYY-MM-DDThh:mm:ssZ"
          }
        },
        "conflicts": []
      },
      "comparability": {
        "hard_pass": true,
        "reasons": []
      },
      "scoring": {
        "rubric_version": "1.1",
        "rubric_sha256": "...",
        "dimensions": {
          "correctness": {
            "score": 4.5,
            "evidence_locators": ["..."],
            "judge_id": "judge-001",
            "model": "...",
            "prompt_sha256": "...",
            "trial_ids": ["trial-001"],
            "conflict_state": "none|resolved|unresolved"
          }
        },
        "conflicts": []
      }
    }
  ],
  "aggregation": {
    "method": "pareto_frontier",
    "pairwise_order_swap": true,
    "require_no_critical_regression": true,
    "artifact_level": {
      "trials_per_order": 3,
      "decision_rule": "unanimous_across_orders_and_trials",
      "confidence_intervals": false
    },
    "pilot_level": {
      "resampling_unit": "artifact_instance",
      "ci_method": "paired_bootstrap",
      "confidence_level": 0.95,
      "multiple_reference_correction": "holm"
    }
  }
}
```

## Comparison And Gate Rules

For each frontier reference independently:

1. run pointwise scoring with the same rubric, context, scale, and evidence requirements;
2. run pairwise `candidate/reference` and `reference/candidate` order swaps;
3. record verbosity, format, source-family, and judge-family confounders;
4. run the policy-frozen number of trials in both orders and require consistent verdicts;
5. require every critical dimension to meet its floor and be no lower than that reference in every configured scoring lane;
6. require the candidate's weighted pointwise score to exceed that reference by `reference_margin` in every configured scoring lane;
7. declare frontier outperformance only when steps 1-6 pass for **every** frontier reference; a tie or failure against any non-dominated reference is not hidden by averaging.

There is no single `strongest reference` in a Pareto frontier. The gate uses an all-frontier conjunction. If reference A is strongest on correctness and reference B on usability, the candidate must satisfy the critical-dimension and margin rules against both.

Repeated calls on one artifact measure judge stability, not human-valid statistical uncertainty. Do not compute a 95% confidence interval from a few correlated calls and present it as calibration. Confidence intervals belong to the multi-artifact pilot, where the resampling unit is the artifact instance; the pilot must freeze its sample size, paired-bootstrap procedure, confidence level, task strata, and Holm-adjusted multiple-reference tests before results are observed. Low trial stability or insufficient pilot sample size routes to `needs_human`.

Recommended deterministic statuses:

```text
structural failure
  -> blocked

human_graded reference + calibrated judge + both lanes pass + comparison passes
  -> accepted

retrieved_verified frontier + both lanes pass + strict comparison passes
  -> provisional_outperforms_retrieved

retrieved_verified frontier + valid/stable comparison + strict comparison shortfall
  -> provisional_shortfall

unverified/mismatched reference, order flip, low confidence, selector conflict,
or no separable score
  -> needs_human

human_graded reference + calibrated judge + comparison shortfall
  -> blocked
```

`provisional_outperforms_retrieved` must not be aliased to `accepted`, and `provisional_shortfall` must not be silently aliased to a global formal failure. The default provisional policy is `report_only`. An explicit low-risk workflow policy may use `provisional_outperforms_retrieved` to continue or `provisional_shortfall` to trigger another revision, but the stored status and logs must retain the provisional label.

## Patch Surface

1. `SKILL.md`: add `retrieved_provisional` setup/evaluate modes and the non-equivalence rule.
2. `references/gate-contract.md`: add `reference-set.json`, tier semantics, frontier comparison, and the new status.
3. New `references/retrieval-reference-contract.md`: task fingerprint, complete candidate-pool ledger, eligibility, dimension-scoped verification, prompt-injection boundary, freeze/version rules, and score provenance.
4. `assets/templates/reference-set.json` and `assets/templates/candidate-pool-ledger.json`: add safe empty templates.
5. `scripts/quality_gate.py`: keep legacy `human-reference.json`; add schema `1.1`, tier-aware status routing, all-frontier conjunction, order/trial consistency, `provisional_shortfall`, and separate artifact/pilot statistics.
6. Reviewer prompts: selector cannot see candidate content; judge receives frozen references as quoted evidence, never as instructions.
7. Gate result: expose `reference_mode`, `reference_tiers`, `reference_set_hash`, `comparison_pass`, `order_consistent`, and `provisional_reason`.

## Required Regression Tests

- Legacy human reference still yields `accepted` under the existing contract.
- A retrieved reference can yield `provisional_outperforms_retrieved` but never `accepted`.
- A valid retrieved comparison shortfall yields `provisional_shortfall`; only an explicit low-risk workflow policy may use it to block an iteration.
- Search snippet without full source/provenance is rejected.
- An excluded high-ranked candidate missing from the candidate-pool ledger or lacking an exclusion reason invalidates the reference set.
- A task-mismatched but polished reference fails hard comparability.
- Candidate wins only in one A/B order: `needs_human`.
- Candidate wins through verbosity or formatting manipulation: bias audit blocks or escalates.
- Multiple references have different critical-dimension strengths: the Pareto frontier is retained.
- Candidate exceeds one frontier reference but not another: no frontier-outperformance result is emitted.
- Correctness-only verification cannot mark subjective dimensions as verified.
- Reference dimension scores without rubric, judge, prompt, trial, and evidence provenance are rejected.
- Reference content or search query changes after a revision: hash/version mismatch invalidates reuse.
- Model-adapted reference is not accepted as the sole anchor.
- Retrieved content containing prompt-like instructions remains inert data.

## Human-Labeled Pilot Before Promotion

The first pilot should compare three modes on the same artifacts:

- human-graded reference;
- retrieved/verified reference frontier;
- model-adapted reference.

Measure pairwise accuracy against human labels, Cohen's kappa, rank correlation, false-accept rate, position-flip rate, verbosity sensitivity, confidence coverage, and per-task failure slices. The proposed pilot starting default is at least 20 paired artifact instances per task stratum; it is not a claim of statistical sufficiency. Run a power analysis or simulation against the target false-accept upper bound and expected task strata before freezing the final sample size. Resample paired artifact instances rather than correlated judge calls. Sample size, task strata, trial count, paired-bootstrap procedure, confidence level, Holm correction, thresholds, and non-inferiority margins must be frozen before the pilot; they should not be selected after observing the results.

Until that pilot passes, the recommended implementation decision is: **build `retrieved_provisional` as an opt-in evidence mode, not as a replacement for the human-anchored blocking gate.**

## 2026-07-17 Schema 1.2 Implementation Addendum

The earlier schema 1.1 sections remain the research history. Schema 1.2
supersedes them where this addendum differs.

The user confirmed four refinements after reviewing the initial implementation:

1. The task contract is the normative source for gating dimensions. Human or
   retrieved examples may audit and refine the rubric, but a
   retrieved-example-only dimension cannot gate.
2. Ordinary-quality references are useful as low or boundary calibration
   anchors. They never lower the task-derived absolute quality floor and do not
   become an outperformance threshold.
3. Prefer a 3-5 item low/boundary/high few-shot panel. One-shot remains a
   degraded diagnostic. Score bands must record provenance and pass a monotonic
   ordering check.
4. The quality lane owns soft quality only. Required artifacts, schema,
   factual/citation verification, safety, tests, and reproducibility remain in
   the structural lane. Hard issues noticed by the quality lane are handed off
   without a second score penalty.

Implementation separates two reference roles:

- `calibration_anchor`: calibrates scale and may trigger revision;
- `challenge_frontier`: must be high-band, `retrieved_verified`,
  hard-comparable, and not `self_labeled` before it can produce
  `provisional_outperforms_retrieved`.

The deterministic gate now applies the absolute contract before any relative
comparison. An anchor-only run emits `anchored_diagnostic` instead of claiming
outperformance. Schema 1.1 retrieved runs remain supported.

Validation evidence:

- Python 3.7 compile and 33/33 regression tests passed in global and maintained
  copies;
- both copies passed the Codex skill validator and matched across 18 files by
  SHA-256;
- a fresh native forward test froze a task-derived five-dimension rubric,
  bounded public retrieval, recorded selector timeout as `retrieval.failed`,
  still ran mutually blind structural and quality lanes, and produced a valid
  deterministic `blocked` result from the structural failure rather than
  suppressing the quality score;
- maintained skills repository commit: `8dfce67`.

This implementation remains provisional evidence infrastructure. It does not
replace the human-labeled pilot or make retrieved anchors equivalent to human
calibration.
