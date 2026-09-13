"""Local fly-connectome regulator pilot. Synthetic tasks, fixed measured graph."""
from pathlib import Path
import json, hashlib, time, resource, urllib.request, fcntl, os
import numpy as np
from scipy import sparse
ROOT=Path(__file__).resolve().parent
CONDITIONS=['alone','simple','random','fly','rewired','fly_reset','fly_disconnected']
TASKS=['resources','tools']; SEEDS=[11,29,47]; HORIZON=6; TICKS=3
ACTIONS=['A','B','C']; DIM=16

def dump(path,obj):
 Path(path).write_text(json.dumps(obj,indent=2,allow_nan=False))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def append(path,obj):
 with Path(path).open('a') as f:f.write(json.dumps(obj,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())

def make_graphs():
 raw=sparse.load_npz(ROOT/'data/fly_raw.npz').tocoo();n=raw.shape[0];m=raw.nnz
 # Normalize anatomical incoming counts ONCE; retain this exact multiset in controls.
 weights=raw.data/np.asarray(raw.tocsr().sum(axis=1)).ravel()[raw.row]
 graphs={'fly':(raw.row.copy(),raw.col.copy(),weights.copy())};stats={}
 for seed in SEEDS:
  rng=np.random.default_rng(seed)
  row,col=raw.row.copy(),raw.col.copy();edges=set(zip(row.tolist(),col.tolist()));swaps=0;attempts=0
  # Directed double-edge swap: exchange sources, holding target-associated weights.
  # Allows existing autapses, rejects duplicate pairs. Exact directed degrees + incoming strength.
  while swaps<10*m:
   i,j=rng.integers(m,size=2);a,b=int(row[i]),int(col[i]);c,d=int(row[j]),int(col[j]);attempts+=1
   if a==c or b==d or (a,d) in edges or (c,b) in edges:continue
   edges.remove((a,b));edges.remove((c,d));edges.add((a,d));edges.add((c,b));col[i]=d;col[j]=b;swaps+=1
  graphs[f'rewired_{seed}']=(row,col,weights.copy())
  stats[f'rewired_{seed}']={'accepted_swaps':swaps,'attempts':attempts,'edge_overlap':len(edges & set(zip(raw.row.tolist(),raw.col.tolist())))/m,'in_degree_exact':bool(np.array_equal(np.bincount(row,minlength=n),np.bincount(raw.row,minlength=n))),'out_degree_exact':bool(np.array_equal(np.bincount(col,minlength=n),np.bincount(raw.col,minlength=n)))}
  ix=rng.choice(n*n,size=m,replace=False)
  graphs[f'random_{seed}']=(ix//n,ix%n,rng.permutation(weights))
 bound=max(np.bincount(r,weights=w,minlength=n).max() for r,c,w in graphs.values());scale=.85/bound
 for key,(r,c,w) in graphs.items():
  mat=sparse.csr_matrix((w*scale,(r,c)),shape=(n,n));sparse.save_npz(ROOT/f'data/{key}.npz',mat)
  stats.setdefault(key,{}).update({'nodes':n,'edges':mat.nnz,'max_incoming_sum':float(np.max(np.asarray(mat.sum(axis=1)))),'self_loops':int(np.count_nonzero(mat.diagonal())),'bytes':mat.data.nbytes+mat.indices.nbytes+mat.indptr.nbytes,'sha256':sha(ROOT/f'data/{key}.npz')})
 dump(ROOT/'data/graph_controls.json',{'common_scale':scale,'original_weight_normalization':'per-postsynaptic sum before rewiring/randomization; one common final scale across all variants','graphs':stats})
 return stats

class Environment:
 def __init__(self,task,seed,split='test',overrides=None):
  assert task in TASKS and split in ['train','validation','test','explore']
  self.task=task;self.seed=seed;self.split=split;self.overrides=overrides or {};self.t=0;self.energy=4.;self.total=0.;self.progress=0;self.last=-1;self.failed=0;self.history=[];self.observations=[];self.switches=0;self.retries=0;self.violations=0;self.regrets=[];self.changed_steps=[];self.last_inspect=None
  rng=np.random.default_rng(seed)
  # Disjoint change-time combinations, including unseen double changes in test.
  self.changes={'train':[6,12],'validation':[9],'test':[5,11],'explore':[5,11]}[split]
  self.initial=int(rng.integers(2));self.resource_rates=np.round(rng.uniform([2.5,.75],[3.,1.5],size=(3,2)),2);self.energy=float(rng.integers(3,6)) if task=='resources' else 4.;self.noise=rng.random((HORIZON*TICKS,2));self.outcomes=rng.random((HORIZON,2))
  self.costs=[2.,1.];self.values=[3.,1.5];self.ps=[.85,.2]
 def advance(self):
  if self.t>=HORIZON:raise ValueError('Episode complete; reset required')
  frames=[]
  for tick in range(self.t*TICKS,(self.t+1)*TICKS):
   phase=self.initial+sum(tick>=x for x in self.changes);hot=phase%2
   change=int(tick in self.changes)
   if change:self.changed_steps.append(self.t)
   self.ps=([.85,.2] if hot==0 else [.2,.85])
   hi,lo=self.resource_rates[sum(tick>=x for x in self.changes)];self.values=([float(hi),float(lo)] if hot==0 else [float(lo),float(hi)]);self.costs=([2.,1.] if hot==0 else [1.,2.])
   if 'reliability_a' in self.overrides:self.ps[0]=self.overrides['reliability_a']
   if 'reliability_b' in self.overrides:self.ps[1]=self.overrides['reliability_b']
   self.ps=np.clip(self.ps,0,1).tolist()
   gauges=(self.noise[tick]<self.ps).astype(float).tolist()
   if self.task=='resources':gauges=[1.,1.]
   if self.last_inspect is not None and self.task=='tools':gauges=self.last_inspect;self.last_inspect=None
   frame={'tick':tick,'energy':self.energy,'remaining_decisions':HORIZON-self.t,'values':self.values.copy() if self.task=='resources' else [2.,2.], 'costs':self.costs.copy() if self.task=='resources' else [.2,.2],'gauges':gauges,'changed':change,'last_action':self.last,'last_failed':self.failed,'progress':self.progress}
   frames.append(frame);self.observations.append(frame)
  return frames
 def step(self,action):
  if self.t>=HORIZON:raise ValueError('Episode complete')
  valid=action in ACTIONS;a=ACTIONS.index(action) if valid else -1;prev=self.last;fail=False;violation=False
  utilities=[2.3*p-.5-.4*(prev in (0,1) and prev!=j) for j,p in enumerate(self.ps)]
  switched=int(a in (0,1) and prev in (0,1) and a!=prev);retry=int(a in (0,1) and a==prev and self.failed)
  if not valid:reward=-2.;violation=True;fail=True
  elif self.task=='resources':
   if a==2:self.energy=min(6.,self.energy+float(self.overrides.get('recharge',3.)));reward=-.1
   elif self.energy<self.costs[a]:reward=-2.;violation=True;fail=True
   else:self.energy-=self.costs[a];reward=self.values[a];self.progress+=1
  else:
   if a==2:reward=-.4;self.last_inspect=self.ps.copy()
   else:fail=bool(self.outcomes[self.t,a]>=self.ps[a]);reward=(2. if not fail else -.3)-.2-.4*switched;self.progress+=int(not fail)
   utilities=[2.3*p-.5-.4*(prev in (0,1) and prev!=j) for j,p in enumerate(self.ps)]
  regret=0.
  if self.task=='tools':regret=max(utilities)- (utilities[a] if a in (0,1) else (-.4 if a==2 else -2.))
  self.regrets.append(float(regret));self.total+=reward;self.violations+=int(violation);self.switches+=switched;self.retries+=retry;self.last=a;self.failed=int(fail)
  rec={'decision':self.t,'action':action,'reward':float(reward),'energy':self.energy,'failed':fail,'violation':violation,'switched':switched,'retry_after_failure':retry,'unnecessary_switch':int(self.task=='tools' and switched and utilities[a]<=utilities[prev]),'unnecessary_retry':int(self.task=='tools' and retry and utilities[a]<max(utilities)), 'expected_regret':float(regret)}
  self.history.append(rec);self.t+=1;return rec
 def summary(self):
  # Full horizon; inspection/recharge/invalid never count as completed work.
  return {'return':self.total,'normalized_return':self.total/(18. if self.task=='resources' else 10.8),'success':bool(self.t==HORIZON and self.progress>=4 and self.violations==0),'progress':self.progress,'violations':self.violations,'switches':self.switches,'retries':self.retries,'unnecessary_switches':sum(h['unnecessary_switch'] for h in self.history),'unnecessary_retries':sum(h['unnecessary_retry'] for h in self.history),'expected_regret':float(sum(self.regrets)),'recovery_lag':self.recovery()}
 def recovery(self):
  lags=[]
  for s in sorted(set(self.changed_steps)):
   lag=HORIZON-s
   for h in self.history[s:]:
    if h['reward']>0 and not h['violation']:lag=h['decision']-s;break
   lags.append(lag)
  return float(np.mean(lags)) if lags else 0.

def vector(frame,task):
 f=frame;u=np.array([f['energy']/6,f['remaining_decisions']/6,*[v/3 for v in f['values']],*[c/2 for c in f['costs']],*f['gauges'],f['changed'],f['last_failed'],f['progress']/6,float(task=='tools'),float(f['last_action']==0),float(f['last_action']==1),float(f['last_action']==2),1.])
 assert u.shape==(DIM,) and np.isfinite(u).all();return u

class Controller:
 def __init__(self,condition,seed,leak=.5,ridge=.01,fit=None):
  self.condition=condition;self.seed=seed;self.leak=leak;self.ridge=ridge;self.fit=fit;self.previous=0
  key='fly' if condition.startswith('fly') else f'{condition}_{seed}'
  self.graph=condition not in ['alone','simple']
  self.w=sparse.load_npz(ROOT/f'data/{key}.npz') if self.graph else None
  n=self.w.shape[0] if self.graph else DIM;self.x=np.zeros(n);rng=np.random.default_rng(seed+1000)
  self.input_index=rng.integers(DIM,size=n);self.input_sign=rng.choice([-1.,1.],size=n)
  self.pool=rng.integers(DIM,size=n);self.pool_sign=rng.choice([-1.,1.],size=n);self.pool_count=np.sqrt(np.maximum(1,np.bincount(self.pool,minlength=DIM)))
 def features(self,frames,task):
  if self.condition=='fly_reset':self.x.fill(0);self.previous=0
  for f in frames:
   u=vector(f,task)
   drive=.6*u[self.input_index]*self.input_sign if self.graph else .6*u
   recurrent=self.w@self.x if self.graph else 0
   self.x=(1-self.leak)*self.x+self.leak*np.tanh(recurrent+drive)
   assert np.isfinite(self.x).all() and np.max(np.abs(self.x))<=1+1e-9
  return np.bincount(self.pool,weights=self.x*self.pool_sign,minlength=DIM)/self.pool_count if self.graph else self.x.copy()
 def signal(self,frames,task):
  start=time.perf_counter();f=self.features(frames,task)
  if self.fit is None:scores=np.zeros(3)
  else:scores=np.r_[((f-self.fit['mean'])/self.fit['scale']),1.]@self.fit['coef']
  # Explicit small prioritisation interface, common 0.1 hysteresis across active arms.
  best=int(np.argmax(scores))
  if scores[best]-scores[self.previous]<.1:best=self.previous
  self.previous=best
  disconnected=self.condition in ['alone','fly_disconnected'];output='NONE' if disconnected else ACTIONS[best]
  return {'recommendation':output,'scores':[round(float(s),3) for s in scores] if not disconnected else [0.,0.,0.],'state_rms':float(np.sqrt(np.mean(self.x**2))),'controller_ms':1000*(time.perf_counter()-start),'computed_recommendation':ACTIONS[best]}

def teacher(frames,task,belief):
 for f in frames:belief[:]=.6*belief+.4*np.array(f['gauges'])
 f=frames[-1]
 if task=='resources':
  e=f['energy'];v=f['values'];c=f['costs'];score=[v[j]/c[j] if e>=c[j] else -2. for j in range(2)]
  score.append(1.5 if e<min(c) else (-.2 if e>=3 else .8))
 else:
  score=[2.3*belief[j]-.5-.4*(f['last_action'] in (0,1) and f['last_action']!=j) for j in range(2)];score.append(-.4)
 return np.array(score)

def trajectories(split,count):
 data=[]
 for task in TASKS:
  for i in range(count):
   seed=({'train':10000,'validation':20000}[split])+i;env=Environment(task,seed,split);belief=np.ones(2)*.5;seq=[];rng=np.random.default_rng(seed+400)
   for step in range(HORIZON):
    frames=env.advance();target=teacher(frames,task,belief);seq.append((frames,target))
    # Coverage policy independent of any condition, 50% teacher and 50% random.
    a=int(np.argmax(target)) if rng.random()<.5 else int(rng.integers(3));env.step(ACTIONS[a])
   data.append((task,seq))
 return data

def train():
 tr=trajectories('train',40);va=trajectories('validation',16);report=[]
 for condition in ['simple','random','fly','rewired','fly_reset']:
  for seed in SEEDS:
   candidates=[]
   for leak in [.2,.5]:
    def extract(data):
     xs=[];ys=[]
     for task,seq in data:
      c=Controller(condition,seed,leak)
      for frames,target in seq:xs.append(c.features(frames,task));ys.append(target)
     return np.array(xs),np.array(ys)
    x,y=extract(tr);vx,vy=extract(va);mean=x.mean(0);scale=np.maximum(x.std(0),1e-4);X=np.c_[(x-mean)/scale,np.ones(len(x))];V=np.c_[(vx-mean)/scale,np.ones(len(vx))]
    for ridge in [.01,1.]:
     coef=np.linalg.solve(X.T@X+ridge*np.eye(DIM+1),X.T@y);mse=float(np.mean((V@coef-vy)**2));candidates.append((mse,leak,ridge,mean,scale,coef))
   best=min(candidates,key=lambda z:z[0]);mse,leak,ridge,mean,scale,coef=best
   np.savez(ROOT/f'data/readout_{condition}_{seed}.npz',mean=mean,scale=scale,coef=coef,leak=leak,ridge=ridge)
   report.append({'condition':condition,'seed':seed,'leak':leak,'ridge':ridge,'validation_mse':mse,'candidates':[{'mse':c[0],'leak':c[1],'ridge':c[2]} for c in candidates],'training_decisions':len(x),'validation_decisions':len(vx),'readout_parameters':int(coef.size)})
 dump(ROOT/'runs/tuning.json',report)

def controller(condition,seed):
 k='fly' if condition=='fly_disconnected' else condition
 if k=='alone':return Controller(k,seed)
 a=np.load(ROOT/f'data/readout_{k}_{seed}.npz');fit={k:a[k] for k in ['mean','scale','coef']};return Controller(condition,seed,float(a['leak']),float(a['ridge']),fit)

SYSTEM='''You control a six-decision sandbox episode. Maximize total reward while avoiding constraint violations. Every decision consumes one opportunity. A and B perform work; C recovers or inspects. No quitting. Use all observed history. Gauges and changes are observed evidence, not future knowledge. The optional numerical controller recommends A, B, C, or NONE. Treat it as fallible advice; choose the action yourself. Return only JSON {"action":"A"}, {"action":"B"}, or {"action":"C"}.'''
RULES={'resources':'Resources: A/B earn current values and consume current energy costs. Insufficient energy costs -2 and completes no work. C adds 3 energy (capacity 6), reward -0.1. Priorities/costs may change; future schedules unknown. Success requires >=4 work completions and zero violations at decision 6.', 'tools':'Tools: A/B attempt equivalent work. Success +2, failure -0.3, attempt cost 0.2. Switching A/B also costs 0.4. Each gauge is a noisy independent 0/1 health probe; reliability may change. C costs 0.4 and supplies a precise reliability reading on the next tick. Success requires >=4 successful work completions at decision 6.'}

def reserve_call(tag):
 path=ROOT/'runs/call_ledger.jsonl'
 with path.open('a+') as f:
  fcntl.flock(f,fcntl.LOCK_EX);f.seek(0);rows=[json.loads(l) for l in f if l.strip()]
  profiles=sum(1 for l in (ROOT/'runs/profile.jsonl').read_text().splitlines()) if (ROOT/'runs/profile.jsonl').exists() else 0
  count=sum(r['tag']!='explore' for r in rows)+profiles
  if tag!='explore' and count>=1000:raise RuntimeError('Initial 1000-call cap reached')
  ident=len(rows)+1;f.seek(0,2);f.write(json.dumps({'id':ident,'tag':tag,'time':time.time()})+'\n');f.flush();os.fsync(f.fileno());return ident

def llm(env,signal,tag):
 # Only allowlisted public observations/history; no environment seed, schedule, latent ps, outcome table or targets.
 rules=RULES[env.task]
 if env.task=='resources' and 'recharge' in env.overrides:rules=rules.replace('C adds 3 energy',f"C adds {env.overrides['recharge']} energy")
 public_history=[{k:h[k] for k in ['decision','action','reward','energy','failed','violation','switched','retry_after_failure']} for h in env.history]
 user={'rules':rules,'observations':env.observations,'history':public_history,'controller':{'recommendation':signal['recommendation'],'scores':signal['scores']}}
 prompt='<|im_start|>system\n'+SYSTEM+'<|im_end|>\n<|im_start|>user\n'+json.dumps(user,separators=(',',':'))+'<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n'
 body={'model':'fly-regulator-llm','prompt':prompt,'temperature':0,'max_tokens':32,'seed':177,'stop':['<|im_end|>'],'response_format':{'type':'json_schema','json_schema':{'name':'decision','strict':True,'schema':{'type':'object','properties':{'action':{'type':'string','enum':ACTIONS}},'required':['action'],'additionalProperties':False}}}}
 ident=reserve_call(tag);start=time.perf_counter();result={};action='INVALID';error=None
 try:
  req=urllib.request.Request('http://127.0.0.1:1234/v1/completions',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=90) as response:result=json.load(response)
  action=json.loads(result['choices'][0]['text'])['action']
  if action not in ACTIONS:raise ValueError('Action out of range')
 except Exception as e:error=str(e);action='INVALID'
 record={'call_id':ident,'request':body,'response':result,'error':error,'action':action,'latency_s':time.perf_counter()-start,'python_peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
 append(ROOT/f'runs/{tag}_calls.jsonl',record);return action,record

def episode(task,env_seed,interface_seed,condition,split,tag,output=None):
 env=Environment(task,env_seed,split);c=controller(condition,interface_seed);steps=[]
 for _ in range(HORIZON):
  frames=env.advance();sig=c.signal(frames,task);action,call=llm(env,sig,tag);outcome=env.step(action)
  steps.append({'frames':frames,'signal':sig,'outcome':outcome,'call_id':call['call_id'],'latency_s':call['latency_s'],'usage':call['response'].get('usage',{}),'error':call['error']})
 result={'task':task,'env_seed':env_seed,'interface_seed':interface_seed,'condition':condition,'split':split,'summary':env.summary(),'steps':steps}
 if output:append(output,result)
 return result

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('command',choices=['graphs','train','smoke','test']);args=p.parse_args()
 if args.command=='graphs':print(make_graphs())
 elif args.command=='train':train();print('Readouts fitted using training episodes; four candidates selected on validation episodes.')
 else:
  is_test=args.command=='test';tag='test' if is_test else 'validation_v3';path=ROOT/f'runs/{tag}_episodes.jsonl'
  if path.exists():raise SystemExit('Refusing to overwrite existing run')
  if is_test:
   lock=json.loads((ROOT/'runs/protocol_lock.json').read_text())
   for f,digest in lock['hashes'].items():
    if sha(ROOT/f)!=digest:raise SystemExit(f'Frozen file changed: {f}')
  jobs=[(task,30000+i if is_test else 21000,seed,condition) for task in TASKS for i in range(3 if is_test else 1) for seed in (SEEDS if is_test else [11]) for condition in (CONDITIONS if is_test else ['alone','fly'])]
  np.random.default_rng(904).shuffle(jobs)
  for j,(task,s,seed,c) in enumerate(jobs):
   r=episode(task,s,seed,c,'test' if is_test else 'validation',tag,path)
   print(f'{j+1}/{len(jobs)} {task} {s} {seed} {c} complete',flush=True)
