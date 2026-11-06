import streamlit as st

from .common import _todo


def reports() -> None:
    st.header("Activity & milestones")
    _todo(
        "REPORTS / UI",
        "Owner-only aggregates, campaign/version filters, labeled denominators and freshness.",
    )
    st.text_input("Campaign filter")
    st.text_input("Published version filter (optional)")
    st.dataframe(
        {
            "Metric": [
                "Playthroughs started",
                "Accepted turns",
                "Rejected / failed attempts",
                "Marker playthrough count",
                "Marker distinct-account count",
            ],
            "Value": ["Not measured"] * 5,
        },
        hide_index=True,
    )
