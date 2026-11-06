import streamlit as st

from .common import _buttons, _todo


def catalog() -> None:
    st.header("Browse Campaigns")
    _todo(
        "WORLD / UI",
        "CATALOG query returns public summaries only; choose published version and preset PC.",
    )
    st.text_input("Filter campaign titles")
    with st.container(border=True):
        st.subheader("The Thornmere Wedding")
        st.write("A storm-bound wedding becomes an inquiry after a guest collapses.")
        st.caption("Synthetic fixture preview")
        st.selectbox("Preset player character", ("Rowan Vale",))
        _buttons("Start my playthrough")
