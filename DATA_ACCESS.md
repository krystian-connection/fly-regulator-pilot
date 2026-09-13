# Exact data and limits of reproduction

The experiment used `Supplementary-Data-S1.zip` at revision `15e065f5c29f08c96ccd64ea8fe0f51510629009` of https://github.com/brain-networks/larval-drosophila-connectome, attributed to Winding et al., Science 2023, https://doi.org/10.1126/science.add9330 .

Archive SHA-256: `8c1f43809ed5d527ba61b154e377cc21da26383a75eda8aab85ce05607a72a4c`.
CSV member: `Supplementary-Data-S1/all-all_connectivity_matrix.csv`.
CSV SHA-256: `94d51a821217048acf711f4feb71693a8487f2547540c6f2f25896c60e2348e3`.
Source rows/columns are pre/post and are transposed to W[post,pre]. It contains 2,952 nodes, 110,677 directed pairs, 352,611 contacts and 537 self-pairs. No licence for this exact archive is asserted here.

The candidate does not download or redistribute the data. Readers must establish appropriate access/terms at the upstream source; links and checksums are provenance, not permission. We also omit all derived NPZs (including random controls and readouts) to avoid silently assuming which derivatives are distributable. Metadata and aggregate experiment outputs are retained.

After obtaining the correct archive under suitable terms, an independent reproducer can work in a NEW scratch copy: place it at `data/Supplementary-Data-S1.zip`; verify the archive digest; run `scripts/prepare_graph.py`, `scripts/check_anatomy.py`, `experiment.py graphs`, and `experiment.py train` using the pinned numerical environment. These are local numerical operations, not LLM inference. Preserve this candidate: generation commands write graph and tuning files and must not be run over released results. Inspect the reconstruction scripts before running them. Sparse archive bytes can depend on packaging/library details; check numerical invariants as well as hashes. This fresh reconstruction route has not been independently tested from this data-excluded candidate.

Fresh inference additionally requires an appropriately licensed model with the recorded checksum, the compatible local runtime and a new run directory/protocol/budget. The included run scripts intentionally guard against overwriting the historical test. Do not remove the lock or reset the old budget to claim another independent run. Exact Metal inference determinism is not guaranteed.
