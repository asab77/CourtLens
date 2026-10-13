# Citation-support candidate labeling guidelines

**Status: PROPOSED.** Initial labels/justifications are Codex proposals, not
independent human adjudication. Candidates are not frozen or an official benchmark.
Human approval is required before treating `gold_support_label` as gold truth.
No verifier was built or optimized against these labels.

## Unit and support scope

Evaluate the claim against its complete, exact cited passage. Preserve material
scope, legal qualifications, opinion attribution, and quotation context. Do not
use retrieval scores, original model confidence, question-type labels, or outside
knowledge as a support proxy. An externally true proposition may be UNSUPPORTED
by its selected passage. The corpus's page-overlap retrieval relevance convention
is separate from substantive citation support; the existing benchmark is unchanged.

Most claims target one proposition, with attribution/scope integral to it. Five
explicit `compound_probe` examples retain components for the multi-part/incomplete
support requirement. Do not treat those as atomic training instances without an
explicit decision to split them later. A verbatim historical sentence can contain
interrelated propositions; reviewers should decide whether further decomposition
would improve the unit without changing source wording.

## Four proposed claim labels

- **SUPPORTED:** Every material proposition, attribution, and necessary qualification
  is established by the passage. Reasonable faithful paraphrase is allowed.
- **PARTIALLY_SUPPORTED:** A meaningful part is established, but some component,
  scope, or necessary qualification is missing or overstated. Specify both parts.
- **UNSUPPORTED:** The material claim or asserted attribution is not established.
  Mere topic overlap, plausible external truth, and valid source IDs do not suffice.
  Absence is not contradiction.
- **CONTRADICTED:** The passage affirmatively states an incompatible proposition,
  including a reversed stance. Identify the exact incompatible source language.

For compound probes with a supported part and a contradicted part, this initial
proposal uses PARTIALLY_SUPPORTED and flags high-priority review. Human reviewers
must decide whether to retain that convention, prefer CONTRADICTED for any material
contradiction, or split components. Absolute exclusivity versus omitted qualification
is another explicit partial/contradicted boundary requiring adjudication.

Support is passage-local, not a declaration of the legally correct result. In
particular, an unsupported Dobbs statement must not be called contradicted just
because a reviewer knows its actual holding from outside this context.

## Attribution and quotations

A concurrence or dissent does not by itself establish that its author's reasoning
was the majority rationale. Distinguish reporting another opinion from endorsing
it. A dissent may faithfully reproduce majority words; a claim accurately identifying
that embedded quotation can be supported even when its container is a dissent.
Do not reject solely because of the container's opinion label, and do not convert
an embedded quote into the dissenter's own controlling holding.

Raw `opinion_type`/`author` fields are retained, not verified. The Miranda source
labeled unknown explicitly contains Syllabus; it does not identify Warren as its
syllabus author. The Tinker Stewart-labeled chunk contains a Black dissent header.
Treat page-header/OCR uncertainty explicitly, not as proof of invented authorship.

`exact_quotation` must be a literal substring of the source chunk. Extraction
hyphenation, punctuation and OCR artifacts are retained even when awkward.
Constructed paraphrases are claims, never fabricated source quotations. PDF page
ranges describe the full chunk's extraction provenance, not a fabricated precise
page location for a sentence. No OCR repair or PDF-layout revalidation occurred.

## Authentic versus synthetic

Every cited source is authentic corpus text. `example_kind` classifies the
claim–citation pairing, not whether its source passage is fabricated:

- **authentic:** A verbatim smoke-answer claim with its original cited source
  (including paragraph-scoped references explicitly documented as such).
- **synthetic:** A constructed claim or a newly assigned claim–passage pairing.
  A verbatim Miranda list item newly paired with one member of an answer's grouped
  citation context remains a synthetic example with `claim_origin=verbatim_smoke_answer`.

`pairing_origin`, `claim_origin`, and `provenance.evidence_origin` distinguish these
axes. Supplemental concurrence contexts use example-local [S1]; that is an
explicit constructed context identifier, not a historical smoke citation.
Smoke IDs are scoped to their original case context: A/S1 is not B/S1.

The cited complete chunk is stored in each candidate. SHA-256 hashes and exact
metadata bind it to both frozen chunks and vector-store records. Smoke-derived
bindings also point to the exact original selected-evidence record. Generated
answers are preserved as saved or explicitly marked constructed; no new model
responses were requested.

## Answer-level evaluation is separate

Answer examples use `response_assessment`, never the four claim-support labels:

| Dimension | Values | Question |
|---|---|---|
| completeness | COMPLETE / INCOMPLETE / NOT_APPLICABLE | Does it address the requested material points given this context? |
| abstention | APPROPRIATE / UNWARRANTED / NOT_APPLICABLE | Does this supplied context establish an answer or justify refusal? |
| certainty | JUSTIFIED / OVERSTATED / NOT_APPLICABLE | Does the answer's certainty exceed what its context establishes? |
| citation_coverage | ADEQUATE / INCOMPLETE / MISLEADING / NOT_APPLICABLE | Are material claims appropriately linked to the available passages? |

An answer can be complete for the requested relationship yet overstate a holding
or have incomplete citation coverage. A refusal can be appropriate while appended
citations mislead. “Unsupported abstention” is operationalized as UNWARRANTED
when direct context evidence answers the question. Completeness is context/task
coverage, not universal coverage of Supreme Court law. Reviewers can disagree
and must explain their proposed changes.

## Schema and review workflow

`citation_support_candidates.json` contains version/status, label/category
vocabularies, required field lists, `claim_examples`, and `answer_examples`.
Each claim has question/text/citation/source attribution/pages, a proposed label,
rationale, component structure, authenticity/pairing flags and complete provenance.
Answer examples carry exact complete selected contexts and separate assessment axes.
An example envelope (illustrative schema, not an additional candidate):

```json
{
  "example_id": "CS-001",
  "level": "claim",
  "review_status": "PROPOSED",
  "gold_support_label": "SUPPORTED",
  "citation_identifier": "S1",
  "example_kind": "synthetic",
  "claim_origin": "verbatim_smoke_answer",
  "pairing_origin": "constructed_evidence_pairing"
}
```

Read every claim with its full source in `citation_support_review.md`. For answer
reviews, inspect full contexts in the JSON, not just case/page labels. All examples
require approval; high-priority items specifically flag attribution, quoted-majority
reasoning, OCR, missing qualifications, and partial/contradicted boundaries.
Record reviewer identity, approve/relabel/reject, proposed final outcome, reason,
and date in a separate reviewed artifact. Do not change source passages, silently
relabel frozen benchmark files, infer approval, or freeze this candidate set.

The deterministic builder refuses to overwrite differing candidates/review files.
Running it reproduces the proposed artifacts locally without provider requests.
Existing source artifacts and prior citation-integrity tests remain protected.

## Limits

This is a deliberately small challenge set dominated by Miranda/Obergefell, with
Gideon, New York Times, and Tinker concurrence probes. It does not represent all
eight cases or deployment claim frequencies. It has no held-out split, calibrated
scores, verifier metrics, human-agreement estimates, or automated legal judgment.
A future verifier comparison must specify input units and avoid leakage from
near-duplicate claims/passage pairs. All initial labels remain contestable.

## Local validation record — Phase 7B.2A

- 32 claim examples: 10 SUPPORTED, 8 PARTIALLY_SUPPORTED, 8 UNSUPPORTED,
  6 CONTRADICTED; all labels PROPOSED.
- Six separate answer examples; three authentic saved answers and three
  constructed answers/refusals. Claim pairs: two authentic, 30 synthetic,
  including verbatim claims assigned new evidence pairings.
- All 15 A–O coverage requirements represented; exact IDs/counts appear in the
  review and can be computed from `coverage_categories` (categories overlap).
- Ten deterministic dataset tests and the full 322-test repository suite pass.
- 52 example/context source references match exact frozen text and metadata.
- All 164 protected before/after SHA-256 values match, including 133 existing
  data files, every prior test module, and eight response/retrieval modules.
  Only the two new candidate/review files were added under data.
- No source/benchmark/smoke artifact or prior citation test was modified.
  No live API calls, verifier implementation, commits, or pushes occurred.

**READY for human adjudication.** All 38 examples need review; especially prioritize
CS-003, CS-007, CS-008, CS-012, CS-013, CS-015, CS-017, CS-018, CS-024, CS-025,
CS-031, and CS-032. Approval, relabeling, or rejection remains a human decision.
