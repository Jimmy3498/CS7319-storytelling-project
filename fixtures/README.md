# Thornmere demonstration campaign

Both architectures use `thornmere.json` for the same characters, locations, items, relationships,
knowledge, flags and milestones.

## Source

Adapted from the custom ST Workbench fixture `fixtures/world-state/medieval-wedding-murder.json`.
Original SHA256: `b916bb5d0816d7a1312627d3a7ae35d835037e039d2f36b41827f15a0417c454`.

ST Workbench is custom [SillyTavern](https://github.com/SillyTavern/SillyTavern)-related work, separate
from the upstream project. This adaptation retains the scene and characters, revises descriptions and
access conditions, and adds milestones and the witness-seal example. Authorship is recorded in the JSON.

## Scenarios

- Save an incomplete draft, edit its entities/knowledge, then publish.
- Start two Rowan playthroughs and verify their state stays separate.
- Enter the Antechamber and discover the dagger under its authored condition.
- Create one witness seal from `seal-template`; reject invalid or duplicate creation.
- Acquire `wedding-chalice`, disclose its clue and satisfy the inquiry-flag condition.
- Count milestones by session, account and definition.
- Keep Tomas/Cedric private text out of player contexts and other sessions.
- Adopt a compatible campaign update; preserve state when an update conflicts.

Replace the placeholder fixture-author ID when importing. Private records include a fictional spoiler
canary for isolation tests. Follow the state and disclosure rules in [CONTRACTS](../docs/CONTRACTS.md).
