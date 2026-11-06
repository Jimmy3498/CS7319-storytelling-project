from dataclasses import dataclass


@dataclass(frozen=True)
class AccountView:
    id: str
    username: str


@dataclass(frozen=True)
class LoginResult:
    account: AccountView
    # Real login session handling belongs to AUTH; never trust a user_id widget.
    session_reference: str
