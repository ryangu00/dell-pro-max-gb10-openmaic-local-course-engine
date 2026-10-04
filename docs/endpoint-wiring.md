# Endpoint wiring and the limits of the local claim

The problem was to use an ordinary OpenAI-compatible chat endpoint without
patching OpenMAIC. The successful connection is narrower evidence than a complete
network-isolation claim. All implementation findings here refer to OpenMAIC 1.0.1,
commit `d5be393`, and the run on 2026-09-12.

## How provider selection works

The loader activates a provider when its `<PREFIX>_API_KEY` is non-empty.
Ollama, Lemonade and Bedrock have keyless activation paths using a base URL.
For the `deepseek` slot, an otherwise unused dummy key activates the provider.
That was acceptable because the recorded endpoint ignored this credential.
Authentication requirements for a reader's replacement endpoint are unspecified.

`DEEPSEEK_BASE_URL` is the server-side OpenAI-compatible base including `/v1`.
`DEEPSEEK_MODELS` selects the model identifier exposed through the provider.
`DEFAULT_MODEL` is a provider-qualified identifier used at every stage unless
`MODEL_ROUTES`, a JSON override, selects a different per-stage destination.
Changing only the default does not prove that no override exists elsewhere.

The public example replaces deployment coordinates with loopback and placeholders.
It has four assignments plus comments. It is deliberately not ready to copy
without replacing `<port>` and `<served-model>`.

```bash
cp configs/openmaic.env.local.example <engine-directory>/.env.local
```

The command is a reader procedure, not a claim that this book installed the engine.
The file's dummy value is not a cloud key, and it is not a credential for an
endpoint that requires authentication.

## Why the catalog entry mattered

In `lib/ai/providers.ts`, the recorded model ID has a context window of 1,048,576,
output window of 393,216, vision enabled and toggleable thinking enabled by default.
The generation code passes `maxOutputTokens` from the catalog output window.
An unknown ID gets no explicit output limit from this mechanism. A successful
model-list response alone therefore does not establish the expected token ceiling.

The supported checks are to serve a catalog-known name or accept the server
default and inspect the resulting `max_tokens` in that reader's server records.
The cookbook does not invent a catalog patch or a limit for another model.

## Server-side URL and thinking semantics

The server-side base URL passed the engine's local-network boundary in this run.
The source's Ollama example describes client-supplied localhost URLs as blocked
in production while server-side base URLs are allowed. This study relied on that
same mechanism. `ALLOW_LOCAL_NETWORKS=true` exists for client-supplied private
addresses; it was not necessary for the recorded configuration.

Provider slots have different thinking request shapes for this model:

- The `openai` slot sends `chat_template_kwargs` with a `thinking` boolean.
- The `deepseek` slot sends a top-level `thinking` object and `reasoning_effort`.
- The fast-tier proxy injected its own chat-template thinking flag set to false.

No request body was captured. Whether the extra top-level fields reached the
serving engine or were ignored is unknown, and effective thinking-off operation
was not independently confirmed from the request. The proxy mechanism is described
in the [thinking-tier cookbook](https://github.com/ryangu00/dell-pro-max-gb10-thinking-tier-proxy).

## Recorded procedure and evidence

The run used an upstream depth-1 checkout and `pnpm install`, then a model-list
probe and a small chat completion before starting the application. Installation
completed without error and `node_modules` occupied 2.3 GB. The environment file
was the only application-side change; engine source was not patched.

The development server ran in the background with output redirected to a file.
Framework telemetry was disabled with `npx next telemetry disable`. The classic
home-page generator accepted the request and moved into generation preview.
The original request text and log are neither shipped nor quoted.

The [routing-evidence table](results.md#local-routing-evidence) records the file
check, UI observation, application events and endpoint samples separately.
All 16 logged generation events selected the configured local model. Running
requests were 1.0 in all 30 one-minute samples, with no competing endpoint traffic.
That is stronger evidence than the absence of a cloud hostname in application logs,
because those logs do not record outbound request URLs.

## The unexplained second provider

The loader reported 2 LLM providers twice, at 18:38:40 and 18:39:25. The supplied
file configured only one. Loader behavior implies an additional credential or
keyless-provider base URL in another configuration source or the process
environment. Which provider and which source remain unknown.

The process environment was not captured before the process ended. There is no
evidence of a cloud generation call, but there is also no evidence establishing
zero cloud keys in the running process. Browser-side requests were not audited.

The next check is a clean-environment launch using `env -i` with an explicitly
listed environment, followed by `/api/server-providers`. This was not done.
The complete environment allowlist needed by a reader's installation is unknown;
a ready-to-run minimal launcher is therefore not supplied.

## Reader checks

Set `VLLM_URL` to the serving origin without `/v1` and `MODEL` to the served ID,
then run `bash scripts/endpoint-smoke.sh`. The published smoke uses a neutral
synthetic acknowledgement request. It is not the original course request.
The endpoint scripts assume the unauthenticated endpoint behavior described above.

Inspect the app's `/api/server-providers`, not `/api/providers`. The app's health
route is `/api/health`; these are application routes, separate from the model
server's `/v1/models` and `/metrics`. Inspect the actual provider list before
strengthening the file-only claim.

The rule is to make claims at the layer that was checked: a file, a process,
the model endpoint and a learner's browser are separate verification surfaces.
