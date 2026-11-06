# Implementation status

**Version 0.1.0 — contribution scaffold, November 5, 2026.**

| Area | Current state |
|---|---|
| Models, commands and ports | Defined; 15 commands mapped to both architectures |
| UI | Seven preview pages and nine editor tabs; business controls disabled |
| Layered | Call sequence wired; business capabilities unfinished |
| Event-Based | Queue, worker and subscriptions operational; multistage handlers and recovery unfinished |
| Persistence, providers and security | Interfaces and 17-table schema defined; adapters unfinished |
| Demo | Synthetic Thornmere campaign; no seeded account or application database |
| Demo builds | One repository; separate Layered and Event-Based entrypoints and build targets |
| Acceptance | A0–A13 specified for both architectures; tests skipped pending implementation |

## Checks

Python 3.12.14 · Streamlit 1.66.1 · Ruff 0.17.3

- **27 structural/UI/build tests passed; 28 business-acceptance tests skipped.**
- Both entrypoints rendered all seven pages in Streamlit AppTest.
- Each extracted demo rendered all seven pages in an isolated Python process without the other architecture.
- Each target built successfully with the other application's source directory absent.
- Command mappings, handler registration, fixture decoding, in-memory SQL schema and boundary checks passed.
- Lint, formatting and source/link checks passed.

Connector measurements, graduate risk results and final diagrams are pending.
Update this page as work is completed; [README](../README.md) lists the check commands.
