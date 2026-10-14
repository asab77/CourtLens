"""Benchmark-only accounting. No clients or requests are created by this module."""
from copy import deepcopy
from dataclasses import asdict, replace
from decimal import Decimal
import json
import os
from pathlib import Path

import citation_verifier_evaluation as h
import llm_citation_verifier as v

PREFLIGHT_LEDGER_SHA = '1ed282e2ec930488e9892e28537503a624661ed528e4968b1326f1d330d889a5'
PROMPT_SHA = 'f9b9160cd8c6f168a06d00c10dec680f4f3333ad83cdaf9f245f57b6be3cdfaa'

def money(value):
    if isinstance(value, bool): raise ValueError('Invalid financial value')
    result = Decimal(str(value))
    if not result.is_finite() or result < 0: raise ValueError('Invalid financial value')
    return result

def cost(inp, out):
    return (Decimal(inp) * Decimal('.40') + Decimal(out) * Decimal('1.60')) / Decimal(1000000)

def load_preflight(directory):
    if v.MODEL!='openai/gpt-4.1-mini' or v.VERCEL_BASE_URL!='https://ai-gateway.vercel.sh/v1':
        raise ValueError('Fixed verifier provider configuration changed')
    directory = Path(directory)
    manifest = json.loads((directory / 'manifest.json').read_text())
    if manifest['benchmark_sha256'] != h.BENCHMARK_SHA256 or manifest['prompt_sha256'] != PROMPT_SHA:
        raise ValueError('Preflight manifest identity mismatch')
    required = {'request_ledger.json', 'configuration.json', 'results.json', 'predictions.json', 'raw_responses.json', 'inputs.json', 'system_prompt.txt'}
    if not required <= manifest['files_sha256'].keys(): raise ValueError('Incomplete preflight manifest')
    for name, digest in manifest['files_sha256'].items():
        if Path(name).name != name or h.sha((directory/name).read_bytes()) != digest:
            raise ValueError('Preflight integrity failure')
    if h.sha((directory/'request_ledger.json').read_bytes()) != PREFLIGHT_LEDGER_SHA:
        raise ValueError('Unrecognized historical ledger')
    if h.sha((directory/'system_prompt.txt').read_bytes()) != PROMPT_SHA or v.PROMPT_SHA256 != PROMPT_SHA:
        raise ValueError('Prompt mismatch')
    config = json.loads((directory/'configuration.json').read_text())
    expected = {'model': v.MODEL, 'base_url': v.VERCEL_BASE_URL, 'temperature': 0,
                'sdk_max_retries': 0, 'automatic_model_fallback': False,
                'prompt_sha256': PROMPT_SHA, 'benchmark_sha256': h.BENCHMARK_SHA256}
    if any(config.get(k) != val for k,val in expected.items()): raise ValueError('Preflight configuration mismatch')
    if config['limits'] != asdict(v.RequestLimits(3,512,.10)): raise ValueError('Preflight limit mismatch')
    if money(config['pricing']['input_per_million']) != Decimal('.40') or money(config['pricing']['output_per_million']) != Decimal('1.60'):
        raise ValueError('Pricing mismatch')
    ledger = json.loads((directory/'request_ledger.json').read_text())
    records = ledger['records']
    results = json.loads((directory/'results.json').read_text())
    predictions = json.loads((directory/'predictions.json').read_text())
    raw = json.loads((directory/'raw_responses.json').read_text())
    inputs = json.loads((directory/'inputs.json').read_text())
    if len(records)!=3 or [r['request_number'] for r in records]!=[1,2,3]: raise ValueError('Invalid prior request IDs')
    if ledger['stopped'] or ledger['scope']!='preflight_only' or ledger['limits']!=config['limits']: raise ValueError('Invalid prior ledger')
    if len(raw)!=3 or len(predictions)!=3 or len(inputs)!=3 or results['results']!=predictions:
        raise ValueError('Incomplete prior results')
    for i,r in enumerate(records):
        result = predictions[i]['result']; usage = r['usage']
        if r['kind']!='preflight' or r['status']!='VALID_PREDICTION' or r['error_class'] is not None:
            raise ValueError('Incomplete or failed preflight')
        if inputs[i]['id']!=predictions[i]['id'] or raw[i]['id']!=predictions[i]['id'] or raw[i]['returned_model']!=v.MODEL:
            raise ValueError('Prior response identity mismatch')
        if raw[i]['finish_reason']!='stop' or raw[i]['usage']!=usage or result['execution_status']!=r['status']:
            raise ValueError('Prior response mismatch')
        parsed=v.parse_output(raw[i]['content'])
        if parsed.execution_status!='VALID_PREDICTION' or parsed.predicted_label!=result['predicted_label'] or parsed.rationale!=result['rationale']:
            raise ValueError('Prior response schema mismatch')
        if any(type(usage[k]) is not int or usage[k]<0 for k in ('input_tokens','output_tokens')):
            raise ValueError('Invalid prior usage')
        if result['token_usage']!={'input':usage['input_tokens'],'output':usage['output_tokens']}:
            raise ValueError('Prior usage mismatch')
        if money(r['accounted_cost_usd'])!=money(usage['reported_cost_usd']) or money(result['cost_usd'])!=money(r['accounted_cost_usd']) or r['accounting_method']!='provider_reported':
            raise ValueError('Prior cost mismatch')
        estimate=v.token_estimate(v.build_messages(**inputs[i]['input']))['reserved_input_tokens']
        if r['reserved_input_tokens']!=estimate or r['max_output_tokens']!=512 or money(r['reserved_cost_usd'])!=money(v.Pricing().cost(estimate,512)):
            raise ValueError('Prior reservation mismatch')
    total=sum((money(r['accounted_cost_usd']) for r in records),Decimal(0))
    if total!=Decimal('.000818') or money(ledger['accounted_cost_usd'])!=total or money(results['accounted_cost_usd'])!=total:
        raise ValueError('Historical total mismatch')
    for key,val in {'attempted_requests':3,'provider_responses_received':3,'valid_schema_responses':3,'provider_errors':0,'benchmark_requests':0,'input_tokens':1577,'output_tokens':117}.items():
        if results[key]!=val: raise ValueError('Historical aggregate mismatch')
    if results['checksums']!={'benchmark_sha256':h.BENCHMARK_SHA256,'prompt_sha256':PROMPT_SHA}:
        raise ValueError('Historical result identity mismatch')
    return {'records':deepcopy(records),'cost':total,'ledger_sha256':PREFLIGHT_LEDGER_SHA}


def atomic_event(directory, number, envelope):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    parent_fd=os.open(directory.parent,os.O_RDONLY)
    try:os.fsync(parent_fd)
    finally:os.close(parent_fd)
    target=directory/f'{number:04d}.json';temp=directory/f'{number:04d}.tmp'
    h.reject_credentials(envelope)
    with temp.open('x',encoding='utf-8') as f:
        f.write(h.serialize(envelope));f.flush();os.fsync(f.fileno())
    # Hard link is atomic and refuses replacement of any previous event.
    os.link(temp,target);temp.unlink()
    fd=os.open(directory,os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)


class CumulativeBudget:
    def __init__(self, prior, benchmark, journal=None):
        self.prior=prior;self.benchmark=benchmark;self.journal=Path(journal) if journal else None
        self.limits=v.RequestLimits(35,512,.10);self.pricing=v.Pricing()
        self.records=deepcopy(prior['records']);self.charged_estimate=prior['cost'];self.stopped=False
        self.current_example=None;self.last_hash=None;self.event_count=0
        if self.journal and self.journal.exists(): self._restore()

    @property
    def new_records(self): return self.records[3:]

    def _body(self):
        return {'preflight_ledger_sha256':self.prior['ledger_sha256'],'benchmark_sha256':h.BENCHMARK_SHA256,
                'prompt_sha256':PROMPT_SHA,'limits':asdict(self.limits),'records':self.records,
                'charged_estimate_usd':str(self.charged_estimate),'stopped':self.stopped}

    def _persist(self):
        if self.journal:
            body=self._body();envelope={'previous_sha256':self.last_hash,'body':body,'body_sha256':h.sha(h.serialize(body).encode())}
            atomic_event(self.journal,self.event_count+1,envelope)
            self.last_hash=h.sha(h.serialize(envelope).encode());self.event_count+=1

    def _validate(self, body):
        if body['preflight_ledger_sha256']!=self.prior['ledger_sha256'] or body['benchmark_sha256']!=h.BENCHMARK_SHA256 or body['prompt_sha256']!=PROMPT_SHA or body['limits']!=asdict(self.limits):
            raise ValueError('Journal identity mismatch')
        records=body['records']
        if records[:3]!=self.prior['records'] or len(records)>35: raise ValueError('Historical accounting changed')
        total=self.prior['cost']
        for i,r in enumerate(records[3:]):
            if set(r)!={'request_number','example_id','kind','status','reserved_input_tokens','max_output_tokens','reserved_cost_usd','accounted_cost_usd','accounting_method','usage','error_class','result'}:
                raise ValueError('Invalid reservation fields')
            example=self.benchmark['claim_examples'][i]
            estimate=v.token_estimate(v.build_messages(**h.verifier_input(example)))['reserved_input_tokens']
            reservation=cost(estimate,512)
            if type(r['request_number']) is not int or type(r['reserved_input_tokens']) is not int or r['request_number']!=i+4 or r['example_id']!=example['example_id'] or r['kind']!='benchmark' or r['reserved_input_tokens']!=estimate or r['max_output_tokens']!=512 or money(r['reserved_cost_usd'])!=reservation:
                raise ValueError('Conflicting reservation')
            if r['status']=='dispatching':
                if r['result'] is not None or r['usage'] is not None: raise ValueError('Conflicting uncertain request')
                accounted=reservation
                if r['accounting_method']!='conservative_reservation' or r['error_class'] is not None:raise ValueError('Invalid pending accounting')
            else:
                result=r['result']
                if not isinstance(result,dict) or result['execution_status']!=r['status']:
                    raise ValueError('Missing completed result')
                obj=h.VerificationResult(**result)
                if h.result_problem(obj,{'name':'GPT41MiniCitationVerifier','version':'1.0'}):raise ValueError('Invalid stored result')
                usage=r['usage']
                if usage is None:
                    accounted=reservation
                    if obj.token_usage is not None or obj.cost_usd is not None or r['accounting_method']!='conservative_reservation':raise ValueError('Unknown usage conflict')
                else:
                    if any(type(usage[k]) is not int or usage[k]<0 for k in ('input_tokens','output_tokens')):raise ValueError('Invalid journal usage')
                    accounted=money(usage['reported_cost_usd']) if usage['reported_cost_usd'] is not None else cost(usage['input_tokens'],usage['output_tokens'])
                    if obj.token_usage!={'input':usage['input_tokens'],'output':usage['output_tokens']} or money(obj.cost_usd)!=accounted:raise ValueError('Result usage mismatch')
                    method='provider_reported' if usage['reported_cost_usd'] is not None else 'actual_usage_at_recorded_prices'
                    if r['accounting_method']!=method:raise ValueError('Accounting method mismatch')
            if money(r['accounted_cost_usd'])!=accounted:raise ValueError('Journal cost mismatch')
            total+=accounted
        if money(body['charged_estimate_usd'])!=total or type(body['stopped']) is not bool:raise ValueError('Journal total mismatch')
        if total>Decimal('.10') and not body['stopped']:raise ValueError('Unstopped overspend')

    def _restore(self):
        if list(self.journal.glob('*.tmp')):raise ValueError('Incomplete journal write; manual review required')
        files=sorted(self.journal.glob('*.json'));previous=None
        for number,path in enumerate(files,1):
            if path.name!=f'{number:04d}.json':raise ValueError('Missing journal event')
            envelope=json.loads(path.read_text());body=envelope['body']
            if envelope['previous_sha256']!=self.last_hash or envelope['body_sha256']!=h.sha(h.serialize(body).encode()):raise ValueError('Journal hash conflict')
            self._validate(body)
            old=self.records;new=body['records']
            # Only one new reservation or completion of the final reservation may change.
            if len(new)==len(old)+1:
                if new[:-1]!=old or new[-1]['status']!='dispatching':raise ValueError('Invalid reservation transition')
                if self.stopped or self.charged_estimate+money(new[-1]['reserved_cost_usd'])>Decimal('.10'):raise ValueError('Unpermitted historical dispatch')
            elif len(new)==len(old):
                if not old[3:] or old[-1]['status']!='dispatching' or new[:-1]!=old[:-1] or new[-1]['status']=='dispatching':raise ValueError('Invalid completion transition')
                for key in ('request_number','example_id','kind','reserved_input_tokens','max_output_tokens','reserved_cost_usd'):
                    if new[-1][key]!=old[-1][key]:raise ValueError('Changed reservation')
            else:raise ValueError('Journal counters reset')
            self.records=new;self.charged_estimate=money(body['charged_estimate_usd']);self.stopped=body['stopped']
            self.last_hash=h.sha(path.read_bytes());self.event_count=number
        if self.journal.exists() and not files:raise ValueError('Empty existing journal')

    def reserve(self,input_tokens,kind):
        if kind!='benchmark':raise ValueError('Benchmark-only budget forbids preflight')
        if self.stopped or len(self.records)>=35 or len(self.new_records)>=32:raise v.RequestLimitReached('Cumulative request limit reached')
        example=self.benchmark['claim_examples'][len(self.new_records)]
        if self.current_example!=example['example_id']:raise ValueError('Duplicate or out-of-order example')
        expected=v.token_estimate(v.build_messages(**h.verifier_input(example)))['reserved_input_tokens']
        if input_tokens!=expected or input_tokens>8192:raise ValueError('Input reservation mismatch')
        reservation=cost(input_tokens,512)
        if self.charged_estimate+reservation>Decimal('.10'):raise v.RequestLimitReached('Cumulative cost limit reached')
        row={'request_number':len(self.records)+1,'example_id':self.current_example,'kind':'benchmark','status':'dispatching','reserved_input_tokens':input_tokens,'max_output_tokens':512,'reserved_cost_usd':str(reservation),'accounted_cost_usd':str(reservation),'accounting_method':'conservative_reservation','usage':None,'error_class':None,'result':None}
        self.records.append(row);self.charged_estimate+=reservation;self._persist();return row

    def finish(self,row,usage,status,error_class=None,result=None):
        if row is not self.records[-1] or row['status']!='dispatching' or result is None:raise ValueError('Conflicting completion')
        accounted=money(row['reserved_cost_usd'])
        method='conservative_reservation'
        if usage is not None:
            accounted=money(usage['reported_cost_usd']) if usage.get('reported_cost_usd') is not None else cost(usage['input_tokens'],usage['output_tokens'])
            method='provider_reported' if usage.get('reported_cost_usd') is not None else 'actual_usage_at_recorded_prices'
        self.charged_estimate+=accounted-money(row['accounted_cost_usd'])
        row.update(status=status,error_class=error_class,usage=usage,accounted_cost_usd=str(accounted),accounting_method=method,result=asdict(result))
        if self.charged_estimate>Decimal('.10'):self.stopped=True
        self._persist()

    def response_cost(self,usage):
        value=money(usage['reported_cost_usd']) if usage.get('reported_cost_usd') is not None else cost(usage['input_tokens'],usage['output_tokens'])
        return float(value)  # Result schema uses JSON numbers; all budget arithmetic is Decimal.


def benchmark_dry_run(prior,benchmark,journal=None):
    budget=CumulativeBudget(prior,benchmark,journal)
    pending=benchmark['claim_examples'][len(budget.new_records):]
    projected=budget.charged_estimate+sum((cost(v.token_estimate(v.build_messages(**h.verifier_input(r)))['reserved_input_tokens'],512) for r in pending),Decimal(0))
    return {'execution':'DRY_RUN_ONLY','new_API_requests':0,'historical_preflight_requests':3,'historical_cost_usd':str(prior['cost']),
            'reserved_benchmark_requests':len(budget.new_records),'pending_benchmark_examples':len(pending),'total_planned_requests':35,
            'combined_requests_consumed':len(budget.records),'remaining_estimated_allowance_usd':str(Decimal('.10')-budget.charged_estimate),
            'cumulative_projected_cost_usd':str(projected),'benchmark_sha256':h.BENCHMARK_SHA256,'prompt_sha256':PROMPT_SHA,
            'blockers':(['Cumulative projected cost exceeds ceiling'] if projected>Decimal('.10') else [])+(['Budget stopped'] if budget.stopped else [])}


def run_benchmark_only(client, prior, benchmark, output, timestamp):
    """Called only after separate live permission; callers/tests inject the client."""
    import fcntl
    output=Path(output)
    if output.exists() and not (output/'request_journal').exists():raise ValueError('Existing output lacks accounting; manual review required')
    output.mkdir(parents=True,exist_ok=True)
    with (output/'execution.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if (output/'scored').exists() or (output/'finalization').exists():raise FileExistsError('Benchmark already finalized')
        budget=CumulativeBudget(prior,benchmark,output/'request_journal')
        verifier=v.GPT41MiniCitationVerifier(client,budget)
        predictions={}
        for record in budget.new_records:
            predictions[record['example_id']]=(h.VerificationResult(**record['result']) if record['result'] is not None
                else h.failure_result('EXECUTION_FAILURE',h.identity(verifier)))
        for example in benchmark['claim_examples'][len(budget.new_records):]:
            budget.current_example=example['example_id']
            try: result=verifier.request(**h.verifier_input(example),kind='benchmark')
            except v.RequestLimitReached:break
            predictions[example['example_id']]=result
            if budget.stopped:break
        for example in benchmark['claim_examples']:
            predictions.setdefault(example['example_id'],h.failure_result('MISSING_PREDICTION',h.identity(verifier)))
        run=h.build_run(verifier,benchmark,timestamp,predictions)
        run['execution']['mode']='benchmark_only_live'
        run['request_accounting']={'historical_preflight_requests':3,'new_benchmark_requests':len(budget.new_records),
            'combined_requests':len(budget.records),'historical_cost_usd':str(prior['cost']),
            'cumulative_accounted_cost_usd':str(budget.charged_estimate),'preflight_ledger_sha256':prior['ledger_sha256'],
            'records':budget.records,'uncertain_requests_not_retried':[r['example_id'] for r in budget.new_records if r['status']=='dispatching']}
        baseline_path=h.ROOT/'data/analysis/citation_verifiers/lexical_overlap_v1/results.json'
        baseline=json.loads(baseline_path.read_text())
        if baseline['benchmark_sha256']!=h.BENCHMARK_SHA256:raise ValueError('Baseline checksum mismatch')
        run['lexical_baseline_comparison']={'baseline_results_sha256':h.sha(baseline_path.read_bytes()),'baseline_metrics':baseline['metrics'],'llm_metrics':run['metrics']}
        # Harness refuses overwriting, so final scoring artifacts use a fresh subdirectory.
        h.write_run(run,verifier.configuration,output/'scored')
        atomic_event(output/'finalization',1,{'results':run})
        return run
