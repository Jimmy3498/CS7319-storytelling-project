import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from event_based.bootstrap import build
from shared.ui.app import run

run("Event-Based", build)
