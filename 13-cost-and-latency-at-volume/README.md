# Cost and Latency Engineering for AI Systems at Volume

One course in one notebook: `01-route-claims-by-cost-and-latency.ipynb`.

You build the model calls behind an insurance claims desk. Adjusters ask live questions and wait on
screen for the answer, while a backlog of claims is scored overnight when nobody is waiting. The
two jobs want opposite things, so the course measures what each call really costs and how long it
really takes, and then gives each job its own lane.

The notebook starts with one question and reads the usage block that comes back. It then measures
whether the model reuses the repeated claims manual, times warm calls rather than the first one,
runs a question's three lookups in parallel so the slowest call sets the wait, and builds a batch
lane that scores many claims in one request on the cheapest model.

## Before you start

Run `00-setup/01-start-here.ipynb` first. The notebook runs without an API key, from committed
recordings of real responses, so you can follow the whole course for free.

## What you will have built

A live lane and a batch lane for the same claims desk, with the cost and the wait of each measured
from real responses, and tests for the routing and the batch checks that run without calling the
model.
