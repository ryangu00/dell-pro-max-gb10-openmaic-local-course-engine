# A geometry gate for absolute-coordinate slides

The layout failure was concrete: valid scene JSON placed several text boxes on
top of one another. The engine accepted the scene because field validity and
geometry validity are separate questions. The findings refer to five slides from
the course generated on 2026-09-12, not a representative sample of courses.

## What the engine checks

The slide path parses model JSON, runs an element normalizer, and applies an image
box aspect-ratio fix. The normalizer strips null values, fills or derives missing
fields and drops elements that fail type validation. It does not inspect positions
for overlap or canvas bounds.

The slide prompt contains margins of at least 50 from the edges and alignment
conventions such as left positions of 60 or 80, centered content and right-aligned
content. Those instructions are model guidance, not deterministic enforcement.

The upstream changelog describes a detector for overlap, line-through-box and
canvas clipping that feeds findings back to the model. At the recorded commit,
that detector belongs to whiteboard role output, not the slide generation path.
No whiteboard repair result is claimed as a result of this study.

## The supplied checker

`scripts/layout_check.py` is copied unchanged from the supplied checker. It uses
only Python's standard library. A scene is eligible when `content.type` is `slide`;
the elements are read from `content.canvas.elements`.

For every pair of text boxes, construct each rectangle from the absolute origin
and size. Intersect their horizontal and vertical intervals. If either intersection
dimension is non-positive, the boxes do not have positive-area overlap. Otherwise,
divide intersection area by the smaller rectangle's area.

```text
right = left + width
bottom = top + height
intersection_width = min(right_a, right_b) - max(left_a, left_b)
intersection_height = min(bottom_a, bottom_b) - max(top_a, top_b)
fraction = intersection_width * intersection_height / min(area_a, area_b)
```

A fraction of at least 20% is a finding. Matching `left` and `top` values adds an
identical-origin annotation. Separately, every element type is checked against
the fixed 1000 by 562.5 canvas. Shapes are included in bounds checks but excluded
from text-pair collision checks, so intended text-on-background placement does not
create a text collision by itself.

The checker returns exit 1 when findings exist and exit 0 when there are none.
Its `--selftest` checks separated boxes, identical origins and a shape outside
the canvas. The additional unittest cases verify the exact threshold, touching
edges, non-slide skipping and the synthetic stacked-title/body pattern.

## Recorded failure

The [layout results](results.md#layout-findings) contain every slide. Scene 5 had
13 elements and six collision pairs, each 100% overlap with an identical origin.
All other slides had no geometry finding, and no element was outside the canvas.

The three card backgrounds were at x positions 60, 360 and 660. All three titles
were at (80, 160), and all three bodies were at (80, 240). Thus six boxes collapsed
into two stacks of three. The initial description that only the titles stacked
was incomplete; both titles and bodies failed.

Scene 6 used the corresponding text positions 80, 380 and 680 and passed. The
failure was intermittent even within this course. One failing slide out of five
is 20%, n=5, with a very wide interval. It is not a model-wide failure rate.

## Offline procedure

```bash
python3 scripts/layout_check.py --selftest
python3 scripts/layout_check.py fixtures/scene-clean.json
python3 scripts/layout_check.py fixtures/scene-overlap.json
python3 scripts/layout_check.py fixtures/scene-outside.json
```

The clean fixture should print `CLEAN`. The stacked fixture should report six
findings; the out-of-canvas fixture should report its shape. Both intentionally
failing commands return exit 1. These are synthetic test outcomes, not recovered
course output.

For a new course, extract scene JSON, inspect its structure, and pass the slide
files to the same command before export. Keep fixture results separate from
historical course measurements and from any fresh generated sample.

## Limits of the gate

This is a geometry checker, not a full input validator. It expects numeric box
fields and the fixed recorded canvas dimensions. It does not adapt to arbitrary
canvas sizes, rotation or an unrelated schema. A malformed field can fail parsing;
a file that is not a slide is skipped. A clean result does not prove that an
arbitrary JSON file is a valid course.

It does not detect text overflowing its own box, low contrast, unreadable font
size or semantic errors. Intentional overlapping text may also require judgement.
The original study did not feed findings back to a model or measure repair quality.

The rule is to gate coordinate-producing output deterministically, then evaluate
the remaining visual and content requirements separately. Model-driven repair is
an open experiment, not a delivered feature.
