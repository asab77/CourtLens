"""Provider-independent offline verifier evaluation; no runtime RAG integration.

The verifier boundary exposes no gold labels, IDs or adjudication hints. This is
an API isolation contract, not a sandbox for malicious implementations.
"""
from collections import Counter
from copy import deepcopy
from dataclasses import asdict, dataclass
import hashlib
from importlib.metadata import version, PackageNotFoundError
import json
import math
from pathlib import Path
import platform
import re
from typing import Protocol

from bm25_retrieval import tokenize, TOKENIZER_VERSION, TOKENIZER_DESCRIPTION
from finalize_citation_support_benchmark import ROOT, BENCHMARK, load_frozen

BENCHMARK_SHA256 = '2519c6563bcd21ac651e90a0151a67cbd37d6e4d50e6681c061b78884e18cffa'
LABELS = ('SUPPORTED','PARTIALLY_SUPPORTED','UNSUPPORTED','CONTRADICTED')
STATUSES = ('VALID_PREDICTION','INVALID_LABEL','INVALID_RESPONSE_SCHEMA','TIMEOUT',
            'PROVIDER_ERROR','MISSING_PREDICTION','EXECUTION_FAILURE')
ERROR_MESSAGES = {s:s.replace('_',' ').lower() for s in STATUSES if s!='VALID_PREDICTION'}


def serialize(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n'
def sha(data):return hashlib.sha256(data).hexdigest()


def load_benchmark(root=ROOT):
    """Pin actual file bytes, independent of the editable checksum sidecar."""
    try:
        raw=(root/BENCHMARK).read_bytes()
        if sha(raw)!=BENCHMARK_SHA256:raise ValueError('Frozen benchmark SHA-256 mismatch')
        benchmark=load_frozen(root)
    except FileNotFoundError:raise ValueError('Required frozen benchmark/provenance artifact is missing') from None
    if benchmark['benchmark_version']!='1.0' or benchmark['schema_version']!='1.0':
        raise ValueError('Unsupported benchmark/schema version')
    if len(benchmark['claim_examples'])!=32 or len(benchmark['answer_examples'])!=6:
        raise ValueError('Frozen benchmark example counts are invalid')
    return benchmark


def verifier_input(example):
    """Explicit allowlist; never pass the original benchmark record to verify."""
    return {'claim':example['claim'],'evidence':example['cited_evidence_text'],
            'citation_metadata':{'citation_identifier':example['citation_identifier'],
                'case_name':example['case_name'],'opinion_type':example['opinion_type'],
                'author':example['author'],'pdf_page_range':deepcopy(example['pdf_page_range']),
                'source_file':example['provenance']['source_file'],'attribution_is_raw':True}}


@dataclass(frozen=True)
class VerificationResult:
    predicted_label: str | None
    verifier_name: str
    verifier_version: str
    execution_status: str = 'VALID_PREDICTION'
    rationale: str | None = None
    error: dict | None = None
    latency_seconds: float | None = None
    token_usage: dict | None = None
    cost_usd: float | None = None


class Verifier(Protocol):
    verifier_id: str
    name: str
    version: str
    configuration: dict
    def verify(self,claim: str,evidence: str,citation_metadata: dict) -> VerificationResult: ...


class ProviderFailure(RuntimeError):
    """Future adapters may raise this; no provider client is implemented."""


class LexicalOverlapBaseline:
    """Fixed demonstration heuristic. No tuning, metadata or negation logic.

    Unique claim-word recall >= .80 -> SUPPORTED, >= .50 -> PARTIALLY_SUPPORTED,
    otherwise UNSUPPORTED. Never predicts CONTRADICTED. Thresholds were declared
    before the first benchmark evaluation; no label-based selection took place.
    """
    verifier_id='lexical-overlap'
    name='LexicalOverlapBaseline'
    version='1.0'
    def __init__(self):
        self.configuration={'supported_threshold':.80,'partial_threshold':.50,
                            'overlap':'unique_claim_tokens_intersection_evidence / unique_claim_tokens',
                            'tokenizer_version':TOKENIZER_VERSION,'tokenizer_description':TOKENIZER_DESCRIPTION,
                            'stopwords_removed':False,'negation_or_attribution_reasoning':False,
                            'uses_citation_metadata':False,'random_seed':None,
                            'threshold_selection':'fixed before evaluation; not fitted to benchmark labels'}
    def verify(self,claim,evidence,citation_metadata):
        words=set(tokenize(claim));source=set(tokenize(evidence))
        overlap=len(words & source)/len(words) if words else 0.
        label='SUPPORTED' if overlap>=.80 else 'PARTIALLY_SUPPORTED' if overlap>=.50 else 'UNSUPPORTED'
        return VerificationResult(label,self.name,self.version,rationale=f'Unique claim-word overlap: {overlap:.6f}; lexical heuristic only.')


def reject_credentials(value):
    """No credentials/config headers; reject suspected tokens without printing."""
    if isinstance(value,dict):
        for key,item in value.items():
            if re.search(r'api.?key|password|authorization|secret|access.?token|auth.?token|headers',str(key),re.I):
                raise ValueError('Credential-bearing fields are forbidden')
            reject_credentials(item)
    elif isinstance(value,(list,tuple)):
        for item in value:reject_credentials(item)
    elif isinstance(value,str) and re.search(r'github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|sk-(?:proj-)?[A-Za-z0-9_-]{25,}|vck_[A-Za-z0-9_-]{20,}|Bearer\s+\S+',value):
        raise ValueError('Credential-like content is forbidden')


def identity(verifier):
    if not isinstance(verifier.configuration,dict):raise ValueError('Verifier configuration must be a dictionary')
    result={'id':verifier.verifier_id,'name':verifier.name,'version':verifier.version}
    if any(not isinstance(v,str) or not v.strip() for v in result.values()):raise ValueError('Verifier identification is required')
    reject_credentials(result);reject_credentials(verifier.configuration)
    serialize(verifier.configuration)
    return result


def failure_result(status,who):
    return VerificationResult(None,who['name'],who['version'],status,error={'type':status,'message':ERROR_MESSAGES[status]})


def result_problem(result,who):
    if not isinstance(result,VerificationResult):return 'INVALID_RESPONSE_SCHEMA'
    if result.verifier_name!=who['name'] or result.verifier_version!=who['version']:return 'INVALID_RESPONSE_SCHEMA'
    if result.execution_status not in STATUSES:return 'INVALID_RESPONSE_SCHEMA'
    if result.execution_status=='VALID_PREDICTION':
        if result.predicted_label not in LABELS:return 'INVALID_LABEL'
        if result.error is not None:return 'INVALID_RESPONSE_SCHEMA'
    elif (result.predicted_label is not None or not isinstance(result.error,dict)
          or result.error!= {'type':result.execution_status,'message':ERROR_MESSAGES[result.execution_status]}):
        return 'INVALID_RESPONSE_SCHEMA'
    if result.rationale is not None and not isinstance(result.rationale,str):return 'INVALID_RESPONSE_SCHEMA'
    for value in (result.latency_seconds,result.cost_usd):
        if value is not None and (isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0):return 'INVALID_RESPONSE_SCHEMA'
    if result.token_usage is not None and (not isinstance(result.token_usage,dict)
            or any(not isinstance(k,str) or type(v) is not int or v<0 for k,v in result.token_usage.items())):
        return 'INVALID_RESPONSE_SCHEMA'
    try:reject_credentials(asdict(result));serialize(asdict(result))
    except (ValueError,TypeError):return 'INVALID_RESPONSE_SCHEMA'
    return None


def execute(verifier,payload,who):
    """Exactly one call; generic errors, never provider exception bodies."""
    try:result=verifier.verify(**deepcopy(payload))
    except TimeoutError:return failure_result('TIMEOUT',who)
    except ProviderFailure:return failure_result('PROVIDER_ERROR',who)
    except Exception:return failure_result('EXECUTION_FAILURE',who)
    if result is None:return failure_result('MISSING_PREDICTION',who)
    problem=result_problem(result,who)
    return failure_result(problem,who) if problem else result


def score_predictions(rows):
    """Metrics conditional on valid predictions; failures remain in coverage.

    Fixed four-class macro averaging. Zero total coverage -> null classification
    metrics. With coverage, undefined individual precision/recall/F1 -> 0.
    """
    if not rows:raise ValueError('Evaluation requires examples')
    ids=[r['example_id'] for r in rows]
    if len(set(ids))!=len(ids):raise ValueError('Duplicate scoring example IDs')
    matrix={g:{p:0 for p in LABELS} for g in LABELS};failures=Counter();valid=[]
    for row in rows:
        gold=row['gold_label'];r=row['result']
        if gold not in LABELS:raise ValueError('Invalid analysis gold label')
        status=r['execution_status']
        if status not in STATUSES:raise ValueError('Unknown execution status')
        if status=='VALID_PREDICTION':
            if r['predicted_label'] not in LABELS:raise ValueError('Invalid prediction cannot be scored')
            matrix[gold][r['predicted_label']]+=1;valid.append(row)
        else:
            if r['predicted_label'] is not None:raise ValueError('Failure cannot carry a prediction')
            failures[status]+=1
    n=len(valid);classes={}
    for label in LABELS:
        tp=matrix[label][label];gold_count=sum(matrix[label].values());predicted_count=sum(matrix[g][label] for g in LABELS)
        precision=tp/predicted_count if predicted_count else 0.;recall=tp/gold_count if gold_count else 0.
        f1=2*precision*recall/(precision+recall) if precision+recall else 0.
        classes[label]={'precision':precision if n else None,'recall':recall if n else None,'f1':f1 if n else None,
                        'gold_count_valid':gold_count,'predicted_count':predicted_count,'true_positives':tp}
    denominator=sum(r['gold_label']!='SUPPORTED' for r in valid)
    false_support=sum(r['gold_label']!='SUPPORTED' and r['result']['predicted_label']=='SUPPORTED' for r in valid)
    return {'total_examples':len(rows),'valid_predictions':n,'prediction_coverage':n/len(rows),
            'accuracy':sum(matrix[l][l] for l in LABELS)/n if n else None,
            'per_class':classes,'macro_f1':sum(classes[l]['f1'] for l in LABELS)/4 if n else None,
            'confusion_matrix':{'orientation':'rows=gold, columns=prediction','label_order':list(LABELS),'counts':matrix},
            'false_support_rate':false_support/denominator if denominator else None,
            'false_support_numerator':false_support,'false_support_denominator_valid':denominator,
            'non_supported_gold_count_all':sum(r['gold_label']!='SUPPORTED' for r in rows),
            'supported_class_precision':classes['SUPPORTED']['precision'],'supported_class_recall':classes['SUPPORTED']['recall'],
            'failure_counts':{s:failures[s] for s in STATUSES if s!='VALID_PREDICTION'},
            'metric_scope':'valid predictions only; coverage/failures use all examples. FSR denominator is valid non-SUPPORTED gold examples; failures are not negative predictions.'}


def environment():
    dependencies={}
    for package in ('numpy','faiss-cpu','openai','streamlit','tiktoken'):
        try:dependencies[package]=version(package)
        except PackageNotFoundError:dependencies[package]=None
    return {'python':platform.python_version(),'python_implementation':platform.python_implementation(),
            'platform':platform.platform(),'dependency_versions':dependencies,
            'note':'Installed versions for reproducibility; baseline inference uses standard-library code only.'}


def build_run(verifier,benchmark,timestamp,precomputed=None):
    if sha(serialize(benchmark).encode())!=BENCHMARK_SHA256:
        raise ValueError('Evaluation requires the exact pinned benchmark')
    from datetime import datetime
    if not isinstance(timestamp,str) or datetime.fromisoformat(timestamp).tzinfo is None:
        raise ValueError('Run timestamp must be timezone-aware ISO-8601')
    if precomputed is not None and set(precomputed)!={r['example_id'] for r in benchmark['claim_examples']}:
        raise ValueError('Precomputed results must align with every claim ID exactly')
    who=identity(verifier);configuration=deepcopy(verifier.configuration);rows=[]
    for example in benchmark['claim_examples']:
        payload=verifier_input(example)
        result=precomputed[example['example_id']] if precomputed is not None else execute(verifier,payload,who)
        problem=result_problem(result,who)
        if problem:raise ValueError('Invalid precomputed prediction: '+problem)
        rows.append({'example_id':example['example_id'],'input':payload,'input_sha256':sha(serialize(payload).encode()),
                     'gold_label':example['gold_support_label'],'analysis_provenance':deepcopy(example['provenance']),
                     'result':asdict(result)})
    return {'schema_version':'1.0','benchmark_version':benchmark['benchmark_version'],'benchmark_sha256':BENCHMARK_SHA256,
            'verifier':who,'configuration_sha256':sha(serialize(configuration).encode()),
            'timestamp':timestamp,'runtime_environment':environment(),'random_seed':configuration.get('random_seed'),
            'execution':{'mode':'replay' if precomputed is not None else 'offline','hidden_retries':0,
                         'claim_examples':len(rows),'answer_examples_excluded':len(benchmark['answer_examples'])},
            'predictions':rows,'metrics':score_predictions(rows),
            'limitations':benchmark['limitations']+[
                'The lexical baseline does not understand negation, attribution or legal scope, and never predicts CONTRADICTED.',
                'Classifier metrics are conditional on valid predictions; inspect coverage and failure counts alongside them.',
                'No provider implementation, paid inference, application integration, or answer-level scoring is included.']}


@dataclass
class ReplayIdentity:
    verifier_id: str
    name: str
    version: str
    configuration: dict


def load_replay(path,benchmark,expected_id,expected_version):
    """Require every ID exactly once, including explicit failure rows."""
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:raise ValueError('Duplicate JSON field')
            d[k]=v
        return d
    data=json.loads(Path(path).read_text(),object_pairs_hook=pairs)
    if not isinstance(data,dict) or set(data)!={'schema_version','benchmark_version','benchmark_sha256','verifier','configuration','predictions'}:
        raise ValueError('Invalid replay file schema')
    if data['schema_version']!='1.0' or data['benchmark_version']!=benchmark['benchmark_version'] or data['benchmark_sha256']!=BENCHMARK_SHA256:
        raise ValueError('Replay benchmark/version mismatch')
    who=data['verifier']
    if not isinstance(who,dict) or set(who)!={'id','name','version'} or who['id']!=expected_id or who['version']!=expected_version:
        raise ValueError('Replay verifier identity mismatch')
    if not isinstance(data['configuration'],dict) or not isinstance(data['predictions'],list):
        raise ValueError('Invalid replay configuration/predictions schema')
    verifier=ReplayIdentity(who['id'],who['name'],who['version'],data['configuration']);identity(verifier)
    allowed={r['example_id'] for r in benchmark['claim_examples']};results={}
    for row in data['predictions']:
        if not isinstance(row,dict) or set(row)!={'example_id','result'}:raise ValueError('Invalid replay prediction schema')
        eid=row['example_id']
        if eid not in allowed or eid in results:raise ValueError('Unknown or duplicate replay example ID')
        required={'predicted_label','verifier_name','verifier_version','execution_status'}
        if (not isinstance(row['result'],dict) or not required<=set(row['result'])
                or not set(row['result'])<=set(VerificationResult.__dataclass_fields__)):
            raise ValueError('Invalid replay result schema')
        result=VerificationResult(**row['result']);problem=result_problem(result,who)
        if problem:raise ValueError('Invalid replay prediction: '+problem)
        results[eid]=result
    if set(results)!=allowed:raise ValueError('Missing replay IDs: explicit failure records are required')
    return verifier,results


def replay_document(run,configuration):
    if sha(serialize(configuration).encode())!=run['configuration_sha256']:raise ValueError('Run configuration changed')
    return {'schema_version':'1.0','benchmark_version':run['benchmark_version'],'benchmark_sha256':run['benchmark_sha256'],
            'verifier':run['verifier'],'configuration':deepcopy(configuration),
            'predictions':[{'example_id':r['example_id'],'result':r['result']} for r in run['predictions']]}


def write_run(run,configuration,output):
    """Exclusive new directory; never overwrite prior experiment files."""
    output=Path(output);who=run['verifier'];metrics=run['metrics']
    config={'verifier':who,'configuration':configuration,'implementation_sha256':{
        Path(__file__).name:sha(Path(__file__).read_bytes()),'bm25_retrieval.py':sha((ROOT/'bm25_retrieval.py').read_bytes())}}
    report='\n'.join(['# Citation verifier offline evaluation','',
        f"Verifier: {who['id']} v{who['version']}. Benchmark v{run['benchmark_version']}.",
        f"Benchmark SHA-256: `{run['benchmark_sha256']}`",'',
        ('Lexical overlap is a demonstration heuristic, not semantic legal verification.' if who['id']=='lexical-overlap' else 'Experimental verifier predictions are not proof of legal accuracy.'),'',
        '```json',serialize(metrics).rstrip(),'```','','## Limitations','']+['- '+v for v in run['limitations']])+'\n'
    files={'results.json':serialize(run),'configuration.json':serialize(config),
           'predictions.json':serialize(replay_document(run,configuration)),'report.md':report}
    manifest={'schema_version':'1.0','benchmark_sha256':run['benchmark_sha256'],
              'files_sha256':{name:sha(text.encode()) for name,text in files.items()}}
    files['manifest.json']=serialize(manifest)
    reject_credentials(files)
    output.parent.mkdir(parents=True,exist_ok=True);output.mkdir(exist_ok=False)
    for name,text in files.items():(output/name).write_text(text)
    return output
