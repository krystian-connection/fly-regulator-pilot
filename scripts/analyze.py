"""Episode-paired, crossed environment/interface bootstrap; never samples steps as units."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import experiment as e
import numpy as np
rows=[json.loads(l) for l in (e.ROOT/'runs/test_episodes.jsonl').read_text().splitlines()]
assert len(rows)==126
index={(r['task'],r['env_seed'],r['interface_seed'],r['condition']):r for r in rows};assert len(index)==126
summary=[]
for task in e.TASKS+['pooled']:
 for cond in e.CONDITIONS:
  rr=[r for r in rows if r['condition']==cond and (task=='pooled' or r['task']==task)]
  m={k:float(np.mean([r['summary'][k] for r in rr])) for k in rr[0]['summary']}
  steps=[s for r in rr for s in r['steps']]
  m.update(task=task,condition=cond,episodes=len(rr),controller_ms=float(np.mean([s['signal']['controller_ms'] for s in steps])),latency_s=float(np.mean([s['latency_s'] for s in steps])),prompt_tokens=float(np.mean([s['usage'].get('prompt_tokens',0) for s in steps])),completion_tokens=float(np.mean([s['usage'].get('completion_tokens',0) for s in steps])),errors=sum(bool(s['error']) for s in steps),advice_agreement=float(np.mean([s['signal']['recommendation']==s['outcome']['action'] for s in steps])))
  summary.append(m)
contrasts=[]
for comparator in ['simple','alone','random','rewired','fly_reset','fly_disconnected']:
 d=np.array([[[index[(task,30000+i,seed,'fly')]['summary']['normalized_return']-index[(task,30000+i,seed,comparator)]['summary']['normalized_return'] for seed in e.SEEDS] for i in range(3)] for task in e.TASKS])
 rng=np.random.default_rng(812);boot=[]
 for _ in range(10000):
  ss=rng.integers(3,size=3);draw=[]
  for t in range(2):
   ii=rng.integers(3,size=3);draw.append(d[t][ii][:,ss].mean())
  boot.append(np.mean(draw))
 contrasts.append({'comparison':'fly minus '+comparator,'mean':float(d.mean()),'ci95':np.quantile(boot,[.025,.975]).tolist(),'task_means':{task:float(d[t].mean()) for t,task in enumerate(e.TASKS)}})
probes=[json.loads(l) for l in (e.ROOT/'runs/causal_probes.jsonl').read_text().splitlines()] if (e.ROOT/'runs/causal_probes.jsonl').exists() else []
profiles=[json.loads(l) for l in (e.ROOT/'runs/profile.jsonl').read_text().splitlines()];ledger=[json.loads(l) for l in (e.ROOT/'runs/call_ledger.jsonl').read_text().splitlines()]
disconnected=[]
for task in e.TASKS:
 for i in range(3):
  for seed in e.SEEDS:
   a=index[(task,30000+i,seed,'alone')];b=index[(task,30000+i,seed,'fly_disconnected')]
   disconnected.append({'task':task,'env_seed':30000+i,'interface_seed':seed,'actions_identical':[s['outcome']['action'] for s in a['steps']]==[s['outcome']['action'] for s in b['steps']]})
mem=[json.loads(l) for l in (e.ROOT/'runs/memory_samples.jsonl').read_text().splitlines()]
peak_lm=max(sum(p['rss_kib'] for p in s['processes'] if 'LM Studio' in p['process'] or 'llama' in p['process'].lower()) for s in mem)/1024
out={'summary':summary,'paired_contrasts':contrasts,'experimental_reservations':len(profiles)+sum(x['tag']!='explore' for x in ledger),'test_calls':sum(x['tag']=='test' for x in ledger),'causal_probe_pairs':len(probes),'causal_changes':sum(p['changed'] for p in probes),'causal_by_task':{task:{'pairs':sum(p['task']==task for p in probes),'changes':sum(p['changed'] for p in probes if p['task']==task)} for task in e.TASKS},'disconnected_replays':disconnected,'peak_lm_process_rss_sum_MiB':peak_lm,'memory_warning':'Sum of process RSS can double-count shared pages and is not total Metal/unified memory allocation.'}
e.dump(e.ROOT/'runs/analysis.json',out)
print(json.dumps({'paired_contrasts':contrasts,'causal_changes':out['causal_changes'],'causal_pairs':len(probes),'experimental_reservations':out['experimental_reservations']},indent=2))
