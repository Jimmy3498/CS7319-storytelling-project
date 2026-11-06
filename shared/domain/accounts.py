from ..commands import Login, RegisterAccount
from ..errors import unfinished
from ..models.accounts import AccountView, LoginResult
from ..models.common import RequestContext
from ..ports import AccountRepository, PasswordHasher


class AccountService:
    def __init__(self, repository: AccountRepository, passwords: PasswordHasher) -> None:
        self.repository = repository
        self.passwords = passwords

    def register(self, context: RequestContext, command: RegisterAccount) -> AccountView:
        """TODO AUTH: normalize unique username; hash with random salt; create account.
        Keep plaintext passwords out of SQL/logs. Return account metadata; login is separate.
        """
        unfinished("AUTH")

    def login(self, context: RequestContext, command: Login) -> LoginResult:
        """TODO AUTH: verify hash; establish server-side login bound to this client session.
        Return generic invalid-credentials errors. Resolve user identity from stored session.
        """
        unfinished("AUTH")

    def logout(self, context: RequestContext) -> None:
        """TODO AUTH: invalidate session; UI clears account-scoped buffers/cards/pending IDs."""
        unfinished("AUTH")

    def require_user(self, context: RequestContext) -> AccountView:
        """TODO AUTH: resolve stored login; reject absent or forged context.user_id."""
        unfinished("AUTH")
