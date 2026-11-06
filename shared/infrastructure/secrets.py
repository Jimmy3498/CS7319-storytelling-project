from pathlib import Path

from ..errors import unfinished
from ..models.common import SecretInput


class LocalCredentialStore:
    def __init__(self, private_root: Path) -> None:
        self.private_root = private_root  # No read/write occurs on construction.

    def read(self, owner_id: str, reference: str) -> SecretInput:
        """TODO PROFILES: owner-scoped opaque ref; secret storage outside version control.
        Engineering default: OS credential vault through the optional Python keyring adapter.
        Fail closed if no usable backend exists; no plaintext-file/SQLite fallback. Namespace
        references by installation and account. Never enumerate another account's credentials.
        """
        unfinished("PROFILES")

    def write(self, owner_id: str, reference: str, value: SecretInput) -> None:
        """TODO PROFILES: owner check, OS credential vault, sanitized failures."""
        unfinished("PROFILES")

    def remove(self, owner_id: str, reference: str) -> None:
        """TODO PROFILES: explicit retirement; active request captures retain their own copy."""
        unfinished("PROFILES")
