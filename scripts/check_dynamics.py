import sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import experiment as e
import numpy as np
rows=[]
for cond in ['simple','random','fly','rewired']:
 for seed in e.SEEDS:
  c=e.controller(cond,seed);c.x[:]=.5;decay=[]
  for t in range(200):
   c.x=(1-c.leak)*c.x+c.leak*np.tanh(c.w@c.x if c.graph else np.zeros(e.DIM));decay.append(float(np.max(np.abs(c.x))))
  c=e.controller(cond,seed);frames=e.Environment('tools',20001,'validation').advance();start=time.perf_counter()
  for i in range(100):c.features(frames,'tools')
  elapsed=time.perf_counter()-start
  rows.append({'condition':cond,'seed':seed,'leak':c.leak,'half_amplitude_ticks':next(i+1 for i,x in enumerate(decay) if x<.25),'below_1e_minus3_ticks':next(i+1 for i,x in enumerate(decay) if x<.001),'max_abs_after_200_zero_input_ticks':decay[-1],'ms_per_three_ticks':elapsed*10,'state_bytes':c.x.nbytes,'graph_bytes':0 if not c.graph else c.w.data.nbytes+c.w.indices.nbytes+c.w.indptr.nbytes,'decay':decay})
e.dump(e.ROOT/'data/dynamics_checks.json',rows)
print([(r['condition'],r['seed'],r['half_amplitude_ticks'],r['below_1e_minus3_ticks']) for r in rows])
