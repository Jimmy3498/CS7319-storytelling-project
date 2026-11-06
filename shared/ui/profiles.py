import streamlit as st

from .common import _buttons, _todo


def profiles() -> None:
    st.header("Private API cards")
    _todo(
        "PROFILES / UI",
        "Owner-scoped list/save/activate/delete; one active default serves editor and play.",
    )
    st.text_input("Card name")
    st.text_input("Full chat-completions endpoint", placeholder="https://HOST/v1/chat/completions")
    st.text_input("Model ID")
    st.selectbox("Protocol", ("chat-completions-compatible",))
    st.text_input("API key", type="password", disabled=True)
    _buttons("Save API card", "Activate for next request", "Delete API card")
    st.caption(
        "Activation applies to the next request. Endpoint changes require a new credential binding."
    )
