"""Offline baseline or strict precomputed replay; no provider client or retries."""
import argparse
from datetime import datetime, timezone
from pathlib import Path

from citation_verifier_evaluation import (ROOT, LexicalOverlapBaseline, load_benchmark,
    load_replay, build_run, write_run, serialize)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True,help='New output directory; existing directories are rejected')
    parser.add_argument('--replay',type=Path)
    parser.add_argument('--verifier-id',help='Required expected verifier ID for replay')
    parser.add_argument('--verifier-version',help='Required expected verifier version for replay')
    parser.add_argument('--timestamp',help='ISO-8601 timezone-aware timestamp for exact artifact reproduction')
    args=parser.parse_args()
    if args.output.exists():parser.error('Output directory already exists; refusing overwrite')
    timestamp=args.timestamp or datetime.now(timezone.utc).isoformat()
    try:
        parsed=datetime.fromisoformat(timestamp)
        if parsed.tzinfo is None:raise ValueError('Timestamp must include timezone')
    except ValueError:parser.error('Timestamp must be timezone-aware ISO-8601')
    benchmark=load_benchmark()
    verifier=LexicalOverlapBaseline();precomputed=None
    if args.replay:
        if not args.verifier_id or not args.verifier_version:parser.error('Replay requires expected verifier ID/version')
        verifier,precomputed=load_replay(args.replay,benchmark,args.verifier_id,args.verifier_version)
    elif args.verifier_id or args.verifier_version:parser.error('Verifier identity options apply only to replay')
    run=build_run(verifier,benchmark,timestamp,precomputed)
    write_run(run,verifier.configuration,args.output)
    print(serialize({'output':str(args.output),'verifier':run['verifier'],'metrics':run['metrics']}))


if __name__=='__main__':main()
