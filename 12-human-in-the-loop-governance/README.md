# Human in the loop governance

**One video, about thirty minutes.** Which actions stop for a person, how a run pauses and comes
back, and how you answer the question an auditor asks first.

The idea underneath all three: **approval is a budget, not a switch.** Gate too little and something
final happens with nobody watching. Gate everything and the same fixed attention is spread across
five hundred approvals, so nobody reads any of them.

| Sub-module | What breaks | Domain |
|---|---|---|
| `01-which-actions-need-a-human.ipynb` | A model waves a video deletion through, then gating everything leaves 14 seconds per approval | Self driving fleet |
| `02-pausing-and-resuming-a-run.ipynb` | The same tool call six times, nothing decided, nobody told | Ticket drop bot defence |
| `03-capstone-an-agent-that-cannot-drop-prod.ipynb` | Sanctions screening turned off, and no record of who allowed it | Money laundering case work |

## Before you start

Run `00-setup/01-start-here.ipynb` first. Every notebook here runs without an API key, from committed
recordings, so the whole vault executes for free. The LangGraph nodes call the model through the same
recorded client, so the graphs replay too.

## What you will have built

A risk register that fails closed on a tool nobody classified, a stall detector that hashes tool call
signatures and escalates a loop that is going nowhere, a LangGraph runtime that pauses before a
guarded node and resumes from a checkpoint, and an audit trail where approve, reject and timeout all
leave a row.
