import sys,json,itertools
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import experiment as e
import numpy as np
rows=[]
for task in e.TASKS:
 for i in range(16):
  seed=20000+i
  for policy in ['random','observable_teacher','always_A','always_C']:
   env=e.Environment(task,seed,'validation');belief=np.ones(2)*.5;rng=np.random.default_rng(seed+90)
   for _ in range(6):
    fs=env.advance();scores=e.teacher(fs,task,belief);a={'random':int(rng.integers(3)),'observable_teacher':int(np.argmax(scores)),'always_A':0,'always_C':2}[policy];env.step(e.ACTIONS[a])
   rows.append({'task':task,'seed':seed,'policy':policy,**env.summary()})
e.dump(e.ROOT/'runs/validation_difficulty.json',rows)
for task in e.TASKS:
 for policy in ['random','observable_teacher','always_A','always_C']:
  v=[r for r in rows if r['task']==task and r['policy']==policy];print(task,policy,'return',round(np.mean([r['return'] for r in v]),3),'success',np.mean([r['success'] for r in v]))
