import streamlit as st

from shared.gateway import ApplicationGateway
from shared.models.common import RequestContext

from .accounts import account
from .activity import reports
from .catalog import catalog
from .editor import editor
from .play import play
from .profiles import profiles

PAGES = (
    "Overview",
    "Account",
    "Browse Campaigns",
    "My Campaigns / Editor",
    "My Sessions / Play",
    "Activity & Milestones",
    "API Cards",
)

RENDERERS = {
    "Account": account,
    "Browse Campaigns": catalog,
    "My Campaigns / Editor": editor,
    "My Sessions / Play": play,
    "Activity & Milestones": reports,
    "API Cards": profiles,
}


def render(page: str, gateway: ApplicationGateway, context: RequestContext) -> None:
    if page == "Overview":
        st.header("Architecture comparison")
        st.write(
            "Shared capabilities; direct Layered coordination and queued Event-Based coordination."
        )
        st.write(
            "Complete one capability behind its contract, then integrate and test it through both architectures."
        )
    else:
        RENDERERS[page]()


class ScreenController:
    def __init__(self, gateway: ApplicationGateway, context: RequestContext) -> None:
        self.gateway, self.context = gateway, context

    def render(self, page: str) -> None:
        render(page, self.gateway, self.context)
