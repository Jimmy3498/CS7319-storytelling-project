from ..errors import unfinished
from ..models.common import SecretInput


class ScryptPasswordHasher:
    def hash(self, secret: SecretInput) -> str:
        """TODO AUTH: random per-password salt + hashlib.scrypt, versioned parameters.
        Return encoded hash; never store plaintext, unsalted SHA or a reversible password.
        """
        unfinished("AUTH")

    def verify(self, secret: SecretInput, encoded_hash: str) -> bool:
        """TODO AUTH: bounded decode, recompute scrypt and constant-time digest comparison."""
        unfinished("AUTH")
