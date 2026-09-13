"""Adversarial saved-log consistency tests: verify the auditor rejects meaningful corruption."""
from pathlib import Path
import unittest,copy,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import verify_release as v
class VerifierTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=[v.jl(v.ROOT/'runs'/name) for name in ['test_episodes.jsonl','test_calls.jsonl','causal_probes.jsonl','probe_calls.jsonl']]
 def test_rejects_reward_change(self):
  d=copy.deepcopy(self.data);d[0][0]['steps'][0]['outcome']['reward']+=1
  with self.assertRaisesRegex(ValueError,'reward'):v.check_records(*d)
 def test_rejects_hidden_prompt_field(self):
  d=copy.deepcopy(self.data);d[1][0]['request']['prompt']=d[1][0]['request']['prompt'].replace('"history":[]','"history":[],"expected_future":1')
  with self.assertRaisesRegex(ValueError,'allowlist'):v.check_records(*d)
 def test_rejects_changed_probe_history(self):
  d=copy.deepcopy(self.data);d[3][0]['request']['prompt']=d[3][0]['request']['prompt'].replace('"energy":','"private_energy":',1)
  with self.assertRaisesRegex(ValueError,'Probe identical'):v.check_records(*d)
 def test_rejects_missing_episode(self):
  d=copy.deepcopy(self.data);d[0].pop()
  with self.assertRaisesRegex(ValueError,'counts'):v.check_records(*d)
if __name__=='__main__':unittest.main()
