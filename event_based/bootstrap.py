from pathlib import Path

from shared.wiring import compose_services

from .gateway import EventGateway


def build(data_root: Path | None = None, start_worker: bool = True) -> EventGateway:
    root = data_root or Path(__file__).resolve().parents[1] / ".local" / "event_based"
    return EventGateway(compose_services(root), start_worker=start_worker)
