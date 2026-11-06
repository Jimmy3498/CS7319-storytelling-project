"""Compare direct and queued dispatch of a test account command."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from event_based.bootstrap import build as event_based
from layered.bootstrap import build as layered
from shared.commands import RegisterAccount
from shared.models.common import RequestContext, SecretInput


def main() -> None:
    context = RequestContext("structural-probe", None, "probe-correlation")
    command = RegisterAccount("probe", SecretInput("NOT-A-REAL-PASSWORD"))
    direct, queued = layered(), event_based(start_worker=False)
    try:
        result = direct.submit(context, command, "probe-request")
        pending = queued.submit(context, command, "probe-request")
        print("Layered immediate receipt:", result.status.value)
        print(
            "Event-Based initial receipt:",
            pending.status.value,
            "queued messages:",
            queued.bus.pending,
        )
        queued.bus.dispatch_one()
        print(
            "Event-Based after separate dispatch:",
            queued.poll(context, pending.operation_id).status.value,
        )
        print("Metadata-only trace:", queued.bus.trace)
    finally:
        direct.close()
        queued.close()


if __name__ == "__main__":
    main()
