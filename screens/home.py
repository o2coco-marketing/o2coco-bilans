"""Écran d'accueil."""
import streamlit as st

import config


def render() -> None:
    st.title(config.APP_TITLE)
    st.write(
        "Cette application lit automatiquement vos factures fournisseurs et prépare un "
        "tableau récapitulatif prêt pour votre expert-comptable."
    )
    st.divider()

    if st.button("+ Création nouveau bilan mensuel", type="primary"):
        st.session_state["step"] = "upload"
        st.rerun()

    st.divider()
    api_key = config.get_api_key() or ""
    with st.expander("Paramètres"):
        st.caption(f"Clé API actuellement utilisée : se termine par « ...{api_key[-4:]} »" if api_key else "Aucune clé enregistrée.")
        if st.button("Modifier la clé API"):
            st.session_state["step"] = "setup"
            st.rerun()
