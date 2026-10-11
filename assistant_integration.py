"""Small, testable Streamlit integration helpers; no UI or global chat cache."""
import hashlib
import json
from pathlib import Path

from evidence_context import build_evidence_context, default_tokenizer, token_count
from gateway_config import (PROJECT_DIR, get_gateway_api_key, get_runtime_setting,
                            vercel_generation_config, evidence_budget_config)
from live_retrieval import retrieve_hybrid, load_live_resources
from retrieve import semantic_search
from rag import (generate_grounded_answer_from_evidence, citation_problem,
                 INSUFFICIENT_EVIDENCE_MESSAGE, SYSTEM_PROMPT, format_history)

HYBRID = 'Structure-aware hybrid'
DENSE = 'Dense only'


class AssistantError(RuntimeError):
    """Only fixed, safe public text is supplied to this exception."""


def resource_identity(asset_path):
    """Hash path-associated assets/provenance for a credential-free cache key."""
    path = Path(asset_path).resolve()
    chunk_manifest = json.loads((path.parent / 'manifest.json').read_text())
    relative = Path(chunk_manifest['source_structural_artifact'])
    source = (PROJECT_DIR / relative).resolve()
    if relative.is_absolute() or not source.is_relative_to(PROJECT_DIR.resolve()):
        raise ValueError('Invalid source artifact path')
    files = [path / n for n in ('index.faiss', 'records.jsonl', 'manifest.json')]
    files += [path.parent / 'chunks.jsonl', path.parent / 'manifest.json', source]
    return tuple(hashlib.sha256(p.read_bytes()).hexdigest() for p in files)


def initialize_resources(asset_path, identity):
    """Validate on cache misses; reject assets changing during initialization."""
    if resource_identity(asset_path) != identity:
        raise ValueError('Runtime assets changed before initialization')
    resources = load_live_resources(Path(asset_path))
    if resource_identity(asset_path) != identity:
        raise ValueError('Runtime assets changed during initialization')
    return resources


def answer_question(question, resources, model_id, history, *, strategy=HYBRID,
                    case_name=None, dense_top_k=5):
    """Retrieve -> budget -> generate -> ID validation -> session-ready message."""
    if not get_gateway_api_key():
        raise AssistantError('Configure AI_GATEWAY_API_KEY in Streamlit secrets or the environment.')
    if not get_runtime_setting('VERCEL_GENERATION_MODEL'):
        raise AssistantError('Configure VERCEL_GENERATION_MODEL with a verified Vercel chat model.')
    try:
        configuration = vercel_generation_config()
        if configuration.model != model_id:
            raise ValueError('Generation model mismatch')
    except Exception:
        raise AssistantError('CourtLens generation configuration is invalid. Check the configured model and credential.') from None
    try:
        if strategy == HYBRID:
            results = retrieve_hybrid(question, resources, case_name=case_name)
        elif strategy == DENSE:
            results = semantic_search(question, top_k=dense_top_k, case_name=case_name,
                                      vector_store=resources.vector_store)
        else:
            raise ValueError('Unknown retrieval strategy')
    except Exception:
        raise AssistantError('Evidence retrieval failed. Check the gateway connection and selected case; no alternate retrieval strategy was used.') from None
    try:
        budget, margin = evidence_budget_config()
        context = build_evidence_context(results, budget, safety_margin=margin)
        encoding = default_tokenizer()
        expected_answer = int(get_runtime_setting('COURTLENS_EXPECTED_ANSWER_TOKENS') or '1024')
        if expected_answer < 1:
            raise ValueError('Invalid answer allowance')
        prompt_accounting = {
            'system_tokens': token_count(SYSTEM_PROMPT, encoding),
            'history_tokens': token_count(format_history(history), encoding),
            'question_tokens': token_count(question, encoding),
            'evidence_tokens': context.usage['evidence_tokens'],
            'expected_answer_tokens': expected_answer,
            'answer_allowance_is_planning_only': True,
            'total_model_capacity_known': False,
            'note': 'Component estimates exclude message framing; capacity is not guaranteed. Answer allowance is not an API output limit.',
        }
    except Exception:
        raise AssistantError('Could not prepare bounded evidence. Check the evidence budget and verified local tokenizer vocabulary.') from None
    if context.status == 'insufficient_context':
        answer = INSUFFICIENT_EVIDENCE_MESSAGE
    else:
        try:
            answer = generate_grounded_answer_from_evidence(question, context, model_id,
                                                           conversation_history=history)
            if citation_problem(answer, len(context.evidence)):
                raise ValueError('Invalid citation identifiers')
        except Exception:
            raise AssistantError('Answer generation failed or returned invalid source citations. Check the gateway and configured model.') from None
    return {'role': 'assistant', 'content': answer, 'evidence': context.evidence,
            'source_mapping': context.sources, 'context_usage': context.usage,
            'skipped_evidence': context.skipped, 'context_status': context.status,
            'prompt_accounting': prompt_accounting, 'retrieval_strategy': strategy,
            'model_name': model_id}
