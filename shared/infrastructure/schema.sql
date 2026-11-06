-- Structural schema only. Application repositories/transactions are unimplemented.
-- No credentials, user records, runtime state or real provider data are seeded here.
PRAGMA foreign_keys = ON;
CREATE TABLE schema_versions (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL);
CREATE TABLE accounts (
 id TEXT PRIMARY KEY, username_normalized TEXT NOT NULL UNIQUE,
 display_name TEXT NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE login_sessions (
 id TEXT PRIMARY KEY, account_id TEXT NOT NULL REFERENCES accounts(id),
 client_session_hash TEXT NOT NULL UNIQUE, expires_at TEXT NOT NULL
);
CREATE TABLE campaigns (
 id TEXT PRIMARY KEY, owner_id TEXT NOT NULL REFERENCES accounts(id),
 draft_revision INTEGER NOT NULL CHECK(draft_revision >= 0),
 draft_json TEXT NOT NULL CHECK(json_valid(draft_json)), updated_at TEXT NOT NULL
);
CREATE TABLE published_versions (
 id TEXT PRIMARY KEY, campaign_id TEXT NOT NULL REFERENCES campaigns(id),
 version INTEGER NOT NULL CHECK(version > 0),
 content_json TEXT NOT NULL CHECK(json_valid(content_json)), published_at TEXT NOT NULL,
 UNIQUE(campaign_id, version), UNIQUE(id, campaign_id)
);
CREATE TABLE playthroughs (
 id TEXT PRIMARY KEY, owner_id TEXT NOT NULL REFERENCES accounts(id),
 campaign_id TEXT NOT NULL REFERENCES campaigns(id), base_version_id TEXT NOT NULL,
 player_character_id TEXT NOT NULL, revision INTEGER NOT NULL CHECK(revision >= 0),
 state_json TEXT NOT NULL CHECK(json_valid(state_json)), created_at TEXT NOT NULL,
 updated_at TEXT NOT NULL,
 FOREIGN KEY(base_version_id, campaign_id) REFERENCES published_versions(id, campaign_id)
);
CREATE TABLE operation_receipts (
 operation_id TEXT PRIMARY KEY, owner_id TEXT NOT NULL REFERENCES accounts(id),
 request_id TEXT NOT NULL, request_digest TEXT NOT NULL, kind TEXT NOT NULL,
 status TEXT NOT NULL, result_json TEXT, public_error_code TEXT, created_at TEXT NOT NULL,
 UNIQUE(owner_id, request_id)
);
CREATE TABLE session_version_memberships (
 session_id TEXT NOT NULL REFERENCES playthroughs(id),
 version_id TEXT NOT NULL REFERENCES published_versions(id),
 entered_at_revision INTEGER NOT NULL, entered_at TEXT NOT NULL,
 PRIMARY KEY(session_id, version_id)
);
CREATE TABLE turn_attempts (
 id TEXT PRIMARY KEY, operation_id TEXT NOT NULL REFERENCES operation_receipts(operation_id),
 session_id TEXT NOT NULL REFERENCES playthroughs(id), prior_attempt_id TEXT REFERENCES turn_attempts(id),
 expected_revision INTEGER NOT NULL, state TEXT NOT NULL,
 player_input TEXT NOT NULL, -- owner-private retry input; never a public event/log field
 provider_outcome_uncertain INTEGER NOT NULL CHECK(provider_outcome_uncertain IN (0,1)),
 captured_profile_json TEXT CHECK(captured_profile_json IS NULL OR json_valid(captured_profile_json)),
 created_at TEXT NOT NULL
 -- captured_profile_json is redacted metadata only; keys never go here.
);
CREATE TABLE accepted_turns (
 id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES playthroughs(id),
 operation_id TEXT NOT NULL UNIQUE REFERENCES operation_receipts(operation_id),
 revision INTEGER NOT NULL, player_input TEXT NOT NULL, public_narration TEXT NOT NULL,
 created_at TEXT NOT NULL, UNIQUE(session_id, revision)
);
CREATE TABLE session_changes (
 id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES playthroughs(id),
 revision INTEGER NOT NULL, operation_id TEXT NOT NULL REFERENCES operation_receipts(operation_id),
 kind TEXT NOT NULL, changes_json TEXT NOT NULL CHECK(json_valid(changes_json)),
 created_at TEXT NOT NULL, UNIQUE(session_id, revision)
);
CREATE TABLE session_checkpoints (
 id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES playthroughs(id),
 revision INTEGER NOT NULL, base_version_id TEXT NOT NULL REFERENCES published_versions(id),
 reason TEXT NOT NULL, world_json TEXT NOT NULL CHECK(json_valid(world_json)), created_at TEXT NOT NULL
);
CREATE TABLE editor_proposals (
 id TEXT PRIMARY KEY, owner_id TEXT NOT NULL REFERENCES accounts(id),
 campaign_id TEXT NOT NULL REFERENCES campaigns(id), base_persisted_revision INTEGER NOT NULL,
 base_buffer_revision INTEGER NOT NULL, candidate_json TEXT NOT NULL CHECK(json_valid(candidate_json)),
 status TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE provider_profiles (
 id TEXT PRIMARY KEY, owner_id TEXT NOT NULL REFERENCES accounts(id), name TEXT NOT NULL,
 endpoint TEXT NOT NULL, model TEXT NOT NULL, protocol TEXT NOT NULL,
 configuration_revision INTEGER NOT NULL, credential_reference TEXT,
 is_active INTEGER NOT NULL CHECK(is_active IN (0,1))
);
CREATE UNIQUE INDEX one_active_profile_per_account ON provider_profiles(owner_id) WHERE is_active = 1;
CREATE TABLE pending_notifications (
 event_id TEXT PRIMARY KEY, operation_id TEXT NOT NULL REFERENCES operation_receipts(operation_id),
 session_id TEXT REFERENCES playthroughs(id), kind TEXT NOT NULL,
 identifiers_json TEXT NOT NULL CHECK(json_valid(identifiers_json)), created_at TEXT NOT NULL
 -- IDs only, not private context or provider secrets. Same transaction as accepted changes.
);
CREATE TABLE consumer_receipts (
 event_id TEXT NOT NULL REFERENCES pending_notifications(event_id), consumer_id TEXT NOT NULL,
 processed_at TEXT NOT NULL, PRIMARY KEY(event_id, consumer_id)
);
CREATE TABLE milestone_hits (
 session_id TEXT NOT NULL REFERENCES playthroughs(id), marker_id TEXT NOT NULL,
 definition_fingerprint TEXT NOT NULL, campaign_version_id TEXT NOT NULL REFERENCES published_versions(id),
 owner_id TEXT NOT NULL REFERENCES accounts(id), source_event_id TEXT NOT NULL,
 first_reached_at TEXT NOT NULL, PRIMARY KEY(session_id, marker_id, definition_fingerprint)
);
