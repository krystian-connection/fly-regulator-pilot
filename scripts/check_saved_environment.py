"""Reconstruct every held-out trajectory with the original seeded environment, no controllers/LLM."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
def deny(event,args):
 if event.startswith('socket.'):raise RuntimeError('Offline replay: sockets disabled')
sys.addaudithook(deny)
import experiment as e
rows=[json.loads(x) for x in (e.ROOT/'runs/test_episodes.jsonl').read_text().splitlines()]
for r in rows:
 env=e.Environment(r['task'],r['env_seed'],'test')
 for s in r['steps']:
  assert env.advance()==s['frames'],'Seeded observations differ'
  assert env.step(s['outcome']['action'])==s['outcome'],'Seeded scoring/outcome differs'
 assert env.summary()==r['summary'],'Seeded episode summary differs'
print(json.dumps({'status':'passed','seeded_episodes_reconstructed':len(rows),'all_observations_outcomes_and_summaries_equal':True,'new_llm_calls':0}))
