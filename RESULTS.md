# Results — local pilot, 13 September 2026

**The pilot did not establish an advantage from measured fly wiring or persistent fly state.** The regulator can change the local LLM’s actions, but the primary fly-versus-simple gain was tiny and concentrated in one paired episode. Random/rewired comparisons and the persistence ablation provide no convincing topology-specific benefit. Higher average return also came with worse resource-task success and more violations than the LLM alone.

## What actually ran

The existing Qwen3.5-4B Q4_K_S model ran locally through LM Studio 0.4.21+2 on this M3 Max / 64GB Mac. The language-model file was hashed and its weights/settings stayed fixed. All 2,952 neurons and 110,677 directed pairs in the supplied measured larval matrix participated, with no invented edges or neuron filtering. This supplied graph is smaller than the final paper’s headline connectome; the release and data-licence limitations are documented in RESEARCH.md.

The protocol and 38 execution/data/readout artifacts were frozen at **2026-09-13 14:05:32 UTC**, before test inference. Seven conditions × two tasks × three environment seeds × three graph/interface seeds × six decisions produced **126 complete episodes and 756 real local test calls**. All test calls returned valid actions; the separate scoring/leakage audit passed. All frozen hashes remained unchanged. There were 48 additional local calls for 24 paired causal probes.

The conservative initial count is **1,000 reservations/attempts including the live browser check**: 3 profiling attempts, 84 first validation calls, 84 second validation calls, 24 final sanitized validation calls, 756 test calls, 48 probes and 1 browser Step. One profiling attempt was blocked before reaching the server, so 999 requests actually reached local inference. One early real profiling response was truncated reasoning; it is retained. There were no paid inference APIs, model downloads or cloud uploads. Further user-driven browser exploration is separately logged and is not part of this pilot.

Two early validation batches are **invalid as efficacy evidence**: the separate audit found scoring-only latent reliability information in model history. An explicit public-history allowlist fixed this before the locked test. Their raw records and old code snapshots remain saved. Offline readout fitting used observed features and a separate numerical validation set, not those contaminated LLM histories.

## Objective outcomes

Each cell averages nine runs: three distinct seeded scenarios crossed with three interface seeds. These are not nine independent environments. Success requires four completed jobs/tool successes, zero violations and the full six-decision horizon.

| Condition | Resource return | Resource successes | Resource violations, total | Tool return | Tool successes |
|---|---:|---:|---:|---:|---:|
| LLM alone | 6.417 | 9/9 | 0 | -0.467 | 0/9 |
| Simple stateful | 7.637 | 6/9 | 3 | -0.167 | 0/9 |
| Random reservoir | 7.792 | 7/9 | 2 | -0.167 | 0/9 |
| Measured fly | 7.637 | 6/9 | 3 | 0.033 | 0/9 |
| Degree-preserving rewired | 7.787 | 8/9 | 1 | -0.167 | 0/9 |
| Fly reset each decision | 7.786 | 8/9 | 1 | 0.067 | 0/9 |
| Fly output disconnected | 6.417 | 9/9 | 0 | -0.467 | 0/9 |

The fly controller increased average resource return from 6.417 to 7.637 compared with the LLM alone, but reduced success from 9/9 to 6/9 and added three constraint violations. It had exactly the same resource return as the simple controller. Every condition failed the tool success threshold; this floor limits claims about practical adaptation even when returns differ.

## Paired uncertainty

The primary score divides resource return by 18 and tool return by 10.8, then averages the tasks equally. Positive differences below favour fly. Intervals use 10,000 paired bootstrap draws resampling environment seeds within task and interface seeds jointly across conditions. No decision step is treated as an independent sample. With only three environment seeds per task and three interface seeds, these are fragile descriptive intervals, not a confirmatory population test.

| Fly minus comparator | Mean scaled-return difference | Descriptive 95% interval |
|---|---:|---:|
| simple | +0.0093 | [+0.0000, +0.0370] |
| alone | +0.0570 | [-0.1189, +0.2028] |
| random | +0.0049 | [-0.0130, +0.0370] |
| rewired | +0.0051 | [-0.0259, +0.0394] |
| fly_reset | -0.0057 | [-0.0645, +0.0433] |
| fly_disconnected | +0.0570 | [-0.1189, +0.2028] |

The **primary fly-minus-simple difference is +0.0093**, interval **[0.0000, +0.0370]**. Seventeen of the 18 paired cells had identical returns. The entire gain came from tools/scenario 30001/interface 47: on decision four, fly chose A and earned 1.4; simple inspected (C) for −0.4. This single 1.8-point event is insufficient evidence of sustained adaptation. The bootstrap’s zero lower endpoint must not be treated as proof that harm is impossible outside these few episodes.

Neither the random nor degree-preserving rewired comparison excludes zero. Resetting fly state before every decision slightly improved the pooled point estimate (fly-minus-reset −0.0057). The evidence therefore does not favour measured topology or persistent cross-decision state. Even the ordinary fly-versus-alone gain has a wide interval spanning harm and benefit.

## Did controller output causally matter?

Yes, on some sampled states: replacing fly advice with the neutral block changed the LLM action in **7/24 paired probes** (29.2%): 3/12 resource probes and 4/12 tool probes. Each pair held the public state/history and model settings fixed. Repeated environment/interface structure means these 24 probes are not independent Bernoulli trials; the fractions are descriptive. They establish influence, not benefit.

All 18 complete fly-output-disconnected episodes reproduced the corresponding LLM-alone action sequences exactly. Fly state remained active internally but was causally disconnected from the action interface. In the normal fly arm, only 18.5% of selected actions matched the explicit recommendation; agreement is not itself a causal estimate.

## Adaptation and action costs

Recovery below is decisions until the next positive, violation-free reward after an observed change, averaged across both tasks; it is a coarse proxy, not full recovery of an optimal policy. Switching/retry columns are means per **tool episode**, with “unnecessary” judged from the scorer’s current latent expected utility (never exposed to the LLM). They do not price future information value.

| Condition | Recovery lag | Tool switches | Tool unnecessary switches | Tool retries after failure | Tool unnecessary retries |
|---|---:|---:|---:|---:|---:|
| LLM alone | 1.17 | 0.00 | 0.00 | 0.67 | 0.67 |
| Simple stateful | 1.08 | 1.00 | 0.67 | 0.67 | 0.67 |
| Random reservoir | 1.08 | 1.00 | 0.67 | 0.67 | 0.67 |
| Measured fly | 0.92 | 1.11 | 0.78 | 0.67 | 0.67 |
| Degree-preserving rewired | 1.08 | 1.00 | 0.67 | 0.67 | 0.67 |
| Fly reset each decision | 0.89 | 1.00 | 0.78 | 0.78 | 0.78 |
| Fly output disconnected | 1.17 | 0.00 | 0.00 | 0.67 | 0.67 |

Fly had a shorter descriptive recovery lag than simple, but more unnecessary tool switching. Resource violations and failed tool success prevent interpreting that single recovery proxy as overall superior control. Complete episode metrics, including expected tool regret and work completions, are in the CSV/JSON results.

## Compute, tokens and memory

| Condition | Controller ms/decision | Local LLM seconds/call | Mean prompt tokens | Mean output tokens |
|---|---:|---:|---:|---:|
| LLM alone | 0.110 | 1.172 | 1031.4 | 6.0 |
| Simple stateful | 0.146 | 1.249 | 1036.9 | 6.0 |
| Random reservoir | 0.655 | 1.079 | 1036.9 | 6.0 |
| Measured fly | 0.627 | 1.046 | 1036.8 | 6.0 |
| Degree-preserving rewired | 0.715 | 1.224 | 1037.0 | 6.0 |
| Fly reset each decision | 0.659 | 1.443 | 1036.8 | 6.0 |
| Fly output disconnected | 0.695 | 1.205 | 1031.4 | 6.0 |

Test inference used **787,231 total tokens** and **909.1 seconds of summed request latency** (~15.2 minutes). The fixed output cap was 32 tokens and context cap 4,096; actual prompts stayed below the cap without truncation. Advice/history differences cost roughly five additional prompt tokens on average in active arms. Timing differences between LLM conditions include caching/order and machine noise; they are not a demonstrated controller speedup. The direct fly controller cost was ~0.63 ms per decision, about 0.48 ms above simple and below 0.1% of average LLM latency. Graph loading/initialization is outside this per-decision timing.

Each recurrent CSR graph occupies **1,339,936 bytes (~1.28 MiB)** and its float64 state 23,616 bytes, plus small mapping/pooling/readout arrays. The evaluator’s recorded Python peak RSS was **64.0 MiB**. LM Studio reported **3.65 GiB** when loading the model. Peak summed LM Studio/backend process RSS during evaluation was **11.79 GiB**; it includes app/runtime processes and can double-count shared pages, so it is neither incremental model memory nor a complete measurement of Metal/unified memory allocation. Raw samples are retained.

All selected neuron leaks were 0.5. Each graph arm used identical dynamics, state size, sparsity, normalized weight/sign multiset, input/output capacity and four-candidate tuning budget. Rewiring preserved every neuron’s in/out degree and incoming strength, with ten accepted swaps per edge; only ~3.3–3.4% of original edges remained. It changed outgoing strengths and self-loop counts. Random graphs intentionally differed in degree/strength placement. Conservative shared normalization bounds incoming sums by 0.85; fly/rewired maximum is ~0.2604. Half-amplitude undriven decay was about two ticks for fly, and amplitude fell below 0.001 within 14 ticks. This is a short-memory operating regime.

## Post-test floor diagnostic and limitations

After observing zero tool successes, a separate **post-hoc**, non-LLM diagnostic ran the fixed observable heuristic on the unchanged test scenarios. It succeeded on all three tool scenarios, with returns 5.4, 7.7 and 5.4. An exhaustive clairvoyant action search also confirmed that success was attainable in every scenario; that search sees future outcomes and is only a scoring/attainability check, never training data or a fair agent baseline. No parameters, tasks or primary outcomes were changed afterward.

The immediate bottleneck is the LLM’s use of observed telemetry/advice, not demonstrated lack of a sufficiently elaborate graph. The explicit closed-reasoning completion template and short JSON output budget may suppress planning; this tests one decoding configuration, not the full capability of the model. Short episodes, three scenario seeds, artificial dense input ports, nonnegative anatomical coupling, conservative dynamics and a myopic engineered teacher all limit the result. The full public history already gives the LLM memory; a fly-only improvement could not automatically be attributed to anatomy. The readout has 51 fitted coefficients plus 32 matched training-derived centering/scaling constants. The supplied S1 graph and its unresolved archive-specific redistribution licence also limit generalization and sharing.

These are new synthetic tasks, not reproduced EVAAA or conn2res benchmarks. The research review found close precedents, including a frozen larval rate-operator study; no guaranteed novelty, living-fly mechanism or biological superiority is claimed. The separate harness review is a second pass by the implementation agent, not independent human replication.

## Most informative next experiment

First validate an interface that lets the frozen LLM reliably use tool health evidence, and include the direct observable heuristic as a formal baseline. Apply any feasibility guard or prompt clarification equally to all conditions. Require non-floor validation success before spending on a larger topology test. Then use longer episodes and more independent change schedules, compare persistent/reset states across validated decay settings, and retain matched random/rewired controls. This would distinguish an interface failure from useful state memory before asking whether exact measured wiring helps. **No larger run has been started; it requires a new approved budget and protocol.**

## Try it and inspect the record

Open **http://127.0.0.1:8765** while the local server is running, or double-click **Launch.command** and open that address. Run/Stop/Step/Reset, scenario overrides and recorded condition replay are available. One live browser Step used the real local model; Stop allowed the in-flight decision to finish; no further model calls were made. Reset/stop lifecycle and boundary tests passed. The saved replay contains all 126 episodes. Live exploration is separate and never modifies this locked result. Three plain-English Codex example requests are in README.md.

- `runs/test_episodes.jsonl`, `runs/test_calls.jsonl`: complete raw test episodes and API requests/responses.
- `runs/causal_probes.jsonl`, `runs/probe_calls.jsonl`: matched intervention records.
- `runs/analysis.json`, `runs/condition_summary.csv`, `runs/episode_summary.csv`, `runs/paired_intervals.csv`: machine-readable results.
- `runs/protocol_lock.json`, `runs/delivery_verification.json`, `runs/test_audit.json`: frozen hashes and integrity/audit outcomes.
- `runs/call_ledger.jsonl`, `runs/profile.jsonl`, `runs/memory_samples.jsonl`: costs and failures.
- `runs/posthoc_task_sanity.json`: explicitly labelled post-test diagnostic.
- `HARNESS_REVIEW.md`, `RESEARCH.md`, `PROTOCOL.md`: methodology, limitations and source/licence record.
