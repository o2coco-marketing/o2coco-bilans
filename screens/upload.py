"""Écran d'import des factures pour un nouveau bilan mensuel."""
from datetime import date

import streamlit as st

import business_rules

MIN_RECOMMENDED = 5
MAX_ALLOWED = 300


def render() -> None:
    st.title("Nouveau bilan mensuel")
    st.write(
        "Choisissez le mois concerné, puis importez toutes les factures fournisseurs de ce "
        "mois (photos ou fichiers PDF)."
    )

    today = date.today()
    years = list(range(today.year - 2, today.year + 1))
    col1, col2 = st.columns(2)
    with col1:
        month = st.selectbox(
            "Mois",
            options=list(range(1, 13)),
            format_func=lambda m: business_rules.MONTH_NAMES_FR[m - 1].capitalize(),
            index=today.month - 1,
        )
    with col2:
        year = st.selectbox("Année", options=years, index=len(years) - 1)

    files = st.file_uploader(
        f"Factures (JPG, PNG ou PDF) — entre {MIN_RECOMMENDED} et {MAX_ALLOWED} fichiers",
        type=["jpg", "jpeg", "png", "pdf"],
        accept_multiple_files=True,
    )

    can_start = False
    if files:
        st.info(f"{len(files)} fichier(s) sélectionné(s).")
        if len(files) < MIN_RECOMMENDED:
            st.warning(
                f"Vous pouvez continuer avec moins de {MIN_RECOMMENDED} factures, mais "
                "l'application est surtout conçue pour traiter des lots complets."
            )
            can_start = True
        elif len(files) > MAX_ALLOWED:
            st.error(
                f"Merci de ne pas dépasser {MAX_ALLOWED} factures en une seule fois. "
                "Séparez votre import en plusieurs lots."
            )
            can_start = False
        else:
            can_start = True

    st.divider()
    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("← Retour à l'accueil"):
            st.session_state["step"] = "home"
            st.rerun()
    with col_next:
        if st.button("Analyser les factures →", type="primary", disabled=not can_start):
            st.session_state["upload_files"] = [(f.name, f.getvalue()) for f in files]
            st.session_state["bilan_month_label"] = business_rules.format_month_label(year, month)
            st.session_state["bilan_month_key"] = business_rules.format_month_key(year, month)
            st.session_state["step"] = "processing"
            st.rerun()
