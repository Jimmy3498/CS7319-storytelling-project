# CS7319 — AI-Powered Interactive Storytelling

One repository with two Python/Streamlit applications: **Layered** and **Event-Based**.
Each has its own entrypoint, coordinator and build target. Models, business capabilities, adapters
and UI components are maintained once in `shared/`.

This is a contribution scaffold. Business workflows are marked with TODO work IDs;
[STATUS](docs/STATUS.md) lists what runs and what needs implementation.

## Run locally

Use Python **3.12+** and run these commands from the repository root:

```sh
python3 -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the application you want:

```sh
# Layered
python -m streamlit run layered/streamlit_app.py --server.port 8501
# Event-Based (use another terminal to run both side by side)
python -m streamlit run event_based/streamlit_app.py --server.port 8502
```

Each application is fixed to its architecture; there is no combined launcher or runtime selector.
The preview runs locally with business controls disabled. The sidebar wiring probe returns
`UNIMPLEMENTED` and makes no provider calls.

## Build each demo

```sh
python -m layered.build
python -m event_based.build
```

The first command creates `dist/layered-demo.zip`; the second creates `dist/event-based-demo.zip`.
Each also creates an unpacked folder. A build reads only its own application and common inputs;
the other application's source is not required. Extract either ZIP and follow its README.

The Layered demo uses port **8501**; Event-Based uses **8502**. Each keeps its own local data.
Develop in this repository, not in the generated folders. To rebuild without overwriting a previous
output, use `python -m layered.build --output dist/v2` or `python -m event_based.build --output dist/v2`.

## Project layout

| Area | Location |
|---|---|
| Models, commands and interfaces | `shared/models/`, `shared/commands.py`, `shared/ports.py` |
| Business capabilities | `shared/domain/` |
| SQLite, credential and HTTP adapters | `shared/infrastructure/` |
| Screens | `shared/ui/` |
| Layered app, coordination and build target | `layered/` |
| Event-Based app, coordination and build target | `event_based/` |
| Demo campaign | `fixtures/thornmere.json` |
| Work IDs | `shared/work_items.py` |

Dependency direction: `layered → shared ← event_based`. Neither application imports the other;
shared code imports neither. The two builds reuse packaging utilities in `scripts/demo_bundle.py`.

## Contribute

Choose a capability in [CONTRIBUTING](CONTRIBUTING.md), read its [contract](docs/CONTRACTS.md) and
[acceptance cases](docs/ACCEPTANCE.md), and integrate it through both architectures.
[ARCHITECTURE](docs/ARCHITECTURE.md) maps the components, connectors and classes.

## Check your changes

```sh
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -m ruff format --check .
python scripts/check_scaffold.py
python scripts/check_public_tree.py
python scripts/wiring_smoke.py
python -m unittest discover -s tests -v
```

## MVP scope

One account can author and play. Planned features include world/entity editing, reviewed AI coediting,
a campaign catalog, preset player characters, independent sessions, validated turns, save/resume,
template-based item creation, compatible campaign updates, milestone reports and private API cards.
Player views enforce character knowledge and disclosure rules.

Marketplace/payments, multiplayer, custom player-character creation, rulebook interpretation and
intelligent campaign merging are outside this MVP.

## References and credits

[SillyTavern](https://github.com/SillyTavern/SillyTavern) is a reference for LLM-assisted roleplay and
provider configuration. See [fixture provenance](fixtures/README.md) for the demo campaign's source.

The initial scaffold, documentation and fixture adaptation were AI-assisted. A project license has
not yet been selected.
