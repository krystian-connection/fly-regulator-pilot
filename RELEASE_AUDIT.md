# Release preparation audit — rc3, 13 September 2026

This documentation-only revision records the author's MIT/CC BY 4.0 approval and the actual private GitHub repository. Final public upload approval and independent review remain pending. See RIGHTS.md for current licence scope. Author, contact and human/AI contribution roles are unchanged.

All scientific code, protocol, logs, episode records and analysis are byte-identical to privacy-audited rc2. Its numerical analysis, seeded reconstruction and corruption-rejection checks therefore apply to the same inputs and implementations; those tests were not redundantly rerun. Current verification checks the full file allowlist, new checksums, privacy patterns, exact preservation of scientific files, and the extracted archive's standard-library saved-record verifier. No new inference or uploads occurred. External ARCHIVE_VERIFICATION-rc3.json records the final checksum and results.

## Historical rc2 audit

The historical text below describes approval states and checks at rc2 preparation time. Licence approval is now recorded in RIGHTS.md; no public release or independent review is claimed.

# Release preparation audit — rc2, 13 September 2026

Current privacy revision: see PRIVACY_AUDIT.md and CHANGELOG.md. Author remains Krystian Turek, contact krystian@connection-london.org. The original human/AI contribution statement is preserved. This package remains local and unpublished, with final author approval and independent review pending.

Current checks passed: saved-record verifier (126 episodes, 756 test calls, 48 probe calls, 1,000 historical reservations), exact reconstruction of all seeded observations/outcomes/summaries, numerical analysis equality and three byte-identical CSVs, and four corruption-rejection tests. Semantic comparisons verify that log edits remove only declared metadata. Frozen scientific code and original local records remain unchanged. No fresh inference, new graph-dependent testing, public upload or external messages occurred. Replay edits change only the version label and contact text; the embedded episodes and executable JavaScript are unchanged. Browser coverage below is historical rc1 coverage, not a newly performed rc2 browser test.

The final seal and external ARCHIVE_VERIFICATION-rc2.json record directory/archive integrity and privacy scan outcomes. The review scope and residual exposure are in PRIVACY_AUDIT.md. These are same-agent checks, not independent assurance or proof that future harm is impossible.

## Historical rc1 audit, preserved below for provenance

The following describes rc1 before rc2 metadata removal and email addition. Its no-email result and historical test/browser statements apply to that prior candidate.

# Release preparation audit — 13 September 2026

Status: local candidate prepared; publication and independent human review pending. Public author name Krystian Turek confirmed; natural-language direction and Codex execution roles disclosed separately. No new inference, downloads or uploads occurred in this preparation. No reviewer or maintainer messages were sent.

## Checks actually completed

- Original 38 protocol hashes verified; every original file in runs/ and data/ plus locked source files remained unchanged through preparation.
- Explicit allowlist selected project files. No model/graph/readout binaries, third-party research source copies, user instructions, interactive exploration logs, .git or .venv included.
- Full selected text scanned for personal home paths, email addresses, private-key headers and common credential formats. No matches. Selected log schemas and machine/process metadata reviewed; this is not proof that every possible sensitive string is detectable.
- Machine record sanitised by an explicit field allowlist; original hash preserved in the manifest. 860 process-memory samples aggregated with exactly the frozen analyzer's selection, with personal paths, PIDs, unrelated processes and timestamps removed. Aggregate memory results reproduced unchanged.
- Standard-library saved-record verifier passed: 126 episodes, 756 test calls, 48 probe calls, exact public observation/history equality, response/action consistency, reward/energy/success/switch/retry/recovery arithmetic, neutral ablation, token costs and budget ledger. Only one of 18 primary pairs differs. The protocol-lock subset is explicit: 14 byte-identical included files, 1 sanitised machine file, 23 excluded NPZ files.
- The original analyzer and scorer were executed against a temporary copy with Python socket operations blocked. Analysis JSON matched numerically; all three CSVs matched byte for byte. No released analysis outputs were overwritten.
- All 126 seeded environments were reconstructed with original code, without controllers/model calls. Every observation, outcome (including secondary scorer fields) and summary matched exactly.
- Original 16 unit/lifecycle tests passed again on the existing local graph installation without inference. These were not run from a data-excluded clean machine; historical test logs are included separately.
- Four adversarial verifier tests passed: altered reward, hidden prompt field, mismatched probe history and missing episode were rejected.
- Browser replay rendered all seven conditions for all 18 task/scenario/interface combinations. Task/scenario/interface/detail selectors and previous/next controls were exercised; the final next button was disabled at decision six. The primary-difference case showed fly advice B / LLM action A / reward 1.4, versus simple advice A / LLM action C / reward -0.4. The page's CSP disallows connections and contains no fetch/XHR/socket calls.
- The static localhost server initially encountered a sandbox bind restriction; an approved sandbox escalation started it on 127.0.0.1:8766. It serves only the embedded replay file. This is not a system installation or a public server.

## Limits and release gates

All these checks were performed by the same implementing agent, using the original Mac's interpreter/dependencies. No independent reviewer, clean-machine fresh inference or peer review has occurred. The four corruption tests cover meaningful verifier cases but are not exhaustive security testing. The original live UI source is included for inspection; the data-excluded candidate's verified entry point is recorded replay. The full fresh graph/readout rebuild cannot be validated from the package alone.

Do not redistribute excluded graph/readout artifacts until exact terms are established. Do not call the locally frozen protocol externally preregistered. Keep the two contaminated validation batches excluded from efficacy estimates. Final author approval of the report, proposed documentation/results licence, publication destination and exact archive is still required before upload. Independent review is recommended before presenting this as a scientific publication.

SHA256SUMS.json seals this audit with the candidate contents. The outer archive checksum and extraction-verification record are retained beside the archive. Checksums establish local file consistency, not an independently witnessed creation date.
