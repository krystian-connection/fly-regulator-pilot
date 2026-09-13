"""Read numeric CSV from pinned supplement; never execute archive content."""
import csv,io,zipfile,json,hashlib
from pathlib import Path
import numpy as np
from scipy import sparse
p=Path('data/Supplementary-Data-S1.zip');z=zipfile.ZipFile(p)
name='Supplementary-Data-S1/all-all_connectivity_matrix.csv'
b=z.read(name);r=csv.reader(io.StringIO(b.decode()));ids=next(r)[1:];a=[]
for i,row in enumerate(r):
 assert row[0]==ids[i]
 a.append([float(v) if v else 0 for v in row[1:]])
a=np.array(a);assert a.shape==(len(ids),len(ids)) and np.isfinite(a).all() and (a>=0).all()
assert np.equal(a,np.floor(a)).all()
# CSV rows = presynaptic, columns = postsynaptic; recurrence uses W[post,pre].
w=sparse.csr_matrix(a.T);sparse.save_npz('data/fly_raw.npz',w)
Path('data/neuron_ids.json').write_text(json.dumps(ids))
manifest={'source':'Winding et al. 2023 Science, Supplementary Data S1; mirror brain-networks/larval-drosophila-connectome','revision':'15e065f5c29f08c96ccd64ea8fe0f51510629009','archive_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'csv_sha256':hashlib.sha256(b).hexdigest(),'derived_sha256':hashlib.sha256(Path('data/fly_raw.npz').read_bytes()).hexdigest(),'nodes':len(ids),'edges':w.nnz,'synapses':int(w.sum()),'self_loops':int(np.count_nonzero(w.diagonal())),'filter':'None; all 2952 rows of supplied all-all matrix, no threshold, no core selection. This supplied graph is not all 3016 neurons reported in final paper.','orientation':'CSV pre rows/post columns transposed to W[post,pre]','signs':'Nonnegative counts; no transmitter inference; engineered rate operator, not biophysical excitation claims.'}
Path('data/manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
