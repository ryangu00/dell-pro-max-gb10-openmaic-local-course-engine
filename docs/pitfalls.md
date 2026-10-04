# Pitfalls: symptom, cause, supported fix

Historical observations refer to the single 2026-09-12 course at OpenMAIC commit
`d5be393`. Source-only findings and untested follow-ups are labelled. No original
prompt, course text or log lines are quoted. The table below covers the public
pitfalls from the fact sheet; details follow in the same order.

Conditions: one recorded run or source inspection as described below; a proposed fix is not a measured success unless stated.

| Symptom | Root cause or evidence limit | Supported fix or next check |
|---|---|---|
| Provider listing is 404 | `/api/providers` is not the listing route | Use `/api/server-providers`; app health is `/api/health` |
| Error search fires immediately | Repeated compile warnings contain a generic error word | Match `[ERROR]` application severity or generation POST results |
| Missing model or unexpected output ceiling | Served name is not known to the catalog | Use a catalog-known name or inspect server-default `max_tokens` |
| No scene completion event for 5 to 11 minutes | One long non-streaming content call | Watch token-counter deltas |
| First delta is about a million tokens | Cumulative counter was compared with zero | Discard the first monitor sample |
| Clean cumulative finish reasons appear reassuring | Counters include other requests since startup | Diff before/after or attribute to request identifiers |
| Outline seems slow for 7 items | Structured JSON generation is limited by endpoint token rate | Budget the observed 3.7 min; do not diagnose a stall from item count |
| Scene filenames do not reflect presentation order | Storage keys are random identifiers | Sort by the `order` field |
| Garbled slide despite completed generation | Field/type validity does not establish geometry | Run the geometry checker before export |
| Correct card backgrounds but stacked text | Repeated text coordinates across columns | Inspect identical origins first |
| Access code is assumed active | Setting is opt-in and absent by default | Set it, then check an unauthenticated API request for 401 |
| Local-generation claim fails during playback | Interactive HTML references KaTeX on a CDN | Vendor and rewrite assets, or block the domain and test rendering |
| Development server is network-reachable | Default development listening behavior exposes the port | Bind to loopback or firewall during evaluation |
| Export click produces no file | Download blocking was suspected, not independently confirmed | Use a normal browser or IndexedDB plus the receiver |
| Compose profile option is rejected | Installed CLI lacks compose support | Install the plugin or satisfy standalone-service prerequisites |
| Receiver filename can escape its output folder | Original helper only removed traversal substrings | Enforce `[A-Za-z0-9_-]+`; published helper does so |
| An idle tab keeps growing the log | Repeated board polling and warnings | Close the tab; root cause of polling remains unknown |

## Provider and health routes

The provider-listing request to `/api/providers` returned 404. The correct
application route `/api/server-providers` returned 200 in the record. Two app
requests to `/health` also returned 404; the exempt app route is `/api/health`.
These paths belong to OpenMAIC, not the model endpoint.

Getting the correct listing route matters because the server reported two
providers despite one provider in the file. A healthy application or a valid
model list is not a substitute for identifying those loaded providers.

## Generic error matching creates false alarms

The final log contained 18,510 instances of repeated edge-runtime warning wording
that included a generic error term. Searching for that term alone immediately
matched compilation noise. The application error-severity count was 0.

The sanitized scripts keep the `[ERROR]` severity pattern and generation POST
patterns. They do not ship those original warning lines. Synthetic tests verify
that an unqualified error word does not trigger the application's error branch.

## Model IDs influence token ceilings

The recorded catalog includes the model ID and its output window. The generation
path supplies that window as `maxOutputTokens`. An unfamiliar served ID lacks that
explicit limit. An empty or unexpected UI model list can therefore be a provider
or catalog configuration problem, not proof that the endpoint is unreachable.

Use the recorded provider mechanism, then inspect the server's actual request
limit. Behavior for an arbitrary replacement model is not measured here.

## Long calls look silent

Scene content uses a non-streaming HTTP request. The application logs completion
only when the request returns, so a 5-to-11-minute quiet period can still contain
active decoding. The interactive content request lasted 668 seconds, or 11.1
minutes, in this course.

Use the serving endpoint's token delta rather than only application log activity.
The corresponding metric sample is evidence of progress only when the endpoint
traffic can be attributed to the course, as it could in this recorded run.

## The first counter delta is not a rate

The original monitor starts the previous count at zero. A first printed delta of
about a million tokens was cumulative work since engine start, not generation in
that minute. The public script preserves the behavior and labels it in comments.

Discard that baseline sample before summarizing rates. The synthetic tests verify
the initial cumulative delta and later zero deltas independently of real time.

## Finish reasons need attribution

Cumulative finish-reason counters showed abort 0 and error 0 in the recorded
inspection, but those counters span all clients since engine start. Their scope
does not establish the outcome of a specific course.

Before/after differences or request-specific records are the supported approach.
This study did not archive such a per-course finish-reason series. A clean
cumulative counter must not be restated as a stronger attributed result.

## Outline size does not predict latency

The seven-item outline was streamed structured JSON. Its recorded time was
3.66 minutes, with 219 seconds and a rounded POST duration of 3.6 minutes in the
timing record. The fact sheet's planning shorthand is 3.7 minutes.

These forms describe the same recorded stage at different displayed precision.
The suggested budget is based on that observation, not a guaranteed latency for
another course or a different endpoint.

## Storage order is not presentation order

Scene storage keys are random identifiers. Sorting names or keys lexically can
therefore change course order. The reader procedure uses the `order` field and
names exported records by order and type.

The JavaScript mock test checks ordering. It does not discover cross-course join
fields for a browser containing several courses; the snippets require explicit
selection before the posting block.

## Valid schema, invalid slide geometry

The normalizer validates fields and types, not text-box intersection or bounds.
One slide in the recorded course passed generation with six overlapping text
boxes: three titles in one stack and three bodies in another.

Run the geometry check before treating generation as an export-ready result.
It checks overlap of at least 20% of the smaller text box and the fixed canvas
boundary. It cannot assess text overflow, contrast or font readability.

## Backgrounds can conceal a coordinate failure

The failing slide's card shapes were arranged across three columns, while the
titles shared an origin and the bodies shared another. The cards alone looked
like a valid column layout. Checking only titles initially missed half the defect.

Inspect identical origins among all text elements. The synthetic stacked fixture
has both groups and produces six pairwise findings. It contains no original slide
text, and its values are fixture inputs rather than new course measurements.

## An access-code feature is not an enabled gate

The run left `ACCESS_CODE` unset. The source permits requests in that state.
When configured, it protects API routes with a shared cookie, while pages pass
through to a front-end modal. This was source inspection, not a dynamic test.

The supported follow-up is to set the code and check a protected API request
without a valid cookie for 401. Real per-user authentication remains separate
work; the shared code distinguishes only one identity.

## Playback can fetch external assets

The interactive artifact referenced three KaTeX 0.16.9 CDN assets. The five slides
and quiz had no external URL. These are saved-artifact observations, not a full
browser-network trace.

The new rewrite script replaces the pinned references without downloading files.
Supplying genuine matching local assets and confirming browser rendering offline
remain unperformed checks. Passing the substitution test does not close this gap.

## Development listening scope matters

The development server advertised a network address, and the run had no access
code. The supported evaluation fix is loopback binding or a firewall rule.
Neither a firewall nor a new listening configuration was deployed in the study.

The cookbook publishes only loopback example addresses; they are not a record of
the historical endpoint's network coordinates.

## A menu click is not a recovered artifact

PPTX, resource-pack and classroom ZIP export clicks produced no downloaded file
within the check window. The notes attributed that to the test browser's download
restriction, but the restriction itself was not separately confirmed.

Use a normal browser or extract IndexedDB records through the loopback receiver.
The JSON transfer succeeded; the menu export routes remain unverified.

## Render-service prerequisites were missing

The Docker CLI lacked the compose plugin and the runtime daemon was not available.
The standalone render service lacked Chromium headless shell and installed
dependencies, and its available-memory gate was not met.

Installing compose support or preparing the standalone service is a possible
next step, not a completed fix. The installed Hyperframes and FFmpeg versions
alone do not establish a working MP4 route.

## Receiver names need validation

Removing traversal substrings from a client path is not a filename allowlist.
The public receiver accepts only alphanumeric names, underscores and hyphens,
and refuses symlink destinations. The output directory is a caller argument.

Offline tests verify valid writes and rejection of traversal, encoded paths,
separators and symlinks. Binding and handlers are mocked; real browser CORS and
socket behavior are not thereby validated. Keep the receiver temporary and local.

## Idle tabs can dominate the log

The recorded tab polled a board route 9,369 times, receiving 404 each time, with
9,255 pairs of repeated warnings. The final development log was 263,315 lines and
10.1 MB for a one-hour session. The polling cause was not investigated.

Closing the tab addresses that observed source of log growth. It is not a fix to
the underlying application behavior, and no change to the polling code is shipped.
