"""Explicit, one-shot Phase 7A.3 live smoke runner; never invoked by tests.

Only this runner injects output/budget limits. It calls the production Assistant
helpers, records before dispatch, disables SDK retries, and aborts on provider
failure. Re-execution is refused when its ledger exists. No document embedding.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import assistant_integration as assistant
import live_retrieval as live
import rag
from evidence_context import default_tokenizer, token_count
from gateway_config import vercel_generation_config, vercel_embedding_config, PROJECT_DIR

QUESTIONS = [
    ('A', 'What safeguards did the Supreme Court require before custodial interrogation in Miranda v. Arizona?'),
    ('B', 'How did the majority in Obergefell v. Hodges connect the Due Process Clause and Equal Protection Clause?'),
    ('C', "What did the Supreme Court decide in Dobbs v. Jackson Women's Health Organization?"),
]
OUTPUT = PROJECT_DIR / 'data/analysis/phase7a3_smoke_test.json'
REPORT = OUTPUT.with_suffix('.md')
PRICING = {'checked_date': '2026-10-11', 'generation_input_usd_per_million': .40,
           'generation_output_usd_per_million': 1.60, 'embedding_input_usd_per_million': .02,
           'sources': ['https://vercel.com/ai-gateway/models/gpt-4.1-mini',
                       'https://vercel.com/ai-gateway/models/text-embedding-3-small'],
           'maximum_expected_usd': .011206,
           'assumptions': '4 generation calls at approximately <=5000 input + 500 output tokens each; 3 queries <=300 embedding tokens total. Includes framing/correction allowance. Estimate, not a spending cap; no cache discount assumed.'}


class SmokeAbort(RuntimeError):
    pass


class CappedCalls:
    """Pre-dispatch caps count attempts, including failures and corrections."""
    def __init__(self, client, document, save):
        self.client, self.document, self.save = client, document, save
        self.failed = False
        self.embeddings = SimpleNamespace(create=lambda **kw: self.call('embedding', **kw))
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=lambda **kw: self.call('generation', **kw)))

    def call(self, kind, **kwargs):
        if self.failed:
            raise SmokeAbort('Previous provider failure: no further dispatch')
        cap = {'embedding': 3, 'generation': 4}[kind]
        calls = self.document['requests']
        if sum(row['kind'] == kind for row in calls) >= cap:
            raise SmokeAbort('Authorized request cap exhausted')
        if kind == 'embedding':
            if kwargs.get('model') != 'openai/text-embedding-3-small' or kwargs.get('input') not in [[q] for _, q in QUESTIONS]:
                raise SmokeAbort('Only the three authorized query embeddings are allowed')
            dispatch = self.client.embeddings.create
        else:
            if kwargs.get('model') != 'openai/gpt-4.1-mini':
                raise SmokeAbort('Generation model mismatch')
            kwargs['max_tokens'] = 500
            dispatch = self.client.chat.completions.create
        row = {'kind': kind, 'case_id': self.document.get('active_case'), 'status': 'dispatching',
               'model': kwargs['model']}
        if kind == 'generation':
            row.update(messages=deepcopy(kwargs['messages']), max_tokens=500)
        calls.append(row)
        self.save()
        try:
            response = dispatch(**kwargs)
        except Exception as exc:
            self.failed = True
            row.update(status='failed', error_type=type(exc).__name__)
            self.save()
            # Do not expose provider response bodies or enter production 429 retries.
            raise SmokeAbort('Provider request failed; smoke test stopped') from None
        row['status'] = 'succeeded'
        usage = response.usage
        row['usage'] = usage.model_dump() if usage is not None else None
        if kind == 'generation':
            row['finish_reason'] = response.choices[0].finish_reason
            row['answer'] = response.choices[0].message.content
        self.save()
        return response


def write_report(document):
    lines = ['# CourtLens Phase 7A.3 controlled smoke test', '',
             'Production Assistant helpers were exercised headlessly; browser interaction was not part of this live run.', '',
             'Citation checks validate ID syntax/membership only. Manual observations below do not implement semantic verification.', '',
             '## Configuration and accounting', '', '```json',
             json.dumps({k: document[k] for k in ('configuration', 'pricing', 'totals', 'verification') if k in document}, indent=2), '```', '',
             'Pricing sources: ' + ', '.join(f'[{u}]({u})' for u in PRICING['sources']), '']
    lines += ['## Outcome', '', document.get('readiness', 'Pending manual assessment.'), '', document.get('assessment_summary', ''), '']
    for case in document['cases']:
        lines += [f"## Test {case['id']}", '', case['question'], '',
                  '### Answer', '', case.get('result', {}).get('content', 'No successful answer.'), '',
                  '### Manual grounding observations', '', case.get('manual_grounding', 'Pending manual inspection.'), '',
                  '### Retrieval and context accounting', '', '```json',
                  json.dumps({k: v for k, v in case.items() if k not in ('exact_evidence', 'result', 'manual_grounding')}, indent=2, ensure_ascii=False), '```', '',
                  '### Source mapping and evidence usage', '', '```json',
                  json.dumps({k: v for k, v in case.get('result', {}).items() if k not in ('content', 'evidence')}, indent=2, ensure_ascii=False), '```', '',
                  '### Exact evidence sent to generation', '', '```text', case.get('exact_evidence', ''), '```', '']
    lines += ['## Request ledger (including correction drafts)', '', '```json',
              json.dumps([{k: v for k, v in row.items() if k != 'messages'} for row in document['requests']], indent=2), '```', '',
              'Full exact request messages are preserved in the JSON. No credential or request headers are recorded.', '',
              '## Limitations', '', document.get('limitations', 'Three questions only; no retrieval metrics or benchmark labels changed. Pricing estimates are not provider invoices.'), '']
    REPORT.write_text('\n'.join(lines))


def summarize(document):
    totals = {'embedding_calls': 0, 'generation_calls': 0, 'embedding_input_tokens': 0,
              'generation_input_tokens': 0, 'generation_output_tokens': 0}
    for row in document['requests']:
        totals[row['kind'] + '_calls'] += 1
        usage = row.get('usage') or {}
        if row['kind'] == 'embedding':
            totals['embedding_input_tokens'] += usage.get('total_tokens', 0)
        else:
            totals['generation_input_tokens'] += usage.get('prompt_tokens', 0)
            totals['generation_output_tokens'] += usage.get('completion_tokens', 0)
    totals['estimated_usage_cost_usd_without_cache_discount'] = (
        totals['embedding_input_tokens'] * .02 + totals['generation_input_tokens'] * .40 + totals['generation_output_tokens'] * 1.60) / 1_000_000
    costs = [row['usage']['cost'] for row in document['requests'] if row.get('usage') and isinstance(row['usage'].get('cost'), (int, float))]
    totals['provider_reported_cost_usd'] = sum(costs) if costs else None
    totals['requests_with_provider_reported_cost'] = len(costs)
    totals['provider_cost_note'] = 'Reported cost covers only responses exposing usage.cost; embedding cost is estimated separately. Token totals include citation-correction drafts.'
    document['totals'] = totals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', help='Dispatch the explicitly authorized live requests once')
    args = parser.parse_args()
    generation, embedding = vercel_generation_config(), vercel_embedding_config()
    assert generation.model == 'openai/gpt-4.1-mini'
    assert embedding.model == 'openai/text-embedding-3-small'
    assert generation.base_url == embedding.base_url == 'https://ai-gateway.vercel.sh/v1'
    resources = live.load_live_resources()
    default_tokenizer()  # Verify local vocabulary before any request.
    if not args.run:
        print('Preflight passed. No provider requests dispatched.')
        return
    if OUTPUT.exists() or REPORT.exists():
        raise SmokeAbort('Existing smoke ledger/report: refusing automatic re-execution')
    protected = {str(p.relative_to(PROJECT_DIR)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in (PROJECT_DIR / 'data').rglob('*') if p.is_file()}
    document = {'started_at': datetime.now(timezone.utc).isoformat(),
                'configuration': {'generation_model': generation.model, 'embedding_model': embedding.model,
                                  'base_url': generation.base_url, 'sdk_max_retries': 0,
                                  'evidence_budget': 4000, 'safety_margin': .10, 'effective_evidence_budget': 3600,
                                  'max_output_tokens': 500, 'dense_top_k': 5, 'bm25_top_k': 5,
                                  'rrf_k': 60, 'final_top_k': 5, 'vectors': resources.vector_store[0].ntotal},
                'pricing': PRICING, 'requests': [], 'cases': [], 'protected_sha256_before': protected}
    def save():
        summarize(document)
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n')
    from openai import OpenAI
    with OpenAI(api_key=generation.api_key, base_url=generation.base_url, max_retries=0, timeout=60) as actual:
        capped = CappedCalls(actual, document, save)
        original_retrieve, original_fuse = live.retrieve_hybrid, live.fuse
        original_generate = rag.generate_grounded_answer_from_evidence
        for case_id, question in QUESTIONS:
            document['active_case'] = case_id
            case = {'id': case_id, 'question': question}
            document['cases'].append(case)
            def capture_fuse(catalog, dense, lexical):
                case['dense_top5'] = deepcopy(dense)
                case['bm25_top5'] = [dict(row, text=resources.catalog.records[row['corpus_index']]['text']) for row in deepcopy(lexical)]
                fused = original_fuse(catalog, dense, lexical)
                case['fused_top5'] = deepcopy(fused[:5])
                return fused
            def capture_retrieve(*a, **kw):
                return original_retrieve(*a, **kw, client=capped)
            def capture_generate(q, context, *a, **kw):
                case['exact_evidence'] = context.text
                case['context_usage'] = context.usage
                return original_generate(q, context, *a, **kw)
            try:
                with patch.object(live, 'fuse', capture_fuse), patch.object(assistant, 'retrieve_hybrid', capture_retrieve), \
                        patch.object(assistant, 'evidence_budget_config', return_value=(4000, .10)), \
                        patch.object(assistant, 'generate_grounded_answer_from_evidence', capture_generate), \
                        patch.object(rag, 'vercel_client', return_value=capped):
                    case['result'] = assistant.answer_question(question, resources, generation.model, [])
                case['citation_problem'] = rag.citation_problem(case['result']['content'], len(case['result']['evidence']))
                case['exact_context_passed'] = all(row['messages'][1]['content'].endswith(case['exact_evidence'])
                                                   for row in document['requests'] if row['kind'] == 'generation' and row['case_id'] == case_id)
                case['status'] = 'succeeded'
                print(f'Test {case_id} completed.', flush=True)
            except Exception as exc:
                case.update(status='failed', error_type=type(exc).__name__)
                print(f'Test {case_id} failed; stopping without further requests.', flush=True)
                break
            finally:
                save()
    changed = [name for name, digest in protected.items()
               if not (PROJECT_DIR / name).is_file() or hashlib.sha256((PROJECT_DIR / name).read_bytes()).hexdigest() != digest]
    document['verification'] = {'protected_existing_data_files': len(protected), 'changed': changed,
                                'indexes_rebuilt': False, 'benchmark_labels_changed': False}
    save()
    write_report(document)
    print(json.dumps(document['totals']))


if __name__ == '__main__':
    main()
