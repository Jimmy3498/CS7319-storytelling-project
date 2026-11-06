import streamlit as st


def _todo(area: str, contract: str) -> None:
    st.info(f"TODO {area}: {contract}")


def _access(prefix: str) -> None:
    st.selectbox(
        "Visibility",
        ("Choose classification", "public", "director", "character"),
        key=prefix + "_visibility",
    )
    st.text_input("Character reader IDs, if character-private", key=prefix + "_readers")


def _condition(prefix: str) -> None:
    st.selectbox(
        "Condition", ("none", "at_location", "owns_item", "flag_equals"), key=prefix + "_kind"
    )
    st.text_input("Referenced location / item / flag ID", key=prefix + "_target")
    st.checkbox("Expected flag value (flag_equals only)", value=True, key=prefix + "_expected")


def _buttons(*labels: str) -> None:
    cols = st.columns(len(labels))
    for col, label in zip(cols, labels):
        col.button(label, disabled=True, key=f"{st.session_state.get('page', '')}::{label}")
