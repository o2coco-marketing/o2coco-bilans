"""Écran d'analyse : lance le traitement du lot et affiche la progression."""
import streamlit as st

import config
from extraction import process_batch
from state import build_extra_map, rows_to_dataframe


def render() -> None:
    st.title("Analyse des factures en cours...")

    files = st.session_state.get("upload_files")
    if not files:
        st.warning("Aucune facture à analyser.")
        if st.button("← Retour à l'import"):
            st.session_state["step"] = "upload"
            st.rerun()
        return

    st.write(f"Merci de patienter, {len(files)} facture(s) sont en cours de lecture automatique.")
    progress_bar = st.progress(0.0)
    status_text = st.empty()

    def on_progress(done: int, total: int) -> None:
        progress_bar.progress(done / total)
        status_text.write(f"Facture {done} / {total} analysée(s)...")

    api_key = config.get_api_key()
    model = config.get_model()
    max_workers = config.get_max_concurrent_requests()

    rows = process_batch(files, api_key, model, max_workers, on_progress=on_progress)

    st.session_state["invoices_df"] = rows_to_dataframe(rows)
    st.session_state["invoice_extra"] = build_extra_map(rows)
    st.session_state.pop("upload_files", None)
    st.session_state.pop("generated_workbook", None)
    st.session_state.pop("generated_filename", None)
    st.session_state["step"] = "review"
    st.rerun()
