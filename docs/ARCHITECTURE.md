# Two architectures, shared capabilities

Shared modules provide business capabilities; each architecture owns its workflow coordination.
UI calls ApplicationGateway, services use repository/provider ports, and composition roots supply
the adapters. Models and the codec have no I/O. Screens access infrastructure through services.

## Design baseline and refinement

Component boundaries, connector policies and diagrams can evolve under the change workflow in
[CONTRIBUTING](../CONTRIBUTING.md). Keep the two implementations functionally equivalent.
These views cover application responsibilities and their provider/storage boundaries.

## Repository and build boundaries

The repository contains two applications, not one app with an architecture switch:

- `layered/`: Layered entrypoint, composition root, coordination and build target.
- `event_based/`: Event-Based entrypoint, composition root, coordination and build target.
- `shared/`: models, capabilities, adapters and UI components used by both.

Each app supplies one gateway factory to the shared UI shell. Dependencies point from each app to
`shared`, never between the apps or from `shared` back to an app. Build targets use common packaging
utilities but read only their own application's code and common inputs. The other application can be
absent during a build. Bundles retain the same entrypoints used during development, with separate
server configuration and local data paths. See [build instructions](../README.md#build-each-demo).

## Layered

`ScreenController → LayeredGateway → LayeredApplication → domain-facing services → infrastructure ports`.
Results return along the same path. A turn calls prepare, capture, privileged
planning, validation, disclosure authorization, player projection, narration, atomic commit, then reporting.
A report failure after commit returns the accepted turn with reporting-pending status.
Reporting catch-up uses an explicit call.

## Event-Based

`ScreenController → EventGateway → Queue → registered component handler`.
Publishing returns without executing a handler. A separate worker dispatches subscriptions. Mutating
commands have distinct topics. Read-only queries may use authorized projections directly.

Normal-turn topology:

1. `turn.requested`: authenticate, admit/deduplicate, capture state/configuration and private work reference.
2. `turn.context_prepared`: Director model handler creates typed plan.
3. `turn.plan_proposed`: validator computes candidate and permitted player projection.
4. `turn.validated_for_narration`: narrator gets only player-scoped NarrationWork.
5. `turn.narration_proposed`: persistence handler atomically commits state/transcript/receipt/notice.
6. `turn.committed`: **independent result and reporting subscribers**; each acknowledges separately.
7. `turn.rejected_or_failed`: attempt history and safe status, no accepted-state mutation.

Editor, account, campaign, profile and session commands also use queued handlers. Multistage handlers
publish continuation messages; terminal handlers complete or acknowledge the operation. The bus handles routing.

The current queue is unbounded and in-memory. One worker invokes subscribers sequentially, with separate
error handling for each subscriber. Shutdown drops queued commands and fails their transient receipts;
running network calls need cancellation/fencing. Recovery replays committed notifications, never paid requests.

## Component → class/module → connector map

| Component | Implementing class/module | Connector |
|---|---|---|
| Shared UI | ScreenController, shared/ui page functions | ApplicationGateway.submit/poll/query |
| Layered application | LayeredGateway, LayeredApplication | Direct typed service calls |
| Event ingress | EventGateway | InProcessBus.publish; status/query interface |
| Event connector | InProcessBus | Queue + topic/subscription callback |
| Event components | ComponentHandlers named methods | Message topics and opaque work references |
| Private stage state | WorkflowStateStore, TurnWork, NarrationWork | Owner/stage-scoped read/retain/release |
| Event recovery | CompletionRecovery | SessionRepository pending notices; bus publication |
| Accounts | AccountService, ScryptPasswordHasher | AccountRepository / PasswordHasher |
| World/publication | WorldService | CampaignRepository |
| Coeditor | EditorService | EditorProposalRepository + AIService |
| Session/gameplay | GameplayService | CampaignRepository / SessionRepository |
| Disclosure/context | KnowledgePolicy | Typed internal state → authorized DTO |
| AI generation | AIService | ProviderTransport |
| API cards | ProfileService | ProfileRepository / CredentialStore |
| Updates | UpdateService | CampaignRepository / SessionRepository |
| Reporting | ReportingService | ReportRepository; direct call or independent subscriber |
| Queries | QueryService | Authorized projections through domain/repository ports |
| Shared persistence | SQLiteStore, schema.sql | Typed repository ports / short SQL transactions |
| Secrets | LocalCredentialStore | OS keyring port |
| HTTP / deterministic test | CompatibleHttpProvider / ScriptedTestProvider | ProviderTransport.complete |
| Transient status | OperationStatusStore | Process-local receipts |

Diagrams: [Layered](diagrams/layered.mmd), [Event-Based](diagrams/event-based.mmd),
[class/port overview](diagrams/classes.mmd). Update these views with interface details and interaction
sequences as implementation progresses. [STATUS](STATUS.md) tracks the unfinished components.

## Connector characterization

Describe each boundary using the course's connector types and dimensions. Identify relevant requires,
prohibits, restricts and cautions relationships between their properties.

| Boundary | Baseline and status | Properties to specify/evaluate |
|---|---|---|
| Gateway/service calls | Typed, local, synchronous procedure calls | Entry points, parameters, accessibility, cardinality, error propagation |
| Event publication/subscription | Queued dispatch implemented; one FIFO worker, sequential subscribers, no durable queue | Delivery, ordering/causality, notification, capacity, scheduling, failure isolation |
| Repository/SQLite | Typed ports and SQL schema | Data access, transaction scope, locking, availability, concurrent updates |
| Provider adapter/HTTP | Nonstreaming request/response port | Adaptation, deadlines, response bounds, credential scope, uncertain remote outcomes |

## Risk analysis and comparison evidence

For each selected risk, record its cause, affected requirement, test scenario, observed consequence,
mitigation and remaining limitation. Evaluate both architectures using comparable conditions.

| Risk to investigate | Experiment | Evidence |
|---|---|---|
| Slow provider/single-worker blocking | Inject the same provider delay and a second independent request | Queue wait, completion time and call/dispatch traces |
| Commit-before-notification failure | Interrupt after commit, resume and redeliver the notice | Preserved state, recovery time and zero duplicate local effects |
| Reporting failure | Fail the report path while processing an accepted turn | Gameplay result, report lag and catch-up behavior |
| Private data crossing an interface | Submit tagged private canaries through planning/narration and queries | Exact outgoing payloads and negative isolation assertions |

Use the same campaign, input sequence, prompts, scripted responses/delays and persistence semantics.
Record the environment, versions, traces, sample counts and ranges. Measure provider time separately
from submit-to-confirm, dispatch, persistence, report lag and recovery. Include stale updates, invalid
proposals, duplicate delivery and storage/subscriber failures. Run these experiments on completed
workflows and use the results to justify the final style selection.
