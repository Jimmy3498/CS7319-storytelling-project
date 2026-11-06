# Behavior and interface contracts

Both architectures implement these contracts. Coordinate changes through the workflow in
[CONTRIBUTING](../CONTRIBUTING.md); [STATUS](STATUS.md) tracks implementation progress.

## 1. Accounts, access and authoring

One registered account can author and play. Services verify `RequestContext.user_id` against a
server-side login bound to the browser session. Store accounts in SQLite; normalize usernames with
NFKC/casefold for uniqueness, allow 3–32 display characters, and accept passwords of 8–1024 UTF-8 bytes.
Use a random salt, versioned scrypt hash and constant-time comparison. Email verification, password
recovery and external identity services are outside the account demo.

A campaign owner edits its draft and reads its reports. Public browsing returns `CatalogEntry`.
Session actions require session ownership; API-card operations require card ownership. Services enforce
these checks. Player-mode knowledge restrictions also apply when the player authored the campaign.

World records have stable, nonempty IDs: at most 128 characters using letters, digits, underscores,
hyphens or colons. Generate IDs for new records and retain fixture aliases. References use IDs.
Records cover characters, locations, item templates/instances, relationships, numeric stats,
text/knowledge, narrative rules, stat bands, flags and milestones. Characters have public
appearance/expression and separately classified personality/history/knowledge. Distinguish authored
facts, beliefs, claims and hearsay; identify the holder of each belief or claim.

Manual editing updates an `EditorBuffer`. `SaveDraft` checks ownership, shape and expected persisted
revision. Incomplete drafts are allowed, and unsaved edits survive a save conflict. AI coediting captures
the buffer, selected record IDs and both revisions, then returns a typed candidate and visible diff.
Acceptance updates the buffer; rejection leaves it unchanged. Save persists it. A changed buffer or
source revision invalidates the proposal. The coeditor has no filesystem tools or publication authority.

Publication checks title/summary/background/opening, public classification for catalog/setup prose,
a preset PC with a valid start, IDs/references, finite bounded stats, item placement, access labels,
conditions and marker references. Publication requires structural readiness, with no story-quality score
or minimum narrative length. It creates an immutable version in the local catalog. Later draft edits
leave publications and existing sessions unchanged.

## 2. Session state and supported effects

`StartSession` copies a chosen publication into an independent session for a preset PC. Session state
contains a base-version reference, revision, materialized world, disclosed IDs and current flag values.
Store current flags separately from authored initial values. Use full snapshots plus change records.

The player submits free text. The Director returns a `TurnProposal`: expected revision, supported
effects and candidate public fact IDs. Reject unknown fields/kinds, non-finite numbers and invalid IDs.
Limits: 8,000 input characters, 32 effects, 64 cited public facts and a 1 MiB decoded response.
Narrative rules guide the model. The validator enforces the state operations below.

| Effect | Required fields beyond kind/actor_id | Checks |
|---|---|---|
| move_character | destination_id | Actor is a known character; target is an adjacent known location. |
| transfer_item | target_id, destination_id | Existing item accessible at actor's position or held by actor; destination is co-located character or current location; one placement only. |
| change_stat | target_id, stat_id, delta | Known character/stat; finite delta; result remains within authored bounds. |
| change_relationship_stat | target_id, stat_id, delta | Known relation/stat; actor is a participant; same numeric bounds. |
| set_flag | target_id, enabled | Defined flag; its authored set_when condition is satisfied. |
| request_disclosure | target_id | Recipient actor is current PC; record reveal_when or item discover_when is satisfied; no policy means deny. |
| create_item | template_id, destination_id | Permitted template/spawn condition/cap; valid local destination; application assigns a new ID. |

Require null for fields irrelevant to an effect. Apply ordered effects to an isolated candidate,
validate the result, then commit all or none. `actor_id` identifies an existing PC or NPC. Reject unknown
entities and state keys; player consent is not inferred from free text. Created items belong to the
session, survive resume and leave the published campaign unchanged. NPCs and locations are authored.

Conditions use a closed menu: `at_location` compares the current PC location; `owns_item` checks direct
PC possession of an existing item ID; `flag_equals` compares a current flag. Evaluate the candidate at
the relevant step. Do not execute scripts, arbitrary expressions or prose rules. Stat bands are
lower-inclusive/upper-exclusive, except the band ending at the stat maximum includes that maximum.

## 3. Information boundary and AI

Text, items and stats require an access label: public, director or an exact set of character IDs.
Reject missing, invalid or mixed labels. At runtime, build player context from perceived public
information, the PC's knowledge and authorized disclosures. Hidden items require a discovery gate.
History stays within the session, and beliefs retain their attribution. Apply the same restrictions
to retrieval, diagnostics and reports.

The normal-turn design uses one logical Director: a privileged structured-planning request followed by
a player-scoped narration request, both using the captured API card. Invalid plans stop before narration;
completed retries return their result without a model call. The two requests trade latency and cost
for context separation. Both architectures follow this design.

KnowledgePolicy authorizes disclosures and builds `PlayerView`, the narrator's sole context input.
Keep full snapshots and raw planner prose out of narration. The Event-Based narrator receives
`NarrationWork`; queue messages carry opaque references to private workflow state.

Test exact outbound messages, histories and UI/report projections with private canaries. Provider
tests should also check narration for errors and unintended disclosures.

## 4. Provider cards

Each account has private cards and one active default for editor/play. Card metadata contains a name,
full endpoint URL, model ID, supported protocol and credential-presence flag. Keep credential values
out of public DTOs.

Support non-streaming chat-completions-compatible HTTP, with status/body parsing, bounded responses
and connect/read deadlines. Require HTTPS except for loopback HTTP. Do not follow redirects with
credentials. Start with 15-second connect and 120-second inactive-read timeouts; tune from measurements.

Capture settings and credentials at admission; a default change affects the next operation. Saving or
activating a card makes no provider call. Endpoint changes require credential rebinding. Deleting an
active card requires a replacement or disabling AI. Paid retries require an explicit request;
do not silently substitute a mock provider.

Store secrets in the OS credential vault through the optional `keyring` adapter, namespaced by
installation, owner and opaque reference. If the backend is unavailable, return an unsupported error;
never fall back to plaintext files or SQLite. Tests use `ScriptedTestProvider` with supplied responses.

## 5. Commit, failure, retries and updates

Commit accepted state, public input/narration, a durable idempotency receipt and a pending completion
notice in one SQLite transaction. Check expected revision at commit and keep provider calls outside SQL
transactions. Display accepted output after persistence confirms it. Record rejected/failed attempts
separately from accepted transcript and achievements.

Durable request identity is owner + request ID + canonical payload digest. Matching requests return
their receipt; the same ID with a changed payload conflicts. Per-session admission prevents overlapping
turns, with a final revision check at commit. An explicit retry inspects the prior status and creates a
linked attempt. A timed-out or interrupted provider call may still be billed: show that uncertainty and
require an explicit retry. After restart, recover committed notifications without replaying paid requests.

`TurnAdmission` contains either a fresh baseline or a previous commit. Return an existing commit before
any model call. `OperationStatusStore` holds owner/client-scoped receipts for the process lifetime; its
HMAC detects conflicting submissions without retaining plaintext. Durable receipts belong in repositories.
A reporting failure preserves accepted gameplay. Each subscriber has its own acknowledgement/dedup
record, and reports show their projection freshness.

Keep a session on its starting version until the player requests an update. Compare old base, new
publication and progressed session by stable IDs/fields. Preserve progress and session-created items.
Validate the entire candidate, retain a pre-update checkpoint, then atomically change base and state.
Incompatible overlapping edits or deletion of referenced entities block the update and preserve the old
version/state/history.
Player previews show safe summaries and conflict categories, never private candidate worlds.

## 6. Reporting and query results

Report started sessions, accepted turns, rejected/failed attempts, last activity and projection freshness.
Award a milestone on an accepted false→true transition, once per session/definition fingerprint.
Resume, rejected turns, duplicate delivery and campaign adoption alone do not award milestones.
Fingerprint the normalized marker ID and condition; label changes do not change its meaning.

Keep session/version membership for denominators. Eligible sessions/accounts have used the selected
version containing that definition. Label these denominators. Version-filtered hits mean **first
achieved while on this version**. Overall counts deduplicate sessions/accounts for the same fingerprint;
keep different fingerprints separate. Campaign owners receive aggregates without player transcripts.
Provider usage/cost records stay separate from story analytics.

| Query | Result |
|---|---|
| catalog | `CatalogEntry` tuple |
| my_campaigns | Owned draft summaries |
| editor_draft | Owned `CampaignDraft` |
| my_sessions | `SessionSummary` tuple |
| resume_session | `PlayerView` and accepted transcript |
| campaign_report | `CampaignReport` |
| provider_cards | Redacted `ProviderProfile` tuple |
| update_preview | Adoption status, version IDs and safe conflict categories |

Keep raw `SessionSnapshot`, `MergePreview` candidates and `ProviderCapture` objects out of player,
catalog and card views.
