# 004: The fix beat is the production build

Date: 2026-09-08
Status: accepted

## What the first vault showed

Written to the full eight beats, four sub-modules measured 36 minutes against a 30 minute budget.
Two trim passes did not close the gap, which suggested the structure rather than the prose was the
problem.

Reading the notebooks back, **"The fix" and "The build" say the same thing twice.** The fix beat
introduces a working function. The build beat then rebuilds it in production shape. The second pass
adds length without adding an idea.

## Decision

Seven beats, not eight. **"The fix" is now the production build**: written one function per cell, in
learning order, with prose between. The separate build beat is gone.

Nothing is lost. The requirement that the implementation be a real module rather than a snippet
moves onto the fix beat, where the scorer already checks that a measurement is printed.

## What changes

`docs/CONTRACT.md` lists seven beats. `nbcommon.BEATS` drops `build`. The production checks that looked
for code between `fix` and `build` now look between `fix` and `gate`.

## What this does not fix

Removing the duplication is worth about a minute and a half per vault. The rest of the gap is prose,
and that is handled by trimming rather than by another structural change.
