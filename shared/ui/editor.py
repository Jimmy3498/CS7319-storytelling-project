import streamlit as st

from .common import _access, _buttons, _condition, _todo


def editor() -> None:
    st.header("World editor")
    _todo(
        "WORLD / EDITOR / UI",
        "Owned draft query → local EditorBuffer → SaveDraft; publish is separate.",
    )
    st.text_input("Campaign ID / draft selection", placeholder="Bind to MY_CAMPAIGNS query")
    tabs = st.tabs(
        [
            "Setup",
            "Canon & knowledge",
            "Characters",
            "Locations",
            "Items",
            "Relationships",
            "Rules & stats",
            "Milestones",
            "AI coeditor",
        ]
    )
    with tabs[0]:
        st.text_input("Campaign title")
        st.text_area("Public catalog summary")
        st.text_area("Public setting/background")
        st.text_area("Opening scene")
    with tabs[1]:
        st.text_input("Record ID", key="canon_id")
        st.text_input("Record title", key="canon_title")
        st.text_area("Record text", key="canon_text")
        st.selectbox("Statement stance", ("authored_fact", "belief", "claim", "hearsay"))
        st.text_input("Holder ID for belief/claim")
        _access("canon")
        st.markdown("**Optional disclosure condition**")
        _condition("canon_reveal")
        _buttons("Add knowledge record", "Apply knowledge edit", "Remove knowledge record")
    with tabs[2]:
        st.text_input("Character ID")
        st.text_input("Character name")
        st.checkbox("Playable preset character")
        st.text_input("Starting location ID")
        st.text_area("Appearance / public image")
        st.text_area("Expression style / public manner")
        st.text_area("Core personality / private notes")
        st.text_area("Personal history")
        st.caption(
            "Personality/history are separately classified TextRecords; beliefs/secrets use knowledge records."
        )
        _access("character_private")
        _buttons("Add character", "Apply character edit", "Remove character")
    with tabs[3]:
        st.text_input("Location ID")
        st.text_input("Location name")
        st.text_area("Location description")
        st.text_input("Connected location IDs")
        _access("location")
        _buttons("Add location", "Apply location edit", "Remove location")
    with tabs[4]:
        st.markdown("**Item templates**")
        st.text_input("Template ID")
        st.text_input("Template name")
        st.text_area("Template description")
        _access("item_template")
        st.number_input("Maximum instances per session", min_value=1, value=1)
        _condition("spawn")
        st.markdown("**Initial item instances**")
        st.text_input("Instance ID")
        st.text_input("Instance template ID")
        st.text_input("Holder character ID OR location ID")
        _access("item_instance")
        _buttons("Add template", "Add initial instance", "Apply item edit", "Remove item")
        st.caption("Runtime item creation uses permitted templates.")
    with tabs[5]:
        st.text_input("Relationship ID")
        st.text_input("Source character ID")
        st.text_input("Target character ID")
        st.text_input("Relationship label")
        st.text_area("Relationship description")
        _access("relation")
        _buttons("Add relationship", "Apply relationship edit", "Remove relationship")
    with tabs[6]:
        st.text_area("Narrative guidance")
        st.text_input("Stat ID / target entity or relationship ID")
        st.number_input("Stat minimum", value=0)
        st.number_input("Stat value", value=50)
        st.number_input("Stat maximum", value=100)
        _access("stat")
        st.text_area("Stat-band text, one authored range per record")
        st.text_input("Flag ID")
        st.checkbox("Initial flag value")
        _condition("flag_permission")
        _buttons("Apply rule/stat/flag edit")
    with tabs[7]:
        st.text_input("Milestone ID")
        st.text_input("Milestone label")
        _condition("milestone")
        _buttons("Add milestone", "Apply milestone edit", "Remove milestone")
        st.caption(
            "Changing a condition starts a new milestone series; earlier counts stay separate."
        )
    with tabs[8]:
        st.text_area("Instruction to AI coeditor")
        st.text_input("Selected record IDs / editing scope")
        _buttons("Request proposal", "Accept into buffer", "Reject proposal")
        st.caption(
            "TODO: show the proposed diff, revision checks and errors. Accept into the buffer, then Save."
        )
    st.divider()
    _buttons("Save Draft", "Check Readiness", "Publish Version")
    st.caption(
        "TODO UI: repeatable record selection/CRUD, dirty-state navigation protection, specific readiness errors and reload conflicts."
    )
