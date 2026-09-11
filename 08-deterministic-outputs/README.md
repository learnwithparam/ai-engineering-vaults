# Deterministic Response Engineering for Production APIs

One course in one notebook: `01-build-an-invoice-extractor.ipynb`.

You build an invoice parsing service for an accounts payable team. Suppliers send invoices as text,
the model reads each one, and your code posts what it read to the ledger the bank pays from. Every
call forces the model to answer through one `extract_invoice` tool, so every reply is JSON in the
shape the tool describes.

The notebook starts by asking for JSON in words and watching the parser fail. It then forces the
reply through the tool, checks that every reply parses and its types match, locks the schema down,
gives the model a way to refuse a document that is not an invoice, and finally checks each value
against the document itself, because a reply can be perfectly valid and still wrong.

## Before you start

Run `00-setup/01-start-here.ipynb` first. The notebook runs without an API key, from committed
recordings of real responses, so you can follow the whole course for free.

## What you will have built

An invoice extractor that posts only answers it has checked, sends everything else to a person with
the reasons, and carries a test for each of its checks that runs without calling the model.
