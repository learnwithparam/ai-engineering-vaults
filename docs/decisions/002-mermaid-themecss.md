# 002: Mermaid custom CSS must arrive via --cssFile

Date: 2026-09-08
Status: accepted

## What happened

`diagrams/theme.json` carries a `themeCSS` string that colours edge labels and cluster titles.
Passing it inside the `-c` config file, which is what the mermaid docs imply, produced an SVG with
no such rule. mermaid-cli **ignored it silently**. No warning, no error, exit code zero.

The visible effect is subtle and easy to ship: edge labels keep a dark background chip and inherit
their text colour, so on a dark notebook they range from low contrast to invisible.

This is the trap already documented in `lwp-presentations/src/components/MermaidRenderer.tsx`, which
notes that edge labels and cluster titles are unreachable from `themeVariables`. It bit again here
in a different tool.

## Decision

Write the CSS to a real stylesheet and pass `-C/--cssFile`. That lands it as a second `<style>`
block in the SVG.

## The gate

`check_diagrams.py` now reads the first selector out of `themeCSS` and asserts it appears in every
rendered SVG. If a future mermaid-cli drops it again, the build fails instead of the diagrams
quietly degrading.

Proven by deleting the rule from a rendered SVG and watching `make check-diagrams` fail.
