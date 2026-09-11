# Programmatic Guardrails for High-Reliability AI

One course in one notebook: `01-validate-a-loan-payment-quote.ipynb`.

You build the checks around a loan advisor model at a consumer lender. The model reads a loan record
and calculates the monthly payment, and it returns a quote in a fixed shape. Your code decides
whether that quote is fit to show a customer.

The notebook starts with a quote whose shape is perfect and whose monthly payment is negative. It
then adds the checks one step at a time: Pydantic validators for ranges and cross-field rules, a
bounded retry that sends the validator's own errors back to the model, an error taxonomy that tells
retryable failures from non-retryable ones, and jittered backoff for timeouts.

## Before you start

Run `00-setup/01-start-here.ipynb` first. The notebook runs without an API key, from committed
recordings of real responses, so you can follow the whole course for free.

## What you will have built

A quote function that checks lending policy before any model call, repairs a bad quote in a loop
that always ends, and waits out transient failures. Each of those guardrails has a test, and every
test runs without calling the model.
