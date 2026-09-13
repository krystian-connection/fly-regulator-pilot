"""Control lifecycle tests using an already-completed sandbox; never mock model output."""
import unittest,threading
from web import server as w
import experiment as e
class WebControls(unittest.TestCase):
 def test_reset_clears_memory_and_uses_seed(self):
  config={'task':'tools','condition':'fly','seed':42,'interface_seed':11,'overrides':{'reliability_a':.2,'reliability_b':.8}}
  w.reset(config);one=w.session['env'].advance();w.session['controller'].features(one,'tools');self.assertGreater(abs(w.session['controller'].x).max(),0)
  w.reset(config);self.assertEqual(w.session['env'].advance(),one);self.assertEqual(abs(w.session['controller'].x).max(),0)
 def test_stop_and_complete_do_not_issue_llm_calls(self):
  w.reset({'task':'resources','condition':'alone','seed':9,'interface_seed':11});env=w.session['env']
  for _ in range(6):env.advance();env.step('C')
  def exploration_calls():
   import json
   return [x['id'] for x in map(json.loads,(e.ROOT/'runs/call_ledger.jsonl').read_text().splitlines()) if x['tag']=='explore']
  before=exploration_calls()
  w.running=True;w.do_step();self.assertFalse(w.running)
  w.running=False;w.loop(w.generation)
  self.assertEqual(before,exploration_calls())
 def test_reset_rejects_inflight_action(self):
  w.step_lock.acquire()
  try:
   with self.assertRaises(ValueError):w.reset({})
  finally:w.step_lock.release()
 def test_invalid_overrides(self):
  for overrides in [{'reliability_a':2},{'recharge':-1},{'hidden_answer':1}]:
   with self.assertRaises(ValueError):w.reset({'overrides':overrides})
if __name__=='__main__':unittest.main()
