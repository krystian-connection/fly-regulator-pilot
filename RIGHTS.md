# Rights and release boundary — checked 13 September 2026

This is a local release candidate, not a completed legal clearance. Scope is deliberately limited; no downstream rights are inferred from public access alone.

| Material | Recorded terms | Candidate handling |
|---|---|---|
| Original code and synthetic task definitions | Existing project MIT notice | Included with original notice; author confirmed MIT on 13 September 2026 |
| New report, documentation and original synthetic results | CC BY 4.0 for rights the owner can grant | Author approved on 13 September 2026; notice in LICENSE-REPORT-RESULTS.md |
| Winding supplementary archive and derived connectivity/readouts | Archive-specific redistribution licence unverified | Excluded, including NPZ files and neuron identifiers |
| Qwen3.5-4B and Unsloth quantisation | Model cards declare Apache-2.0; exact installed file hashed | No weights included; model-output records reviewed as synthetic experiment evidence, not a grant over model assets |
| LM Studio | Proprietary existing runtime | No binaries included |
| NumPy/SciPy | BSD-family and bundled notices, recorded in dependency manifest | No dependencies vendored; installation retains upstream terms |
| Reference repositories/papers | Separate terms in RESEARCH.md | Citations/URLs only; no copied upstream source files, articles or figures bundled |

The Cambridge repository currently identifies its available file as a preprint and gives CC BY 4.0 for that item. It does not expose the exact measured archive in the inspected record. Its abstract counts also differ from the final publication. The mirror's cached metadata had no separate licence; a fresh web fetch failed. The publisher's supplement could not be verified through the browser. No conclusion that the exact archive is licensed for redistribution follows from these checks. DATA_ACCESS.md records the exact excluded source and access limits.

Sources: https://www.repository.cam.ac.uk/items/5a5f1f5e-5efe-45e4-bd93-051d669215ac ; https://github.com/brain-networks/larval-drosophila-connectome ; https://doi.org/10.1126/science.add9330 ; https://huggingface.co/Qwen/Qwen3.5-4B ; https://huggingface.co/unsloth/Qwen3.5-4B-GGUF . The frozen RESEARCH.md records the earlier detailed inspection; it has not been rewritten after the experiment.

## Licence scope and approval

Krystian Turek approved MIT for original code and CC BY 4.0 for the report and synthetic results on 13 September 2026. LICENSE preserves the existing MIT notice and its code/task-definition scope. LICENSE-REPORT-RESULTS.md states the CC BY 4.0 grant for the original report, supporting documentation and synthetic result records. These apply to different materials; the two identifiers in CITATION.cff do not offer a choice of licence for every file. Excluded connectivity, models and third-party assets are not licensed by this grant.

Authorship remains Krystian Turek and the public contact remains krystian@connection-london.org. Human direction and Codex implementation/execution/analysis/drafting roles are unchanged. No affiliation, sponsorship, independent review or complete copyright clearance is implied. This licence approval is separate from approval to upload the final archive or make the repository public.
