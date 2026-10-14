"""Dry-run preparation by default; --live reserved for subsequent authorization.

Do not use --live during Phase 7B.2B.2 implementation/offline validation.
"""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path

import citation_verifier_evaluation as harness
from llm_citation_verifier import (MODEL,SYSTEM_PROMPT,PROMPT_SHA256,PROMPT_VERSION,RequestLimits,
    Pricing,RequestBudget,RequestLimitReached,GPT41MiniCitationVerifier,make_client,build_messages,token_estimate)

DEFAULT_OUTPUT=harness.ROOT/'data/analysis/citation_verifiers/gpt41mini_v1'
PREFLIGHT_METADATA={'citation_identifier':'S1','case_name':'Contract fixture','opinion_type':'unknown','author':None,
                    'pdf_page_range':[1,1],'source_file':'contract_fixture.txt','attribution_is_raw':True}
PREFLIGHT_INPUTS=[{'claim':claim,'evidence':evidence,'citation_metadata':PREFLIGHT_METADATA} for claim,evidence in [
    ('The fictional hearing occurred on Monday.','The fictional hearing occurred on Monday.'),
    ('The fictional hearing occurred on Tuesday.','The fictional hearing occurred on Monday.'),
    ('The fictional hearing was recorded.','The fictional hearing occurred on Monday.')]]


def dry_run(benchmark,limits):
    inputs=[]
    for row in benchmark['claim_examples']:
        payload=harness.verifier_input(row);messages=build_messages(**payload);estimate=token_estimate(messages)
        assert json.loads(messages[1]['content'])==payload
        inputs.append({'example_id':row['example_id'],'input':payload,'input_sha256':harness.sha(harness.serialize(payload).encode()),
                       'evidence_tokens_cl100k_base':len(harness_tokenizer().encode(payload['evidence'],disallowed_special=())),**estimate})
    preflight=[token_estimate(build_messages(**p)) for p in PREFLIGHT_INPUTS]
    pricing=Pricing();reserved_input=sum(r['reserved_input_tokens'] for r in inputs+preflight)
    maximum_cost=pricing.cost(reserved_input,35*limits.max_output_tokens)
    blockers=[]
    if any(r['reserved_input_tokens']>limits.input_budget_tokens for r in inputs+preflight):blockers.append('Complete passage exceeds selected input budget')
    if limits.max_requests<35:blockers.append('Request cap is below intended 32 benchmark + 3 preflight calls')
    if maximum_cost>limits.estimated_cost_ceiling:blockers.append('Maximum estimated planned cost exceeds ceiling')
    return {'phase':'7B.2B.2','execution':'DRY_RUN_ONLY','provider_requests_made':0,
            'benchmark_version':benchmark['benchmark_version'],'benchmark_sha256':harness.BENCHMARK_SHA256,
            'model':MODEL,'prompt_version':PROMPT_VERSION,'prompt_sha256':PROMPT_SHA256,
            'generation_parameters':{'temperature':0,'max_tokens':limits.max_output_tokens,'response_format':None},
            'limits':asdict(limits),'pricing':vars(pricing),
            'pricing_note':'Locally recorded Vercel rates verified 2026-10-11; not refreshed online in this offline phase. Confirm before live authorization.',
            'capability_note':'Ordinary Chat Completions/max_tokens worked in Phase 7A.3. Installed SDK accepts temperature/max_tokens. Temperature=0 gateway behavior requires authorized contract preflight; no structured-output mode assumed.',
            'runtime_environment':harness.environment(),'inputs':inputs,'preflight_token_estimates':preflight,
            'claim_examples':32,'answer_examples_excluded':6,'preflight_calls_planned':3,'benchmark_calls_planned':32,
            'total_reserved_input_tokens':reserved_input,'total_output_token_cap':35*limits.max_output_tokens,
            'max_evidence_tokens_cl100k_base':max(r['evidence_tokens_cl100k_base'] for r in inputs),
            'max_reserved_input_tokens':max(r['reserved_input_tokens'] for r in inputs),
            'maximum_estimated_cost_usd':maximum_cost,'cost_is_provider_enforced':False,
            'blockers':blockers,'evidence_truncated':False,'live_authorization_required':True}


def harness_tokenizer():
    from evidence_context import default_tokenizer
    return default_tokenizer()


def prepare(report,output):
    output=Path(output)
    files={'dry_run.json':harness.serialize(report),'system_prompt.txt':SYSTEM_PROMPT,
           'configuration.json':harness.serialize({k:report[k] for k in ['model','prompt_version','prompt_sha256','generation_parameters','limits','pricing','pricing_note','capability_note']})}
    files['preparation_manifest.json']=harness.serialize({'files_sha256':{n:harness.sha(t.encode()) for n,t in files.items()},
        'implementation_sha256':{n:harness.sha((harness.ROOT/n).read_bytes()) for n in ['llm_citation_verifier.py','run_llm_citation_verifier.py','citation_verifier_evaluation.py']}})
    harness.reject_credentials(files);output.parent.mkdir(parents=True,exist_ok=True);output.mkdir(exist_ok=False)
    for name,text in files.items():(output/name).write_text(text)


def run_authorized(client,benchmark,limits,output,timestamp):
    """Future explicitly authorized execution; tests inject fake clients only."""
    output=Path(output)
    if output.exists():raise FileExistsError('Refusing to overwrite prior live execution')
    ledger=output.parent/(output.name+'_request_ledger.json')
    output.parent.mkdir(parents=True,exist_ok=True)
    with ledger.open('x') as file:file.write('{}\n')
    budget=RequestBudget(limits)
    def checkpoint():
        ledger.write_text(harness.serialize({'benchmark_sha256':harness.BENCHMARK_SHA256,
            'limits':asdict(limits),'records':budget.records,'charged_estimate_usd':budget.charged_estimate,
            'stopped':budget.stopped,'never_auto_resume':True}))
    budget.checkpoint=checkpoint;checkpoint()
    verifier=GPT41MiniCitationVerifier(client,budget);who=harness.identity(verifier)
    preflight=[];predictions={};stop_reason=None
    for payload in PREFLIGHT_INPUTS:
        try:result=verifier.request(**payload,kind='preflight')
        except RequestLimitReached:stop_reason='request_or_cost_limit';break
        preflight.append(asdict(result))
        if result.execution_status!='VALID_PREDICTION' or budget.stopped:stop_reason='preflight_failure_or_cost_limit';break
    if stop_reason is None:
        for row in benchmark['claim_examples']:
            try:result=verifier.verify(**harness.verifier_input(row))
            except RequestLimitReached:stop_reason='request_or_cost_limit';break
            predictions[row['example_id']]=result
            if budget.stopped:stop_reason='cost_limit_after_reconciliation';break
            if result.execution_status in ('PROVIDER_ERROR','TIMEOUT','EXECUTION_FAILURE'):
                stop_reason='provider_execution_failure';break
    # Stop dispatch immediately; explicit missing records preserve full metric denominator.
    for row in benchmark['claim_examples']:
        if row['example_id'] not in predictions:predictions[row['example_id']]=harness.failure_result('MISSING_PREDICTION',who)
    run=harness.build_run(verifier,benchmark,timestamp,predictions)
    run['execution']['mode']='llm_experimental'
    run['request_accounting']={'records':budget.records,'attempted_requests':len(budget.records),
        'completed_requests':sum(r['status']!='dispatching' for r in budget.records),'accounted_cost_usd':budget.charged_estimate,
        'estimated_cost_ceiling_usd':limits.estimated_cost_ceiling,'provider_enforced_spending_cap':False,'stop_reason':stop_reason,
        'durable_request_ledger':ledger.name}
    run['preflight_contract_results']=preflight
    run['limitations']=[v for v in run['limitations'] if not v.startswith('The lexical baseline') and not v.startswith('No provider implementation')]
    run['limitations']+=['Temperature=0 is not a guarantee of deterministic provider inference.',
        'Costs use provider-reported values or actual usage at recorded prices; unknown costs retain conservative reservations. Client estimates are not billing caps.']
    baseline_path=harness.ROOT/'data/analysis/citation_verifiers/lexical_overlap_v1/results.json'
    baseline=json.loads(baseline_path.read_text())
    if baseline['benchmark_sha256']!=harness.BENCHMARK_SHA256:raise ValueError('Baseline checksum mismatch')
    run['lexical_baseline_comparison']={'baseline_results_sha256':harness.sha(baseline_path.read_bytes()),
        'baseline_metrics':baseline['metrics'],'llm_metrics':run['metrics'],'note':'Same frozen claims and scoring definitions; inspect coverage and failures.'}
    harness.write_run(run,verifier.configuration,output)
    (output/'system_prompt.txt').write_text(SYSTEM_PROMPT)
    (output/'comparison.json').write_text(harness.serialize(run['lexical_baseline_comparison']))
    # Supplemental manifest; do not replace harness manifest/checksums.
    (output/'llm_manifest.json').write_text(harness.serialize({'prompt_sha256':PROMPT_SHA256,
        'supplemental_sha256':{n:harness.sha((output/n).read_bytes()) for n in ['system_prompt.txt','comparison.json']}}))
    return run


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=DEFAULT_OUTPUT)
    parser.add_argument('--max-requests',type=int,required=True)
    parser.add_argument('--max-output-tokens',type=int,required=True)
    parser.add_argument('--estimated-cost-ceiling',type=float,required=True)
    parser.add_argument('--live',action='store_true',help='Only for a subsequently explicitly authorized paid evaluation')
    parser.add_argument('--benchmark-only',action='store_true',help='Reuse validated preflight accounting; dry-run unless --live is supplied')
    parser.add_argument('--preflight-dir',type=Path,default=DEFAULT_OUTPUT/'preflight_v1')
    args=parser.parse_args();limits=RequestLimits(args.max_requests,args.max_output_tokens,args.estimated_cost_ceiling)
    if args.benchmark_only:
        from cumulative_verifier_accounting import load_preflight, benchmark_dry_run, run_benchmark_only
        if limits!=RequestLimits(35,512,.10):raise ValueError('Cumulative limits must be 35 requests, 512 output tokens, $0.10')
        benchmark=harness.load_benchmark();prior=load_preflight(args.preflight_dir)
        report=benchmark_dry_run(prior,benchmark,args.output/'request_journal')
        if report['blockers']:raise ValueError('Benchmark-only dry-run has blockers')
        if args.live:
            with make_client() as client:run_benchmark_only(client,prior,benchmark,args.output,datetime.now(timezone.utc).isoformat())
        else:print(harness.serialize(report))
        return
    if args.live:raise ValueError('Live execution requires --benchmark-only and validated historical preflight')
    benchmark=harness.load_benchmark();report=dry_run(benchmark,limits)
    if args.live:
        saved=json.loads((args.output/'dry_run.json').read_text())
        manifest=json.loads((args.output/'preparation_manifest.json').read_text())
        for name,digest in manifest['files_sha256'].items():
            if harness.sha((args.output/name).read_bytes())!=digest:raise ValueError('Prepared artifact changed')
        for name,digest in manifest['implementation_sha256'].items():
            if harness.sha((harness.ROOT/name).read_bytes())!=digest:raise ValueError('Prepared implementation changed')
        if saved!=report or report['blockers']:raise ValueError('Prepared dry run mismatch or blockers')
        with make_client() as client:run_authorized(client,benchmark,limits,args.output/'live_run',datetime.now(timezone.utc).isoformat())
    else:
        prepare(report,args.output)
        print(harness.serialize({k:v for k,v in report.items() if k not in ('inputs','preflight_token_estimates')}))


if __name__=='__main__':main()
