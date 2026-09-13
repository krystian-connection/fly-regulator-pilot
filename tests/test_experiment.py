import unittest,json
from pathlib import Path
import numpy as np
from scipy import sparse
import experiment as e

class HarnessTests(unittest.TestCase):
 def test_real_graph(self):
  w=sparse.load_npz(e.ROOT/'data/fly_raw.npz');self.assertEqual(w.shape,(2952,2952));self.assertEqual(w.nnz,110677);self.assertEqual(w.sum(),352611)
 def test_graph_matching_and_nontrivial_rewire(self):
  fly=sparse.load_npz(e.ROOT/'data/fly.npz');f=fly.tocoo()
  for seed in e.SEEDS:
   for kind in ['rewired','random']:
    w=sparse.load_npz(e.ROOT/f'data/{kind}_{seed}.npz');x=w.tocoo()
    self.assertEqual(w.shape,fly.shape);self.assertEqual(w.nnz,fly.nnz)
    np.testing.assert_allclose(np.sort(w.data),np.sort(fly.data),atol=1e-14)
    self.assertLessEqual(np.asarray(w.sum(1)).max(),.85000001)
    if kind=='rewired':
     np.testing.assert_array_equal(np.diff(w.indptr),np.diff(fly.indptr))
     np.testing.assert_array_equal(np.bincount(x.col,minlength=2952),np.bincount(f.col,minlength=2952))
     np.testing.assert_allclose(w.sum(1),fly.sum(1))
     self.assertGreater((w!=fly).nnz,fly.nnz)
 def test_degree_signature_excludes_relabel(self):
  # General pair swap example changes edges without renaming vertices.
  from collections import Counter
  a=[(0,1),(2,3),(0,2)];b=[(0,3),(2,1),(0,2)]
  self.assertEqual(Counter(x for x,y in a),Counter(x for x,y in b));self.assertEqual(Counter(y for x,y in a),Counter(y for x,y in b));self.assertNotEqual(set(a),set(b))
 def test_reproducible_exogenous_schedule(self):
  for task in e.TASKS:
   a=e.Environment(task,123);b=e.Environment(task,123)
   for j in range(6):
    fa=a.advance();fb=b.advance();self.assertEqual([f['gauges'] for f in fa],[f['gauges'] for f in fb]);a.step('A');b.step('B')
 def test_no_future_observation(self):
  env=e.Environment('tools',30000);frames=env.advance()
  allowed={'tick','energy','remaining_decisions','values','costs','gauges','changed','last_action','last_failed','progress'}
  for f in frames:self.assertEqual(set(f),allowed)
  env2=e.Environment('tools',30000);env2.changes=[16];self.assertEqual(frames,env2.advance())
 def test_invalid_and_quit_penalized_full_horizon(self):
  for task in e.TASKS:
   env=e.Environment(task,12)
   self.assertFalse(env.summary()['success'])
   for i in range(6):env.advance();out=env.step('QUIT');self.assertEqual(out['reward'],-2.)
   self.assertEqual(env.total,-12.);self.assertFalse(env.summary()['success'])
   with self.assertRaises(ValueError):env.advance()
 def test_resources_no_reward_when_insufficient(self):
  env=e.Environment('resources',12);env.energy=0;env.advance();out=env.step('A');self.assertEqual(out['reward'],-2.);self.assertEqual(env.energy,0);self.assertEqual(env.progress,0)
 def test_tools_hand_calculation(self):
  env=e.Environment('tools',12);env.advance();env.outcomes[:]=0;env.last=0
  self.assertAlmostEqual(env.step('B')['reward'],1.4);env.advance();env.outcomes[:]=1
  self.assertAlmostEqual(env.step('B')['reward'],-.5);env.advance();self.assertAlmostEqual(env.step('C')['reward'],-.4)
 def test_reset_and_decay(self):
  frames=e.Environment('resources',5).advance()
  for condition in ['simple','fly','random','rewired']:
   c=e.Controller(condition,11);d=e.Controller(condition,11);np.testing.assert_array_equal(c.features(frames,'resources'),d.features(frames,'resources'))
   start=c.x.copy()
   for _ in range(150):c.x=(1-c.leak)*c.x+c.leak*np.tanh(c.w@c.x if c.graph else np.zeros(16))
   self.assertTrue(np.isfinite(c.x).all());self.assertLess(np.max(np.abs(c.x)),1e-7);self.assertGreater(np.max(np.abs(start)),.01)
 def test_reset_ablation(self):
  frames=e.Environment('tools',8).advance();c=e.Controller('fly_reset',11);a=c.features(frames,'tools');b=c.features(frames,'tools');np.testing.assert_array_equal(a,b)
 def test_disconnection(self):
  c=e.Controller('fly_disconnected',11);s=c.signal(e.Environment('tools',5).advance(),'tools');self.assertEqual(s['recommendation'],'NONE');self.assertEqual(s['scores'],[0.,0.,0.]);self.assertGreater(s['state_rms'],0)
 def test_splits_change_patterns_disjoint(self):
  seq=[tuple(e.Environment('tools',0,x).changes) for x in ['train','validation','test']];self.assertEqual(len(set(seq)),3)
if __name__=='__main__':unittest.main()
