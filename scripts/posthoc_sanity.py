"""Post-test diagnostic only: fixed observable teacher and clairvoyant attainable bounds.
No LLM calls, fitting, parameter changes or task selection. Never a training target.
"""
from pathlib import Path
import sys,itertools
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import experiment as e
import numpy as np
rows=[]
for task in e.TASKS:
 for seed in range(30000,30003):
  env=e.Environment(task,seed);belief=np.ones(2)*.5
  for _ in range(6):
   fs=env.advance();a=int(np.argmax(e.teacher(fs,task,belief)));env.step(e.ACTIONS[a])
  teacher=env.summary();best=-1e9;success_possible=False;best_actions=None
  for actions in itertools.product(e.ACTIONS,repeat=6):
   env=e.Environment(task,seed)
   for a in actions:env.advance();env.step(a)
   s=env.summary();success_possible |= s['success']
   if s['return']>best:best=s['return'];best_actions=actions
  rows.append({'task':task,'seed':seed,'observable_teacher':teacher,'clairvoyant_max_return':best,'success_attainable':bool(success_possible),'clairvoyant_actions':best_actions})
e.dump(e.ROOT/'runs/posthoc_task_sanity.json',{'label':'Post-test sanity check, not preregistered outcome or fitted target. Exhaustive search sees future outcomes and is only an attainability bound.', 'rows':rows})
for r in rows:print(r['task'],r['seed'],'teacher return',round(r['observable_teacher']['return'],3),'teacher success',r['observable_teacher']['success'],'success attainable',r['success_attainable'],'max',r['clairvoyant_max_return'])
