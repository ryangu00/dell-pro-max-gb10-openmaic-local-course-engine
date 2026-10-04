# Complete results and evidence boundaries

All historical results here come from the supplied fact sheet. Original records,
logs and course prose are not distributed, and this publication did not independently
rerun the application. No values are filled in from a newer model or engine.
Measured durations, derived aggregates, single-reader observations and estimates
are labelled separately. Fixture constants are not historical measurements.

## Setting

Conditions: the recorded deployment on 2026-09-12, n=1 course; dependency ranges are not resolved-version measurements.

| Component | Recorded setting |
|---|---|
| Engine | OpenMAIC 1.0.1; changelog dated 2026-09-06; upstream main commit `d5be393`, committed 2026-09-11; depth-1 checkout |
| Framework | Next.js 16.2.11, Turbopack dev server, React 19.2.3 |
| SDK dependencies | `ai` `^6.0.168`, `@ai-sdk/openai` `^3.0.84`; declared ranges, not independently resolved versions |
| Toolchain | Node v22.22.3; requirement `>=22.19.0`, `.nvmrc` 22; pnpm 11.2.2 used although `packageManager` pins `pnpm@10.28.0`; no error observed |
| Installation | `pnpm install` completed; `node_modules` was 2.3 GB |
| Engine host | An Apple-silicon Mac desktop |
| Model server | Two Dell Pro Max with GB10 machines, vLLM tensor-parallel 2, DeepSeek V4 Flash Vision-Exp, served as `deepseek-v4-flash-vision-exp` |
| Endpoint mode | Fast-tier proxy injected `chat_template_kwargs: {"thinking": false}`; request-body confirmation was not captured |
| Storage and voice | Browser IndexedDB; no database, TTS or ASR service; narration remained text; Docker was not used for generation |
| Run window | 2026-09-12, 18:38 to 19:42 local time; generation 18:40 to 19:37; extraction 19:41 |

## Local-routing evidence

Conditions: 2026-09-12, n=1 course; file checks, UI observation, application logs and endpoint samples are distinct evidence layers.

| Layer | Observation | Conditions and limitation |
|---|---|---|
| Configuration | Four-line `.env.local`; zero cloud-key lines in the file check | 18:38; the process environment was not captured |
| UI | DeepSeek was server-managed and not editable; its model list contained one model | Observed once; no saved capture supports the list observation |
| Server events | All 16 generation events selected `deepseek:deepseek-v4-flash-vision-exp`; application error and warning counts were 0 | Final log had 263,315 lines; extracted URL hosts were limited to framework documentation, application loopback and the host's network address; outbound request URLs are not logged |
| Endpoint | Running requests 1.0 in all 30 one-minute samples; waiting 0.0 in direct probes at 18:41 and 18:47 | No other endpoint user during the run; activity coincided with generation |
| Unexplained provider | 2 LLM providers reported twice, at 18:38:40 and 18:39:25 | Only one provider was configured by the file; the second source was not identified |

The evidence supports the configured local generation path. It does not establish a cloud-key-free process or audited browser egress.

## Stage and scene timing

Conditions: n=1 course on 2026-09-12; local timestamps and POST durations; displayed rounding is retained.

| Stage / scene | Type | Start | Content call | Actions call | Scene total | Actions emitted |
|---|---|---|---|---|---|---|
| Outline | Structured JSON, streamed | 18:40:24 | 3.66 min (219 s; POST duration rounded to 3.6 min) | | 3.66 min | |
| Role profiles (4 roles) | | 18:44:04 | 61 s | | 1.02 min | |
| Scene 1 | slide | 18:45:08 | 358 s (6.0 min) | 43 s | 6.7 min | 8 |
| Scene 2 | interactive diagram | 18:51:54 | 668 s (11.1 min) | 66 s | 12.2 min | 8 |
| Scene 3 | slide | 19:04:08 | 216 s (3.6 min) | 90 s | 5.1 min | 9 |
| Scene 4 | slide | 19:09:15 | 443 s (7.4 min) | 120 s | 9.4 min | 11 |
| Scene 5 | slide | 19:18:37 | 560 s (9.3 min) | 144 s | 11.7 min | 9 |
| Scene 6 | slide | 19:30:21 | 234 s (3.9 min) | 83 s | 5.3 min | 10 |
| Scene 7 | quiz | 19:35:39 | 62 s (1.0 min) | 14 s | 1.3 min | 1 |
| Total | | 18:40:24 to 19:36:54 | | | 56.5 min | 56 |

## Derived timing aggregates

Conditions: arithmetic on the preceding measured table, n=1 course on 2026-09-12; these are derived values.

| Quantity | Value |
|---|---|
| Scene-content calls, sum | 42.35 min = 75% of wall time |
| Scene-actions calls, sum | 9.33 min = 16.5% |
| Outline plus roles | 4.7 min = 8.3% |
| Slides (n=5): content mean / range | 6.0 min / 3.6 to 9.3 min; with actions, 7.6 min / 5.1 to 11.7 min |
| Interactive (n=1) | 12.2 min, 21.6% of wall time from 1 of 7 scenes |
| Quiz (n=1) | 1.3 min |
| Planned teaching time (sum of outline's estimated durations) | 600 s (10 min); generation took 5.65x that |
| Gap between the end of one scene and the start of the next | 0.01 to 0.02 s (five times), 4.6 s once (first scene to second; the page loaded the classroom route, 4.3 s) |

## Endpoint samples

Conditions: 30 one-minute monitor samples, 18:48 to 19:18 on 2026-09-12; direct probes and the cumulative preemption counter have their own timestamps.

| Quantity | Value |
|---|---|
| Generation tokens per minute (30 samples) | median 2,890; mean 2,944; min 2,337; max 4,545 |
| Equivalent decode rate | median 48 tok/s; mean 49 tok/s; range 39 to 76 tok/s |
| Running requests | 1.0 in every sample; waiting 0.0 in the direct probes (18:41, 18:47) |
| Preemptions (cumulative counter at 18:59) | 0 |
| Errors during the run | 0 application error-severity entries; no HTTP error status on any generation POST (16 of 16 were 200) |
| Whole-run token estimate (E) | about 166,000 generated tokens (56.5 min times the 30-sample mean); the 9 saved JSON files total 75,530 bytes, so the tokens generated are several times what was kept; cause not isolated |

The whole-run token total is an estimate (E), not a before/after counter difference. Cumulative counters alone do not establish course-specific outcomes.

## Retained size versus content time

Conditions: n=1 course on 2026-09-12; approximate KB values as recorded, not newly converted.

| Scene | Retained scene size | Content-call time |
|---|---|---|
| Scene 3 | 6.6 KB | 216 s |
| Scene 4 | 5.3 KB | 443 s |

Similar retained size did not imply similar generation duration.

## Artifact structure

Conditions: n=1 course, extracted at 19:41 on 2026-09-12; metadata schema and counts only, with no generated prose or persona values.

| Part | Count and shape |
|---|---|
| Stage record | One JSON object with name, style and language metadata; 4 role configurations (1 teacher, 1 assistant, 2 students), each with persona and 3-field voice metadata (identity, texture, delivery); DSL version 0.3.0 |
| Outline | 7 items with type, title, description, key points, objective and estimated duration of 60 to 120 s each; slide, interactive diagram, slide, slide, slide, slide, quiz |
| Slide scene | Canvas width 1000, ratio 0.5625, height 562.5; 3 to 14 text, shape or table elements; absolute left/top/width/height; theme block; PPTist-style format; upstream PPTX exporter exists but no PPTX was obtained |
| Actions | 56 total: 21 spotlight, 28 speech, 6 widget_reveal and 1 discussion; the discussion was in scene 5 and the reveals in the interactive scene |
| Interactive scene | Diagram with 6 nodes, label/subtitle/detail fields, reveal order and HTML page of 24,749 characters with inline script; asset references mean it is not offline-self-contained |
| Quiz | 3 questions: 1 single-choice at 10 points and 2 multiple-choice at 15 points each; 4 options each; explanation field on every question; total 40 points |

## Stored JSON sizes

Conditions: extraction at 19:41 on 2026-09-12; 9 original records, whose contents are not shipped.

| Record | Bytes |
|---|---|
| Stage | 3,288 B |
| Outline | 6,081 B |
| Scene 1 | 4,444 B |
| Scene 2 | 30,790 B |
| Scene 3 | 6,571 B |
| Scene 4 | 5,340 B |
| Scene 5 | 7,204 B |
| Scene 6 | 7,943 B |
| Scene 7 | 3,869 B |
| Total | 75,530 B |

The earlier browser inventory described scene data as about 57 KB. It was a separate approximate observation, not a replacement for the extracted byte sizes.

## Layout findings

Conditions: n=5 slide scenes from the 2026-09-12 course; text overlap at least 20% of the smaller box and all-element canvas bounds.

| Slide | Elements | Text-box overlap findings | Out of canvas |
|---|---|---|---|
| Scene 1 | 7 | 0 | 0 |
| Scene 3 | 3 | 0 | 0 |
| Scene 4 | 6 | 0 | 0 |
| Scene 5 | 13 | 6 pairs, all 100% overlap, identical origin | 0 |
| Scene 6 | 14 | 0 | 0 |

Scene 5 failed: 6 pairs at 100% overlap, from 3 coincident titles and 3 coincident bodies. One slide in five (20%, n=5) is a course-specific observation with a very wide interval.

## Access, persistence and external assets

Conditions: source reading at the recorded commit plus the 2026-09-12 observations; authentication and browser egress were not dynamically tested.

| Item | Finding |
|---|---|
| Access code | Not set; the development server advertised network reachability and allowed all routes |
| Identities with shared code | 1: everyone with the code is indistinguishable |
| Storage | Browser IndexedDB only; no database started |
| Interactive dependencies | 3 KaTeX 0.16.9 asset URLs on `cdn.jsdelivr.net`; the 5 slides and quiz had no external URL |

## Database inventory

Conditions: browser inspection before the 19:41 extraction on 2026-09-12; not a new database scan.

| Database | Version | Observed contents |
|---|---|---|
| `MAIC-Database` | 170 | All 16 stores empty |
| `maic-documents` | 1 | 1 stage, 1 outline set, 7 scenes; about 57 KB of scene data in the browser inventory |
| `maic-runtime` | 1 | Empty |

## Extraction and export outcomes

Conditions: n=1 course, 2026-09-12; structure-verified JSON extraction but no completed presentation, archive or video export.

| Item | Outcome |
|---|---|
| Course data | 9 JSON files, 75,530 B, verified by record content and structure |
| Receiver | Loopback-only; up for under 20 seconds |
| MP4 | Not produced: missing compose support/runtime, absent standalone prerequisites, service memory gate |
| PPTX / resource-pack / classroom ZIP | No file arrived; browser download blocking was the recorded explanation, not independently confirmed |

The browser-download explanation was recorded but the block itself was not separately confirmed. The render-service path had independent prerequisites missing; no success is inferred from an available menu or installed CLI.

## Monitoring and route observations

Conditions: observations from the final 2026-09-12 development log; no original log lines are reproduced.

| Item | Observation |
|---|---|
| App provider listing | `/api/providers` returned 404; `/api/server-providers` returned 200 |
| App health | 2 requests to `/health` returned 404; the documented exempt route is `/api/health` |
| Development-server readiness | 364 ms at startup; not a model-generation latency |
| Compile-warning text matching | 18,510 lines contained the repeated edge-runtime warning wording |
| Idle board polling | 9,369 requests to a board API route, each 404; repeated warnings appeared in 9,255 pairs |
| Log volume | 263,315 lines, 10.1 MB for the one-hour session; polling cause not investigated |

## Limits: parallel-content estimate, never run

Conditions: arithmetic only (E); a separate short-prompt serving workload supplies the throughput bound, not a concurrent course test.

| Input or projection | Value and condition |
|---|---|
| Serving-study aggregate | 75.8 tok/s at 6 concurrent streams, 200 to 800 output tokens, same recorded stack but a different workload |
| Course single-stream mean | About 49 tok/s from the 30-sample window |
| Content phase | 42.35 min measured; longest content call 11.1 min |
| Scaled content estimate | About 27 min from 42.35 times 49/76 |
| Whole-course projection | On the order of 40 min: 27 + 9.3 serial actions + 4.7 outline and roles |
| Headroom estimate | About 1.5x; not 5x and not a measured speedup |
| Optional switch | `PARALLEL_SCENE_CONCURRENCY`, clamped 0 to 10; default 0; never set in the run |
| Interactive-call token estimate | Roughly 33,000 tokens from 11.1 min at about 49 tok/s, for a 24,749-character page; not a captured usage total |

No measured parallel course exists. Workload-dependent per-stream rates and retained-output differences prevent treating this arithmetic as an outcome.
