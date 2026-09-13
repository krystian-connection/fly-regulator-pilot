"""Separate pass: reconstruct score from logged public frames/outcomes, inspect exact prompts."""
from pathlib import Path
import json,sys,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import experiment as e

def audit(tag):
 rows=[json.loads(l) for l in (e.ROOT/f'runs/{tag}_episodes.jsonl').read_text().splitlines()];calls={c['call_id']:c for c in map(json.loads,(e.ROOT/f'runs/{tag}_calls.jsonl').read_text().splitlines())};errors=[]
 for r in rows:
  assert len(r['steps'])==6
  energy=r['steps'][0]['frames'][0]['energy'];total=0;prev=None;violations=0;completed=0
  for i,s in enumerate(r['steps']):
   out=s['outcome'];a=out['action'];f=s['frames'][-1];reward=0
   if a not in ['A','B','C']:reward=-2;violations+=1
   elif r['task']=='resources':
    if a=='C':energy=min(6,energy+3);reward=-.1
    else:
     j=['A','B'].index(a);cost=f['costs'][j]
     if energy<cost:reward=-2;violations+=1
     else:energy-=cost;reward=f['values'][j];completed+=1
   elif a=='C':reward=-.4
   else:
    reward=(-.3 if out['failed'] else 2)-.2-.4*int(prev in ['A','B'] and a!=prev);completed+=int(not out['failed'])
   assert math.isclose(reward,out['reward'],abs_tol=1e-9),(r,i,reward)
   total+=reward;prev=a
   c=calls[s['call_id']];assert c['request']['max_tokens']==32 and c['request']['temperature']==0
   prompt=c['request']['prompt'];user=json.loads(prompt.split('<|im_start|>user\n')[1].split('<|im_end|>')[0]);assert set(user)=={'rules','observations','history','controller'}
   assert len(user['observations'])==3*(i+1) and len(user['history'])==i
   assert not any(k in prompt for k in ['resource_rates','env_seed','interface_seed','outcomes','expected_future'])
   # 'expected_regret' is a SCORING-ONLY latent metric. It must never be in model history.
   assert 'expected_regret' not in prompt,'Scoring-only latent information leaked into history'
  assert math.isclose(total,r['summary']['return'],abs_tol=1e-9)
  assert violations==r['summary']['violations'] and completed==r['summary']['progress']
 return {'tag':tag,'episodes':len(rows),'calls':len(calls),'status':'passed'}
if __name__=='__main__':
 result=audit(sys.argv[1]);e.dump(e.ROOT/f'runs/{sys.argv[1]}_audit.json',result);print(result)
