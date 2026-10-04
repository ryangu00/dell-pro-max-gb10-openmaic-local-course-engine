# Inspecting course artifacts without publishing the course

The study needed to inspect a saved course, not only a completion screen.
The public record therefore describes structure, counts, sizes and timings.
It does not reproduce the original request, generated teaching text, role personas,
screenshots or logs. All historical observations below are from the single
2026-09-12 course and its 19:41 extraction.

## Storage contract

The default application stores records in browser IndexedDB. The populated course
was in `maic-documents`, whose relevant stores were `stages`, `outlines` and
`scenes`. Finding another database with empty stores did not mean the course was
missing. The export snippets inspect stores before selecting the document database.

A stage record holds course metadata, role configurations and DSL version 0.3.0.
The recorded course had four roles: one teacher, one assistant and two students.
Voice metadata had identity, texture and delivery fields, but no TTS or ASR service
was configured. Metadata for voice is not evidence that audio was generated.

Outline items have type, title, description, key points, teaching objective and
estimated duration. The seven scene types were slide, interactive diagram, slide,
slide, slide, slide and quiz. Their estimated durations were 60 to 120 seconds each,
with a planned total of 600 seconds. Those estimates describe teaching time, not
the measured generation time.

## Slide and action contracts

Slides have a canvas width of 1000 and viewport ratio of 0.5625, giving height
562.5. Elements use absolute `left`, `top`, `width` and `height` fields, with text,
shape and table types and a theme block. There were 3 to 14 elements per slide.
The format is PPTist-style, and an upstream PPTX exporter exists. Neither property
means that this run produced a PPTX file.

Action lists refer to element identifiers and supply teacher text or interactive
steps. The recorded counts were 21 `spotlight`, 28 `speech`, 6 `widget_reveal` and
1 `discussion`, totaling 56. The discussion belonged to scene 5; the reveal actions
belonged to the interactive scene. Action counts do not establish successful
playback or audio synthesis.

Scene records should be ordered by `order`. Random storage identifiers are not a
presentation order. The console export names scenes using order and type so the
subsequent geometry check can operate on the intended files.

## Interactive and quiz contracts

The interactive artifact was a diagram with six nodes, label/subtitle/detail
fields and a reveal order. Its HTML page had 24,749 characters and inline script.
Although it was a single HTML document, its injected KaTeX references made it
dependent on external assets at playback. Do not call it offline-self-contained.

The quiz had three questions: one single-choice at 10 points and two multiple-choice
at 15 points each. Each had four options and an explanation field, for 40 points
total. This is a structural account, not publication or validation of the questions.

## Extraction checks

The extraction produced nine files totaling 75,530 bytes. The
[complete size table](results.md#stored-json-sizes) records each file. Inspect the
stage record and role count, the outline set, scene order and type, the quiz
question count, and the interactive keys. A byte-size match alone cannot show that
the correct records were recovered.

For the historical extraction, content signatures as well as structural counts
were checked. The signatures themselves are not published. A reader should use
the expected structure of their own neutral course, not assume their output has
the historical sizes or content.

## Quality evidence and its limits

One reader judged structure fidelity and continuity across scenes, without a
scoring rubric. The reader also checked selected arithmetic-style statements and
compared a generated structure with a separately prepared outline of expectations.
These were observations, not a second-reader evaluation or a controlled benchmark.

The judgement of usability after editing belongs to that single reader and course.
Classroom viewing was inspected by screenshots only. No cloud-model comparison,
learner study, narration audio or complete playback audit was performed.

Geometry supplies a narrower objective gate: it caught a real layout failure even
though generation completed. It still does not assess pedagogical correctness,
readability or whether an interactive explanation teaches the intended concept.

## What the public fixtures are

The files in `fixtures/` are handwritten inputs for the published helpers.
The JSON fixtures implement the layout checker's required subset, not a complete
OpenMAIC import format. The HTML is an asset-reference fixture, not a course scene.
The metrics are synthetic parser inputs, not another timing run.

A fresh neutral course was required as a possible public replacement, but no
endpoint or installed course engine was supplied for this offline authoring task.
No generated replacement is included and none is claimed. Generating and reviewing
one remains a reader exercise; its timing will differ from the historical run.

The rule is to distinguish an artifact's structural contract, a deterministic
check, and a reader's judgement. They answer different questions and need separate
evidence.
