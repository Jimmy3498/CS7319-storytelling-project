import streamlit as st

from .common import _buttons, _todo


def account() -> None:
    st.header("Account")
    _todo(
        "AUTH / UI",
        "RegisterAccount, Login, Logout; authenticated server session and account-scoped UI reset.",
    )
    with st.form("account_form"):
        st.text_input("Username")
        st.text_input("Password", type="password", disabled=True)
        st.form_submit_button("Sign in", disabled=True)
    _buttons("Register account", "Sign out")
