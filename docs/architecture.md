# Architecture Notes

## Goal

Deliver a security assessment tool that feels concrete and useful for Microsoft identity environments.

## MVP Design

The starter uses a simple pipeline:

1. load exported tenant snapshot JSON
2. evaluate deterministic hygiene rules
3. render output as markdown or JSON

This gives a clean baseline for portfolio storytelling while staying easy to test.

## Current Model

The sample tenant snapshot includes:

- Conditional Access policies
- user accounts and privileged role assignments
- MFA registration state
- service principal credentials

## Why Deterministic First

The first version should produce stable output every run so:

- findings are easy to explain in interviews
- unit tests stay straightforward
- future AI summarization can be layered on top without replacing core control logic

## Expansion Path

- live Microsoft Graph ingestion
- secure auth flow for tenant read access
- scoring by control families
- HTML dashboard export
- remediation workflow tracking
