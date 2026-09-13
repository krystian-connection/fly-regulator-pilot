"""Standard-library offline integrity and saved-record audit. Never calls inference."""
from pathlib import Path
import json,hashlib,math,collections,csv,sys,copy
ROOT=Path(__file__).resolve().parents[1]
CONDS=['alone','simple','random','fly','rewired','fly_reset','fly_disconnected']
TASKS=['resources','tools'];SEEDS=[11,29,47]
FRAME={'tick','energy','remaining_decisions','values','costs','gauges','changed','last_action','last_failed','progress'}
HISTORY=['decision','action','reward','energy','failed','violation','switched','retry_after_failure']
def need(ok,message):
 if not ok:raise ValueError(message)
def close(a,b):return math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def jl(p):return [json.loads(x) for x in p.read_text().splitlines()]
def public(call):
 prompt=call['request']['prompt']
 return json.loads(prompt.split('<|im_start|>user\n')[1].split('<|im_end|>')[0])
def check_records(rows,calls,probes,probe_calls):
 need(len(rows)==126 and len(calls)==756,'Balanced test record counts')
 idx={(r['task'],r['env_seed'],r['interface_seed'],r['condition']):r for r in rows}
 expected={(t,e,s,c) for t in TASKS for e in range(30000,30003) for s in SEEDS for c in CONDS}
 need(set(idx)==expected and len(idx)==len(rows),'Unique complete crossed design')
 api={c['call_id']:c for c in calls};need(len(api)==756,'Unique call IDs')
 seen=[];settings=None;system=None;total_tokens=0;latency=0.
 for r in rows:
  steps=r['steps'];need(len(steps)==6 and r['split']=='test','Full test horizon')
  energy=steps[0]['frames'][0]['energy'];total=0.;completed=0;violations=0;previous=None;last_failed=False;observations=[];history=[];switches=0;retries=0;changed=[]
  for i,s in enumerate(steps):
   frames=s['frames'];need(len(frames)==3,'Three numerical ticks per decision')
   for j,f in enumerate(frames):
    need(set(f)==FRAME and f['tick']==3*i+j,'Frame allowlist/tick')
    need(close(f['energy'],energy) and f['progress']==completed and f['remaining_decisions']==6-i,'Resource and progress observation consistency')
    need(f['last_action']==('ABC'.index(previous) if previous else -1) and f['last_failed']==int(last_failed),'Previous action/failure observation consistency')
    if f['changed']:changed.append(i)
   observations.extend(frames);out=s['outcome'];a=out['action'];need(a in 'ABC' and len(a)==1,'Valid actual action')
   c=api[s['call_id']];seen.append(s['call_id']);u=public(c)
   need(set(u)=={'rules','observations','history','controller'},'Public message allowlist')
   need(u['observations']==observations and u['history']==history,'Exact public history/observation equality; no scoring leakage')
   need(u['controller']=={k:s['signal'][k] for k in ['recommendation','scores']},'Exact delivered signal')
   if r['condition'] in ['alone','fly_disconnected']:need(u['controller']=={'recommendation':'NONE','scores':[0.,0.,0.]},'Neutral disconnected output')
   settings_now={k:v for k,v in c['request'].items() if k!='prompt'}
   if settings is None:settings=settings_now
   need(settings_now==settings,'Equal model settings and output schema')
   system_now=c['request']['prompt'].split('<|im_start|>user\n')[0]
   if system is None:system=system_now
   need(system_now==system,'Identical system prompt across arms')
   need(c['error'] is None and s['error'] is None and c['action']==a,'Call/episode error and action matching')
   need(json.loads(c['response']['choices'][0]['text'])=={'action':a},'Raw response matches recorded action')
   need(c['response']['usage']==s['usage'] and close(c['latency_s'],s['latency_s']),'Call costs match')
   need(s['usage']['prompt_tokens']+s['usage']['completion_tokens']==s['usage']['total_tokens'],'Usage arithmetic')
   total_tokens+=s['usage']['total_tokens'];latency+=s['latency_s']
   switched=int(a in ['A','B'] and previous in ['A','B'] and a!=previous)
   retry=int(a in ['A','B'] and a==previous and last_failed)
   violation=False
   if r['task']=='resources':
    if a=='C':energy=min(6.,energy+3.);reward=-.1;failed=False
    elif energy<frames[-1]['costs']['AB'.index(a)]:reward=-2.;violation=True;failed=True
    else:
     energy-=frames[-1]['costs']['AB'.index(a)];reward=frames[-1]['values']['AB'.index(a)];completed+=1;failed=False
   elif a=='C':reward=-.4;failed=False
   else:
    failed=out['failed'];reward=(-.3 if failed else 2.)-.2-.4*switched;completed+=int(not failed)
   need(out['decision']==i and close(out['reward'],reward) and close(out['energy'],energy),'Reconstructed reward/energy')
   need(out['violation']==violation and out['failed']==failed and out['switched']==switched and out['retry_after_failure']==retry,'Reconstructed costs/violation/failure')
   total+=reward;violations+=int(violation);switches+=switched;retries+=retry;previous=a;last_failed=failed
   history.append({k:out[k] for k in HISTORY})
  summary=r['summary'];need(close(summary['return'],total) and close(summary['normalized_return'],total/(18 if r['task']=='resources' else 10.8)),'Reconstructed return')
  need(summary['progress']==completed and summary['violations']==violations and summary['success']==(completed>=4 and violations==0),'Success and constraint scoring')
  need(summary['switches']==switches and summary['retries']==retries,'Switch/retry summaries')
  lags=[]
  for change in sorted(set(changed)):
   lag=6-change
   for h in history[change:]:
    if h['reward']>0 and not h['violation']:lag=h['decision']-change;break
   lags.append(lag)
  need(close(summary['recovery_lag'],sum(lags)/len(lags) if lags else 0),'Recovery lag')
 need(set(seen)==set(api) and len(seen)==len(api),'Every test call used exactly once')
 need(settings['model']=='fly-regulator-llm' and settings['temperature']==0 and settings['seed']==177 and settings['max_tokens']==32,'Frozen model settings')
 need(total_tokens==787231,'Test token total')
 differences=[idx[(t,e,s,'fly')]['summary']['normalized_return']-idx[(t,e,s,'simple')]['summary']['normalized_return'] for t in TASKS for e in range(30000,30003) for s in SEEDS]
 need(sum(abs(d)>1e-10 for d in differences)==1,'Single nonzero primary paired cell')
 need(close(sum(differences)/18,.009259259259259259),'Primary paired mean')
 for t in TASKS:
  for e in range(30000,30003):
   for s in SEEDS:
    a=idx[(t,e,s,'alone')];b=idx[(t,e,s,'fly_disconnected')]
    need([x['outcome']['action'] for x in a['steps']]==[x['outcome']['action'] for x in b['steps']],'Disconnected full-episode replay')
 need(len(probes)==24 and len(probe_calls)==48,'Probe counts');papi={c['call_id']:c for c in probe_calls};need(len(papi)==48,'Unique probe calls');pseen=[];changed_probes=0;probe_states=set()
 for p in probes:
  key=(p['task'],p['env_seed'],p['interface_seed'],p['decision']);need(key not in probe_states,'Unique probe states');probe_states.add(key)
  need(p['decision'] in [0,3],'Prespecified probe decision restriction')
  pair=[]
  for mode in ['active','neutral']:
   rec=p['pair'][mode];c=papi[rec['call_id']];pseen.append(c['call_id']);u=public(c)
   need(c['action']==rec['action'] and c['error'] is None and json.loads(c['response']['choices'][0]['text'])=={'action':rec['action']},'Probe response/action integrity')
   need({k:v for k,v in c['request'].items() if k!='prompt'}==settings,'Probe settings same as test')
   original=api[idx[(p['task'],p['env_seed'],p['interface_seed'],'fly')]['steps'][p['decision']]['call_id']]
   want=public(original)
   if mode=='neutral':want['controller']={'recommendation':'NONE','scores':[0.,0.,0.]}
   need(u==want,'Probe identical saved state and intended intervention')
   pair.append(rec['action'])
  need(p['changed']==(pair[0]!=pair[1]),'Probe action-change flag');changed_probes+=int(p['changed'])
 need(len(pseen)==len(set(pseen))==48 and set(pseen)==set(papi),'Every probe call used exactly once')
 need(changed_probes==7,'Seven causal changes')
 return {'test_episodes':126,'test_calls':756,'paired_probe_calls':48,'changed_probe_pairs':7,'disconnected_matching_episodes':18,'total_test_tokens':total_tokens,'summed_test_latency_s':latency,'primary_mean':sum(differences)/18,'nonzero_primary_pairs':1}
def verify(root=ROOT,sealed=True):
 manifest=json.loads((root/'RELEASE_MANIFEST.json').read_text())
 for row in manifest['files']:need(sha(root/row['path'])==row['release_sha256'],'Manifest digest mismatch: '+row['path'])
 if sealed:
  hashes=json.loads((root/'SHA256SUMS.json').read_text())
  actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.name!='SHA256SUMS.json' and '__pycache__' not in p.parts and p.name!='.DS_Store'}
  need(actual==set(hashes),'Exact release file allowlist')
  for p,h in hashes.items():need(sha(root/p)==h,'Release digest mismatch: '+p)
 lock=json.loads((root/'runs/protocol_lock.json').read_text());included=0;missing=[];sanitised=[]
 for p,h in lock['hashes'].items():
  if not (root/p).exists():missing.append(p)
  elif sha(root/p)==h:included+=1
  else:
   entry=next((m for m in manifest['files'] if m['path']==p),None)
   need(p=='runs/machine.json' and entry['original_sha256']==h,'Unexplained pre-test hash mismatch: '+p);sanitised.append(p)
 need(all(p.endswith('.npz') for p in missing),'Only declared graph/readout files absent from protocol lock')
 result=check_records(jl(root/'runs/test_episodes.jsonl'),jl(root/'runs/test_calls.jsonl'),jl(root/'runs/causal_probes.jsonl'),jl(root/'runs/probe_calls.jsonl'))
 ledger=jl(root/'runs/call_ledger.jsonl');profiles=jl(root/'runs/profile.jsonl')
 need(len(profiles)==3 and len(ledger)==997,'Historical reservation ledger count')
 tags=dict(collections.Counter(r['tag'] for r in ledger));budget=json.loads((root/'runs/final_budget.json').read_text())
 need(tags==budget['tag_counts'] and len(ledger)+len(profiles)==budget['total_initial_reservations']==1000,'Exhausted original budget')
 need(tags['validation']==84 and tags['validation_v2']==84 and tags['validation_v3']==24,'Quarantined validation counts')
 episodes=jl(root/'runs/test_episodes.jsonl');idx={(r['task'],r['env_seed'],r['interface_seed'],r['condition']):r for r in episodes}
 with (root/'runs/episode_summary.csv').open() as f:
  tab=list(csv.DictReader(f));need(len(tab)==126,'CSV episode count')
  for row in tab:
   r=idx[(row['task'],int(row['env_seed']),int(row['interface_seed']),row['condition'])]
   for k,v in r['summary'].items():need(row[k]==str(v),'CSV summary field '+k)
   need(row['actions']==''.join(s['outcome']['action'] for s in r['steps']),'CSV action sequence')
 result.update(status='passed',sealed=sealed,original_frozen_files_byte_identical=included,explicitly_sanitised_frozen_files=sanitised,excluded_frozen_graph_readout_files=len(missing),total_initial_reservations=1000,scope='Saved-record consistency and packaging audit by implementing agent; no fresh inference, graph reconstruction or independent review.')
 return result
if __name__=='__main__':
 try:print(json.dumps(verify(sealed='--unsealed' not in sys.argv),indent=2))
 except Exception as ex:print('FAILED: '+str(ex),file=sys.stderr);sys.exit(1)
