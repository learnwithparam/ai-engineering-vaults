# Verify Agent Sign-In with PyJWT

One course in one notebook: `01-verify-agent-sign-in-with-pyjwt.ipynb`.

Northwind Payroll runs an HR assistant agent. When an employee asks for a payslip, the agent calls the
payroll service for that employee and carries a signed token that says who is asking and what it may
do. Without a check, the payroll service believes any signed token it receives, so a token made for
the payslip service can reach the bank-details service, and an expired token still gets an answer.

You build the sign-in check for that service with PyJWT, one rule at a time. The notebook starts with
a starter that trusts any signed token, then adds the signature check with a pinned algorithm, the
audience and expiry checks, the delegation check and the scope check. It ends with one evaluator and
tests that run without a key.

## Before you start

Run `00-setup/01-start-here.ipynb` first. This course makes no model call, so it needs no API key.

## What you will have built

A sign-in evaluator for an agent token, with a test for each check and a final test that counts the
bad tokens let through and the good tokens refused. All of it runs without calling a model.
