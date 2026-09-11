# 007: Step frames replace the picture

Date: 2026-09-11
Status: accepted, supersedes beat 2 of the contract

## What was wrong

Every notebook gave the learner one diagram and about 800 words of prose, and the fix arrived all at
once. The course teaches engineers to reach a solution, so handing it over skips the lesson. The one
diagram was not a lapse. The contract required exactly one picture, and the scorer rewarded it.

## Decision

`## The picture` is gone. In its place, each notebook carries **3 to 6 step frames** spread across the
beats. It works like a worked derivation in maths: the naive build, where it breaks, why, then each
piece the fix adds, then the test that pins it.

A step is its own markdown cell: `### Step N: <title>`, one image, and a caption of at most 35 words.
Notebook prose is capped at 500 words, because the frames now carry what paragraphs used to.

Frames come from one `.mmd` per notebook with `%% step` directives. `render_diagrams.py` renders the
final graph once and restyles that same SVG per step, so the layout never moves between frames.
Colour means role, as before. Weight means time: a dashed ghost is not reached yet, and a glow is
what this step added.

## How it is enforced

The step rules are a hard dimension in `score.py`, like domain spread and the recording budget. The
weighted average would otherwise let a one-picture notebook lose about two points and still pass 95.
`check_diagrams.py` rejects a directive naming a missing node, a node never lit, and any SVG that no
source renders or no notebook shows. `check_gates.py` plants each of those and asserts the gate names
it.

The recording model gains `seconds_per_step_frame`, because narrating a frame takes real time.
Without it, cutting prose would push the shortest vault toward the 20 minute floor.

## The rollout

Vault 1 is the pilot. `LEGACY_SINGLE_PICTURE` in `score.py` exempts the other twelve until each is
rewritten. The set only shrinks, and the constant goes when it is empty.

Only markdown cells change. Code cells and their committed outputs stay untouched, so the replay
fixtures stay valid and nothing is re-recorded.
