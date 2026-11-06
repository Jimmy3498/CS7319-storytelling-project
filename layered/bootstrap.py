from pathlib import Path

from shared.wiring import compose_services

from .application import LayeredApplication
from .gateway import LayeredGateway


def build(data_root: Path | None = None) -> LayeredGateway:
    root = data_root or Path(__file__).resolve().parents[1] / ".local" / "layered"
    return LayeredGateway(LayeredApplication(compose_services(root)))
