"""Local response envelope validation; no semantic support verification.

Plain chat requests ask for JSON, but no provider-specific JSON/schema capability
is assumed. Invalid output fails closed, without a corrective provider request.
"""
import json
from evidence_context import citation_errors, CANONICAL_CITATION

ANSWERED = 'ANSWERED'
INSUFFICIENT_EVIDENCE = 'INSUFFICIENT_EVIDENCE'
VALIDATION_FAILED = 'VALIDATION_FAILED'
INSUFFICIENT_EVIDENCE_MESSAGE = (
    'The available Supreme Court documents do not provide enough evidence to answer this question.'
)
VALIDATION_FAILED_MESSAGE = (
    'CourtLens could not validate the response format or source identifiers. '
    'The generated draft is not presented as a supported answer.'
)


class ResponseText(str):
    """String-compatible result with explicit state and local-only diagnostics.

    Raw drafts stay here for debugging; do not log them or serialize them into
    user-facing messages. A state is a contract outcome, not a truth judgment.
    """
    def __new__(cls, text, state, errors=(), raw_draft=None):
        result = super().__new__(cls, text)
        result.response_state = state
        result.validation_errors = tuple(errors)
        result.raw_draft = raw_draft
        return result


def failure(raw_draft=None, errors=()):
    return ResponseText(VALIDATION_FAILED_MESSAGE, VALIDATION_FAILED, errors, raw_draft)


def answered_response(answer, source_ids, raw_draft=None):
    """Validate an explicitly ANSWERED body against current evidence IDs only."""
    if not isinstance(answer, str) or not answer.strip():
        return failure(raw_draft, ('answered body must be nonempty',))
    errors = citation_errors(answer, source_ids)
    if not CANONICAL_CITATION.search(answer):
        errors.append('answered body contains no source citation')
    if errors:
        return failure(raw_draft if raw_draft is not None else answer, errors)
    return ResponseText(answer.strip(), ANSWERED, raw_draft=raw_draft)


def parse_response(raw, source_ids):
    """Require exact keys/state/types; abstention bodies must be empty.

    No phrase matching, stripping of invalid citations, or factual correction.
    Reject duplicate JSON keys, extra explanations and markdown fences.
    """
    def pairs(items):
        output = {}
        for key, value in items:
            if key in output:
                raise ValueError('duplicate envelope key')
            output[key] = value
        return output
    try:
        envelope = json.loads(raw, object_pairs_hook=pairs)
    except (ValueError, TypeError):
        return failure(raw, ('invalid JSON envelope',))
    if (not isinstance(envelope, dict) or set(envelope) != {'state', 'answer'}
            or not isinstance(envelope['state'], str) or not isinstance(envelope['answer'], str)):
        return failure(raw, ('invalid envelope shape or field types',))
    state, answer = envelope['state'], envelope['answer']
    if state == ANSWERED:
        return answered_response(answer, source_ids, raw)
    if state not in (INSUFFICIENT_EVIDENCE, VALIDATION_FAILED) or answer != '':
        return failure(raw, ('invalid state or nonempty abstention/failure body',))
    if state == INSUFFICIENT_EVIDENCE:
        return ResponseText(INSUFFICIENT_EVIDENCE_MESSAGE, state, raw_draft=raw)
    return failure(raw, ('model declared validation failure',))
