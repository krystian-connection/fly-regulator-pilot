import zipfile,io,csv,json
import numpy as np
from scipy import sparse
z=zipfile.ZipFile('data/Supplementary-Data-S1.zip')
def table(n):return list(csv.reader(io.TextIOWrapper(z.open('Supplementary-Data-S1/'+n))))
raw=table('all-all_connectivity_matrix.csv');ids=raw[0][1:];a=sparse.load_npz('data/fly_raw.npz').toarray().T
parts=np.zeros_like(a)
for n in ['aa','ad','da','dd']:
 t=table(n+'_connectivity_matrix.csv');m={r[0]:r[1:] for r in t[1:]};cols={v:i for i,v in enumerate(t[0][1:])}
 for i,id in enumerate(ids):
  if id in m:
   row=m[id]
   for j,jd in enumerate(ids):
    if jd in cols and row[cols[jd]]:parts[i,j]+=float(row[cols[jd]])
inputs=table('inputs.csv');outputs=table('outputs.csv');im={r[0]:sum(float(x or 0) for x in r[1:]) for r in inputs[1:]};om={r[0]:sum(float(x or 0) for x in r[1:]) for r in outputs[1:]}
rec={'compartment_sum_equals_all_all':bool(np.array_equal(parts,a)), 'fraction_rows_not_exceeding_output_totals':float(np.mean([a[i].sum()<=om[id] for i,id in enumerate(ids)])), 'fraction_columns_not_exceeding_input_totals':float(np.mean([a[:,i].sum()<=im[id] for i,id in enumerate(ids)])), 'note':'External inputs/outputs exceed within-brain contacts, so totals need not equal. Blank CSV entries represent absent contacts.'}
open('data/anatomy_audit.json','w').write(json.dumps(rec,indent=2));print(rec)
