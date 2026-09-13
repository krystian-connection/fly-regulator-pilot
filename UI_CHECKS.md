# Browser verification — 13 September 2026

- Executed `./Launch.command` successfully; existing local LM Studio model was reused and Python server bound to 127.0.0.1:8765.
- Browser loaded real HTML/JS/CSS without console errors. Layout and state labels visually inspected.
- Changed scenario to tools, seed 42, A reliability 0.2 and B reliability 0.8; Reset applied settings and cleared controller/history.
- Pressed Step and Stop. One real local completion chose B from three observed 0/1 health-probe pairs and controller recommendation B. The seeded tool attempt failed for -0.5. That real negative outcome is retained in exploration logs. UI showed action, state, scores, timing, tokens and outcome; it returned to idle at 1/6 decisions.
- Opened locked replay with all 126 episodes, selected measured fly/resources/scenario 30000/interface 11, and advanced the replay slider to decision 2. The paired table showed all seven conditions for the same scenario/interface seed. Replay required zero model calls.
- Four lifecycle tests verified seeded reset/state clearing, rejection of reset during an in-flight action, invalid overrides, and no inference from a stopped or complete run. These use actual environment/controller objects and no mocked model outputs.
- Invalid Host and foreign Origin received HTTP 400; unknown route received 404. No external assets or public hosting.
- The fresh-inference Compare all button is implemented using the same verified environment/controller/local-inference step path and freezes the selected configuration across conditions. Its entire 42-call browser sequence was not run during delivery, to respect the 1,000-call cap. All seven conditions were executed end-to-end by the locked pilot runner, and all seven are available in verified recorded replay.

Budget at completion: 999 conservative pilot reservations plus one browser verification call = 1,000. Further user exploration is a separate interaction, never retroactively used as test evidence.
