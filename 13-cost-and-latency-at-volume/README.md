# Cost and latency at volume

What a workload really costs and how long it really takes, both measured rather than quoted.

This vault finishes the token economics story. Vault 3 counts the tokens. This one covers the three
levers you actually pull once the counting is done: which model, what shape, and which lane.

| Sub-module | What breaks | Domain |
|---|---|---|
| `01-caching-is-a-property-of-the-model.ipynb` | A cache saving that was budgeted for and never arrives | Content moderation |
| `02-latency-is-not-the-sum.ipynb` | Five fast calls that take as long as their total | Esports analytics |
| `03-capstone-a-lane-for-every-job.ipynb` | The cheapest model per token, on a path where somebody is waiting | Insurance claims |

## What you will have measured

Three models against one identical prefix, reporting very different cached shares. The same five
calls queued and overlapped. And a claims workload priced in both currencies, so the choice between
paying more and changing the shape is a number rather than an argument.

## One thing this vault cannot show you

Batch lanes exist here under a `:batch` model suffix at roughly half the token price, and the chat
endpoint refuses them by design. Submitting to that lane needs a different endpoint, and it returned
404 on the account this course was recorded with. The capstone shows the shape and says plainly that
it did not run it.
