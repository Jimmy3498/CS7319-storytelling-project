from ..commands import ActivateProviderCard, DeleteProviderCard, SaveProviderCard
from ..errors import unfinished
from ..models.ai import ProviderCapture, ProviderProfile
from ..ports import CredentialStore, ProfileRepository


class ProfileService:
    def __init__(self, repository: ProfileRepository, credentials: CredentialStore) -> None:
        self.repository = repository
        self.credentials = credentials

    def save(self, owner_id: str, command: SaveProviderCard) -> ProviderProfile:
        """TODO PROFILES: validate supported protocol/HTTPS-or-loopback endpoint and model;
        enforce owner/revision; store secret separately. Endpoint change clears/rebinds key.
        Save does not activate a new card or make a network request. Return redacted metadata.
        """
        unfinished("PROFILES")

    def activate(self, owner_id: str, command: ActivateProviderCard) -> ProviderProfile:
        """TODO PROFILES: owner and readiness checks; next-request default only."""
        unfinished("PROFILES")

    def delete(self, owner_id: str, command: DeleteProviderCard) -> None:
        """TODO PROFILES: enforce owner/revision; require replacement or explicit disabled
        state if active. Retire credentials safely without disrupting admitted captures.
        """
        unfinished("PROFILES")

    def capture(self, owner_id: str) -> ProviderCapture:
        """TODO PROFILES: freeze active profile and credential for this operation. One account's
        card serves editor and gameplay; never reuse another account's cache/history/secret.
        """
        unfinished("PROFILES")
