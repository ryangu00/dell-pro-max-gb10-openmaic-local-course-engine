# Generation timing: a serial client on a local endpoint

The question was whether the long wall time came from orchestration gaps or model
generation. The recorded evidence is one course on 2026-09-12. No throughput or
latency measurement is added by the synthetic tests in this repository.

## Request graph

The browser starts `scene-outlines-stream`, then `agent-profiles`. It then walks
scenes in order, issuing `scene-content` followed by `scene-actions`, and advances
only after both return. Each scene-type branch in the recorded implementation
calls the model once per content request and once per action request.

The record contains 7 content POSTs, 7 action POSTs, an outline call and a role
call. All 16 POSTs returned 200. The client has retries, but no retry was observed.
Long scene requests were not evidence of several hidden model calls.

The optional bounded-concurrency path applies to scene content. The server
setting `PARALLEL_SCENE_CONCURRENCY` is clamped to 0 to 10, with default 0 selecting
serial execution. Actions remain serial. The setting was not changed for this run.

## Measurement procedure

Use application timestamps to identify outline, roles, scene content and actions.
Use POST durations to quantify the individual calls. The original record began
generation at 18:40:24 and ended at 19:36:54. The complete stage table is in
[results](results.md#stage-and-scene-timing); rounding is retained as reported.

Poll `vllm:generation_tokens_total` and `vllm:num_requests_running` once per minute.
The recorded sample window was 18:48 to 19:18, 30 samples. Direct probes separately
recorded waiting requests at 18:41 and 18:47. A cumulative preemption count was
read at 18:59; it must not be treated as a course-specific before/after difference.

The progress script initializes its previous token count to zero. Its first
printed delta is the counter's cumulative value since engine start. Discard that
sample before deriving a rate; the script preserves this historical behavior and
documents the baseline explicitly.

With `VLLM_URL` and `DEV_LOG` set for a reader's endpoint and application log:

```bash
bash scripts/vllm-metrics-probe.sh
bash scripts/progress-monitor.sh
bash scripts/wait-until-idle.sh
```

These commands are separate diagnostics, not a pipeline of commands to run
simultaneously in a single terminal. They read the application log and the serving
endpoint, so they cannot identify unrelated traffic without additional evidence.

## What the counters showed

The sampled generation-token deltas had median 2,890, mean 2,944, minimum 2,337
and maximum 4,545 per minute. Equivalent rates were median 48 tok/s, mean 49 tok/s
and range 39 to 76 tok/s. Running requests were 1.0 in every sample.

The content phase accounted for 42.35 minutes, or 75% of wall time; actions took
9.33 minutes, or 16.5%; outline plus roles took 4.7 minutes, or 8.3%. The interactive
scene alone took 12.2 minutes, 21.6% of the course's wall time. These are arithmetic
aggregates of a single measured course, not population averages.

Most between-scene gaps were 0.01 to 0.02 seconds, observed five times. The one
4.6-second gap included a 4.3-second classroom-route load. Large idle gaps did not
explain the duration in this record.

The whole-run estimate of about 166,000 generated tokens extrapolates the
30-sample mean over 56.5 minutes. It is not a measured token total. For the
interactive call, roughly 33,000 tokens is likewise an estimate from 11.1 minutes
at about 49 tok/s. Its retained HTML was 24,749 characters. The reason generation
estimates so greatly exceed retained output was not isolated.

## Preserved monitor limitations

The source scripts expect one metric series per counter and the observed decimal
format of running-request values. They do not aggregate multiple replicas or
normalize arbitrary Prometheus formats. Metric-fetch failure is not a successful
observation, even if a shell branch substitutes a zero or question mark.

The progress script requests metrics separately for token and running-request
readings, so the two readings are not an atomic snapshot. Its end conditions are
a completion-text match, application error match, repeated stall heuristic or
timeout. These are diagnostics, not a verified course-completion API.

The idle script labels three zero-running observations at a 30-second cadence
as a 90-second idle check. The initial observation is immediate: the label is
preserved source behavior, not a guaranteed continuously idle duration. Sampling
can also miss work between observations. The script checks idle before the error
branch on the final iteration and does not prove the saved course is complete.

The scripts preserve the historical status-message behavior; they are not designed
as strict success/failure exit-code gates. Inspect their terminal signal and then
validate the extracted scene count and artifacts. The tests intentionally exercise
completion, error, stall and timeout branches without real waits or requests.

## What was not compared

There was no repeat-course distribution, no thinking-on tier comparison and no
parallel scene test. Slides varied 2.6x in content time, from 3.6 to 9.3 minutes,
despite similar retained output sizes. Generated size alone is not a timing model.

The parallel estimate belongs under [Limits](results.md#limits-parallel-content-estimate-never-run).
It uses the serving book's different short-output workload, not measured concurrent
course requests. The content floor from the longest call and the server's aggregate
rate are constraints on a hypothesis, not an observed acceleration.

The rule is to identify the request graph, separate cumulative counters from
request-attributed evidence, and test the built-in concurrency path before claiming
that extra hardware or a switch reduces end-to-end course time.
