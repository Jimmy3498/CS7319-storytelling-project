# Acceptance tests

Run A0–A13 through both architecture gateways with the same fixture, inputs, failures and scripted
responses. Replace each skipped test body with assertions before enabling it. Real-provider cases
run separately with approved credentials.

| ID | Owning capability | Required evidence |
|---|---|---|
| A0 | AUTH | Register, login/logout, reject wrong credentials and cross-account campaign/session/card access. |
| A1 | WORLD / EDITOR | Save incomplete drafts; rich entity CRUD and reviewed AI edits; reject stale/invalid publication; publish valid catalog record. |
| A2 | GAMEPLAY | Start two preset-PC sessions; accepted changes affect only the selected session and preserve its base campaign. |
| A3 | PROVIDER / EDITOR | Run deterministic provider then explicit real configured API; inspect separate contexts and manual editor acceptance versus auto gameplay commit. |
| A4 | GAMEPLAY / PERSISTENCE | Reject malformed/unknown/illegal/stale effects; deduplicate same operation; conflict on changed payload. |
| A5 | LAYERED / EVENTS | Inject timeout/delay/storage/subscriber failures and late results; preserve state and expose explicit retry/uncertainty. |
| A6 | PERSISTENCE / EVENTS | Restart and resume accepted state; recover commit-before-publish without duplicate local effects; never automatically replay a paid request. |
| A7 | REPORTS | Known accepted/rejected/failed attempt counts, no duplicate counts, reporting catch-up independent of gameplay result. |
| A8 | LAYERED / EVENTS | Equivalent observed outcomes and genuinely different call versus queued traces; same fixture/provider/delay inputs. |
| A9 | MERGE | Continue old version; adopt compatible update with checkpoint/progress; reject overlap/broken references atomically. |
| A10 | REPORTS | False-to-true marker hits once per session/fingerprint; distinct-account/session counts and version denominators; no rejected-turn awards. |
| A11 | PRIVACY | Inspect outbound prompts/history/UI/report projections for private canaries, wrong-actor/scope facts, missing labels and privileged free-text handoff. |
| A12 | PROFILES | Private account cards, captured config, endpoint rebinding, secret redaction and no calls on save/activate or unauthorized card access. |
| A13 | GAMEPLAY | Create a real allowed template instance; persist across resume; duplicate retry adds none; reject invalid templates/destinations/NPC creation. |

See [ARCHITECTURE](ARCHITECTURE.md) for the connector experiments and comparison measurements.
