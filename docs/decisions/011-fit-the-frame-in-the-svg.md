# 011: Fit the frame in the SVG, not in a stylesheet

Replaces the 800 by 860 box and the 70% label ratio.

## Why

Frames spread past the reading window in VS Code. `render_diagrams.py` wrote each SVG at its natural
size, up to 860 by 1155, and the only cap was `max-height: 80vh` in `.jupyter/custom/custom.css`,
which JupyterLab loads and VS Code, GitHub and Colab do not. Every source is `graph TD`, so 65 of 96
frames were portrait against a landscape window.

`CONTRACT.md` also said the column "clips anything wider rather than scaling it", which the CSS
never did, and three files gave three different widths.

## Decision

- The renderer writes each SVG at `min(1, 900 / w, 700 / h)` of its natural size, and rewrites
  mermaid-cli's inline `max-width` to match. The size travels inside the file.
- The box lives once, in `diagrams/theme.json`. `check-theme` fails if the `custom.css` cap differs.
- `check-diagrams` asserts each declared size and a floor of 11px on the final label, replacing the
  ratio, which said nothing about what a reader sees.
- Fit wins over label size. No diagram is relaid out to keep its labels large.
- Mermaid's `flowchart` spacing is tightened (`rankSpacing` 28, `nodeSpacing` 30), which shrinks the
  natural canvas without shrinking a label. At 900 by 760 it moved the smallest label from 10.5px to
  12.8px, measured on all 35 sources.

## Measured

After the change all 96 SVGs declare 900 by 700 or smaller. The smallest label is 11.7px, the
median 16px.

## Not covered

The freshness hash covers the `.mmd` source only, so a change to the box or the spacing does not mark
SVGs stale by hash. The declared-size assertion catches a box change. A spacing-only change needs
`make diagrams`.
