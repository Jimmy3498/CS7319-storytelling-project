"""Shared Streamlit shell. Each application supplies its own gateway factory."""

import atexit
from collections.abc import Callable
from uuid import uuid4

import streamlit as st

from shared.commands import RegisterAccount
from shared.gateway import ApplicationGateway
from shared.models.common import RequestContext, SecretInput
from shared.ui.shell import PAGES, ScreenController
from shared.work_items import WORK_ITEMS


@st.cache_resource
def _host(architecture: str, _build: Callable[[], ApplicationGateway]) -> ApplicationGateway:
    host = _build()
    atexit.register(host.close)
    return host


def run(architecture: str, build: Callable[[], ApplicationGateway]) -> None:
    st.set_page_config(page_title=f"CS7319 | {architecture}", page_icon="📚", layout="wide")
    st.title(f"AI-powered storytelling · {architecture}")
    st.warning("Scaffold preview — business controls are disabled.")
    st.sidebar.caption(f"Running: {architecture}")
    page = st.sidebar.radio("Workspace", PAGES, key="page")
    st.session_state.setdefault("_client_session_id", str(uuid4()))
    host = _host(architecture, build)
    context = RequestContext(st.session_state["_client_session_id"], None, "scaffold-ui")
    ScreenController(host, context).render(page)
    with st.sidebar.expander("Structural wiring probe"):
        st.caption("Dispatch a test command. Expected result: UNIMPLEMENTED.")
        key = f"_probe_{architecture}"
        if st.button("Probe command route"):
            receipt = host.submit(
                context,
                RegisterAccount("scaffold-probe", SecretInput("NOT-A-REAL-PASSWORD")),
                str(uuid4()),
            )
            st.session_state[key] = receipt.operation_id
        if key in st.session_state:
            if st.button("Refresh probe status"):
                pass  # Poll only; never redispatch the command on rerun.
            receipt = host.poll(context, st.session_state[key])
            st.write(receipt.status.value)
            st.caption(receipt.message)
    with st.expander("Contribution map"):
        for item_id, item in WORK_ITEMS.items():
            st.markdown(f"**{item_id} — {item.title}**")
            st.caption(" | ".join(item.files))
