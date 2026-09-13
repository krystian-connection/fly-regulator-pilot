from pathlib import Path
import sys,datetime,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import experiment as e
p=e.ROOT/'runs/protocol_lock.json'
if p.exists():raise SystemExit('Lock already exists; do not overwrite')
assert not (e.ROOT/'runs/test_calls.jsonl').exists()
files=['PROTOCOL.md','experiment.py','requirements.txt','tests/test_experiment.py','scripts/probes.py','scripts/analyze.py','scripts/audit_harness.py','scripts/run_pilot.py','runs/machine.json','runs/tuning.json','run_config.json','data/manifest.json','data/graph_controls.json','data/anatomy_audit.json','data/dynamics_checks.json']
files+=[str(p.relative_to(e.ROOT)) for p in (e.ROOT/'data').glob('*.npz')]
e.dump(p,{'frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hashes':{f:e.sha(e.ROOT/f) for f in files}});print('Protocol and execution artifacts frozen:',len(files),'files')
