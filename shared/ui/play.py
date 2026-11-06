import streamlit as st

from .common import _buttons, _todo


def play() -> None:
    st.header("My playthroughs")
    _todo(
        "GAMEPLAY / UI",
        "MY_SESSIONS/RESUME_SESSION → player-only DTO; SubmitTurn with expected revision.",
    )
    st.selectbox("Select a saved session", ("Select a session",))
    st.caption("Show accepted history after validation and save.")
    with st.form("turn_form"):
        st.text_area("What do you do or say?")
        st.form_submit_button("Send action", disabled=True)
    _buttons("Refresh pending operation", "Retry explicitly", "Resume saved session")
    st.markdown("**Published campaign update**")
    st.caption(
        "Show available updates with player-visible conflict summaries. Keep the current version until adoption."
    )
    _buttons("Continue old version", "Preview update", "Adopt compatible update")
