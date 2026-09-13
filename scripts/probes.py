"""Prespecified same-observation local-LLM causal output-disconnection probes."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import experiment as e
import numpy as np
p=e.ROOT/'runs/causal_probes.jsonl'
if p.exists():raise SystemExit('Refusing to overwrite causal probes')
lock=json.loads((e.ROOT/'runs/protocol_lock.json').read_text())
for name,digest in lock['hashes'].items():
 if e.sha(e.ROOT/name)!=digest:raise SystemExit('Frozen artifact changed: '+name)
rows=[json.loads(l) for l in (e.ROOT/'runs/test_episodes.jsonl').read_text().splitlines()]
rng=np.random.default_rng(910)
for task in e.TASKS:
 candidates=[]
 for row in sorted([r for r in rows if r['condition']=='fly' and r['task']==task],key=lambda r:(r['env_seed'],r['interface_seed'])):
  for decision in [0,3]:candidates.append((row,decision))
 for row,decision in candidates[:12]:
  env=e.Environment(task,row['env_seed']);env.observations=[f for s in row['steps'][:decision+1] for f in s['frames']];env.history=[s['outcome'] for s in row['steps'][:decision]]
  active=row['steps'][decision]['signal'];neutral=dict(active,recommendation='NONE',scores=[0.,0.,0.]);pair={};order=['active','neutral'];rng.shuffle(order)
  for arm in order:
   a,call=e.llm(env,active if arm=='active' else neutral,'probe');pair[arm]={'action':a,'call_id':call['call_id'],'error':call['error']}
  e.append(p,{'task':task,'env_seed':row['env_seed'],'interface_seed':row['interface_seed'],'decision':decision,'pair':pair,'changed':pair['active']['action']!=pair['neutral']['action']})
  print(task,row['env_seed'],row['interface_seed'],decision,'paired probe complete',flush=True)
