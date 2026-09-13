# Fly regulator lab — release candidate 0.1.0-rc3

**A controlled pilot found no convincing benefit from measured fly wiring or persistent fly state.** This package lets readers inspect the experiment and reproduce its saved-result analysis. It is not evidence that biological connectivity cannot help other models, tasks or dynamical regimes.

Status: prepared locally, not published or independently reviewed. Author: Krystian Turek. Contact: krystian@connection-london.org. Repository: https://github.com/krystian-connection/fly-regulator-pilot. MIT code and CC BY 4.0 report/results licensing were approved by the author on 13 September 2026. Final public upload approval remains pending. See REPORT.md for a short paper draft, RESULTS.md for full outcomes, and REVIEWER_GUIDE.md for the review request.

## Start without a model or dataset

1. Open `replay.html` in a browser. It contains all 126 saved episodes and makes no network requests. Select a task, scenario, interface seed and decision to compare all seven conditions. This is recorded replay, not fresh inference.
For optional localhost viewing, run `python3 scripts/serve_replay.py` and open http://127.0.0.1:8766 . It serves only this static page.

2. Run `python3 scripts/verify_release.py` for file integrity, call matching, public-history boundaries, score reconstruction and paired-effect checks. This uses only the Python standard library.
For exact seeded environment reconstruction without a controller or model, run `python -B scripts/check_saved_environment.py` in the pinned numerical environment.

3. To reproduce the original bootstrap and tables, use an isolated environment with Python 3.14.7 and the pinned dependencies in `requirements.txt`, then run `python -B scripts/reproduce_saved.py`. This uses existing logs only, disables Python socket connections in the analysis child processes, and computes in a temporary directory. It never calls an LLM or writes the released results.

For a new environment, the commands are `python3.14 -m venv /tmp/fly-review-env`, `/tmp/fly-review-env/bin/python -m pip install -r requirements.txt`, and `/tmp/fly-review-env/bin/python -B scripts/reproduce_saved.py`. Dependency installation accesses the package registry; the verification and analysis commands do not. The candidate contains no binaries, model weights or installed dependencies. Package versions are pinned, but these install instructions are not a hash-locked cross-platform wheel distribution; installed artifact fingerprints from the original Mac are retained in `runs/dependency_manifest.json`.

## What is and is not reproducible from this package

Saved score arithmetic, all task/condition results, uncertainty intervals, token/latency totals and intervention checks are reproducible without the connectivity archive or local model. Python 3.14.7 / NumPy 2.4.3 / SciPy 1.17.1 is the tested analysis environment. Results may require tolerance for floating-point differences on other platforms.

**A complete fresh controller/LLM reproduction is not self-contained.** The measured archive, graph derivatives and all fitted readouts are excluded pending archive-specific licence clarification. Model weights and the proprietary runtime are also absent. DATA_ACCESS.md documents the exact source, checksum and reconstruction sequence for readers who obtain appropriate access. Original graph-dependent tests cannot run from this package alone. Do not interpret their retained historical pass logs as a new clean-machine reproduction.

The original execution code, protocol and experiment-specific scripts are included for inspection, with their original hashes. The interactive live UI source is retained in `web/`; its launch reference is `original/Launch.command`. That launcher belongs to the original configured Mac environment and is not the release's entry point. The release entry point is the offline replay above. Source documents RESULTS.md and original/README.md refer to local-only artifacts and the original live UI; this availability statement governs the candidate.

## Research and integrity record

- PROTOCOL.md: local before-test plan, not external preregistration.
- RESEARCH.md: related primary work, limited novelty search, provenance and separate licences.
- REPORT.md and RESULTS.md: findings, uncertainty, harms, limitations and next experiment.
- runs/test_* and runs/probe_calls.jsonl: synthetic test and intervention requests/responses, with response identifiers and exact response timestamps removed in rc2.
- runs/validation* and runs/development_v*_experiment.py: development records; the first two validation batches are contaminated and INVALID as efficacy evidence. Do not pool them with test results.
- runs/posthoc_task_sanity.json: post-test diagnostic, not a preregistered or fair baseline.
- RELEASE_MANIFEST.json: original-to-release mappings and every sanitisation. runs/machine.json is sanitised and intentionally differs from its original protocol-lock hash; absent graph/readout files are not silently treated as verified.
- SHA256SUMS.json: final candidate contents. These are local integrity records, not proof of independent timestamping or external replication.

LICENSE covers original project code/task definitions only. See RIGHTS.md for author-approved documentation/result terms and excluded upstream material. No cloud inference, account setup, model service or public-facing server is required to inspect saved results. Do not expose the original live inference server to the internet.

## Privacy and release use

PRIVACY_AUDIT.md describes the rc2 checks and remaining exposure. API response IDs, response creation timestamps, the redundant runtime fingerprint, and the OS patch-version field were removed. The reservation ledger retains IDs, tags and order with elapsed seconds replacing exact wall-clock times. Prompts, responses' experimental content, failures, actions, usage, latency, outcomes and result tables are preserved. Original local logs and the sealed rc1 remain immutable; release sanitisation is recorded in RELEASE_MANIFEST.json. Historical documents describe the original experiment or rc1, not a claim that every rc2 log is byte-identical to the original.

Hardware class, scientific software versions, study date, and the historical protocol-freeze time remain for provenance and timing interpretation. No affiliation is implied by the contact domain. This is research software, with no production-safety or biological-superiority claim.

Use the offline entry points above for this release. The retained historical live runner writes local process identifiers and executable paths to new memory logs; those newly generated logs require a separate privacy review before sharing. Do not publish this working directory, its Git history, or future run files automatically. Publish only the reviewed release allowlist. The original live model server is not a public demonstration service.

This rc3 revision changes only release documentation, licence notices, citation metadata and the replay version label. All code, logs, episode data, analysis and privacy removals match rc2. Historical rc1/rc2 audits retain their dated approval states; RIGHTS.md records the current licence approval.
