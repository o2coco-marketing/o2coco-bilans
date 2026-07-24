"""Écran de révision/correction manuelle, puis génération du bilan Excel final."""
import streamlit as st

import business_rules
from config import DEPARTEMENTS, DESIGNATIONS, MISSING_SELECT_MARKER, MISSING_TEXT_MARKER
from excel_export import build_filename, build_workbook
from state import COLUMN_LABELS, CORE_COLUMNS, dataframe_to_rows


def _build_display_df(df):
    """Copie du tableau avec marqueur 🔴 écrit directement dans les cases obligatoires vides."""
    display = df.copy()
    for idx in display.index:
        if not display.at[idx, "nom_fournisseur"]:
            display.at[idx, "nom_fournisseur"] = MISSING_TEXT_MARKER
        if not display.at[idx, "departement"]:
            display.at[idx, "departement"] = MISSING_SELECT_MARKER
        designation = display.at[idx, "designation"]
        if business_rules.requires_amortissement(designation) and not display.at[idx, "amortissement_note"]:
            display.at[idx, "amortissement_note"] = MISSING_TEXT_MARKER
    return display


def render() -> None:
    month_label = st.session_state.get("bilan_month_label", "")
    st.title(f"Révision — Bilan de {month_label}")
    st.write(
        "Vérifiez et corrigez les informations extraites automatiquement avant de générer le "
        "bilan. Rien n'est enregistré tant que vous n'avez pas cliqué sur "
        "« Générer le bilan mensuel »."
    )

    df = st.session_state["invoices_df"]
    extra = st.session_state["invoice_extra"]

    if df.empty:
        st.warning("Aucune facture à afficher.")
        if st.button("← Retour à l'accueil"):
            st.session_state["step"] = "home"
            st.rerun()
        return

    error_entries = [
        (
            extra.get(row_id, {}).get("source_filename", row_id),
            extra.get(row_id, {}).get("extraction_error_message"),
            extra.get(row_id, {}).get("extraction_technical_detail"),
        )
        for row_id in df["id"]
        if extra.get(row_id, {}).get("extraction_status") == "error"
    ]
    if error_entries:
        filenames = [name for name, _, _ in error_entries]
        st.warning(
            "⚠️ Ces fichiers n'ont pas pu être analysés automatiquement et doivent être "
            "complétés manuellement dans le tableau ci-dessous : " + ", ".join(filenames)
        )
        distinct_messages = sorted({msg for _, msg, _ in error_entries if msg})
        for msg in distinct_messages:
            st.error(f"Raison indiquée par le système : {msg}")
        distinct_details = sorted({detail for _, _, detail in error_entries if detail})
        if distinct_details:
            with st.expander("🔧 Détail technique (à copier-coller si vous demandez de l'aide)"):
                for detail in distinct_details:
                    st.code(detail, language=None)

    st.caption("🔴 dans une case = information obligatoire à compléter.")
    st.subheader("Tableau récapitulatif")
    display_df = _build_display_df(df)
    edited_df = st.data_editor(
        display_df,
        column_order=[c for c in CORE_COLUMNS if c != "id"],
        column_config={
            "nom_fournisseur": st.column_config.TextColumn(
                COLUMN_LABELS["nom_fournisseur"],
                help="Nom de l'entreprise (ex: AUCHAN). Obligatoire — à compléter à la main si l'IA ne l'a pas trouvé.",
                required=True,
            ),
            "numero_facture": st.column_config.TextColumn(COLUMN_LABELS["numero_facture"]),
            "numero_client_fournisseur": st.column_config.TextColumn(
                COLUMN_LABELS["numero_client_fournisseur"]
            ),
            "numero_tahiti_siret": st.column_config.TextColumn(
                COLUMN_LABELS["numero_tahiti_siret"]
            ),
            "date_facture": st.column_config.DateColumn(
                COLUMN_LABELS["date_facture"], format="DD/MM/YYYY", required=True
            ),
            "date_echeance": st.column_config.DateColumn(
                COLUMN_LABELS["date_echeance"], format="DD/MM/YYYY", required=True
            ),
            "designation": st.column_config.SelectboxColumn(
                COLUMN_LABELS["designation"], options=DESIGNATIONS, required=True
            ),
            "montant_ht": st.column_config.NumberColumn(
                COLUMN_LABELS["montant_ht"], format="%d", step=1, required=True
            ),
            "taux_tva": st.column_config.NumberColumn(
                COLUMN_LABELS["taux_tva"], format="%d", step=1
            ),
            "montant_tva": st.column_config.NumberColumn(
                COLUMN_LABELS["montant_tva"], format="%d", step=1
            ),
            "departement": st.column_config.SelectboxColumn(
                COLUMN_LABELS["departement"], options=DEPARTEMENTS, required=True
            ),
            "amortissement_note": st.column_config.TextColumn(
                COLUMN_LABELS["amortissement_note"],
                help="Obligatoire uniquement pour les factures « technologie ». Laisser vide sinon.",
            ),
        },
        num_rows="fixed",
        hide_index=True,
        use_container_width=True,
        key="invoices_editor",
    )
    st.session_state["invoices_df"] = edited_df

    flagged_entries = []
    for idx in edited_df.index:
        row_id = edited_df.at[idx, "id"]
        row_extra = extra.setdefault(row_id, {})
        original_values = row_extra.get("original_values", {})
        verified = set(row_extra.get("verified_fields", []))

        for field in row_extra.get("uncertain_fields", []):
            if field in verified:
                continue
            current = edited_df.at[idx, field] if field in edited_df.columns else None
            if current in (MISSING_TEXT_MARKER, MISSING_SELECT_MARKER):
                continue  # case encore vide : ce n'est pas une correction, ne compte pas comme vérifié
            if current != original_values.get(field):
                verified.add(field)
        row_extra["verified_fields"] = list(verified)

        filename = row_extra.get("source_filename", "")
        supplier = edited_df.at[idx, "nom_fournisseur"]
        if not supplier or supplier == MISSING_TEXT_MARKER:
            supplier = filename or "Facture"
        for field in row_extra.get("uncertain_fields", []):
            if field not in verified:
                flagged_entries.append((row_id, field, supplier, filename))

    st.session_state["invoice_extra"] = extra

    if flagged_entries:
        st.warning(
            "⚠️ **À vérifier** — l'IA n'était pas sûre d'avoir bien lu ces valeurs. Corrige la case "
            "concernée dans le tableau ci-dessus (elle sort automatiquement de cette liste), ou "
            "clique « Vérifié » si la valeur affichée était déjà correcte :"
        )
        for row_id, field, supplier, filename in flagged_entries:
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"**{supplier}** ({filename}) — {COLUMN_LABELS[field]}")
            with col_b:
                if st.button("✅ Vérifié", key=f"verify_{row_id}_{field}"):
                    row_extra = extra.setdefault(row_id, {})
                    verified = set(row_extra.get("verified_fields", []))
                    verified.add(field)
                    row_extra["verified_fields"] = list(verified)
                    st.session_state["invoice_extra"] = extra
                    st.rerun()

    st.subheader("Aperçus — factures « technologie »")
    needing_amortissement = edited_df[
        edited_df["designation"].apply(business_rules.requires_amortissement)
    ]
    if needing_amortissement.empty:
        st.caption("Aucune facture « technologie » pour l'instant.")
    else:
        st.caption(
            "Ces factures sont classées « technologie » : complétez la colonne « Amortissement » "
            "directement dans le tableau ci-dessus. Un aperçu rapide de chaque facture est "
            "disponible ci-dessous si besoin de vérifier."
        )
        for _, table_row in needing_amortissement.iterrows():
            row_id = table_row["id"]
            row_extra = extra.get(row_id, {})
            filename = row_extra.get("source_filename", "")
            label = filename or "Facture"
            with st.popover(f"🔍 {label}"):
                preview_bytes = row_extra.get("preview_bytes")
                preview_media_type = row_extra.get("preview_media_type")
                if preview_media_type == "image/jpeg" and preview_bytes:
                    st.image(preview_bytes)
                else:
                    st.caption("Aperçu non disponible pour ce fichier (PDF).")

    st.session_state["invoice_extra"] = extra

    rows = dataframe_to_rows(edited_df, extra)

    st.divider()
    incomplete = [
        row
        for row in rows
        if not business_rules.is_row_complete(
            row.designation, row.departement, row.amortissement_note, row.nom_fournisseur
        )
    ]
    if incomplete:
        missing_labels = [
            row.source_filename or (row.numero_facture or "facture sans nom")
            for row in incomplete
        ]
        st.error(
            f"⚠️ {len(incomplete)} facture(s) incomplète(s) : le nom du fournisseur et le service du "
            "restaurant (et l'amortissement si nécessaire) doivent être renseignés — " + ", ".join(missing_labels)
        )

    total_ht = sum(row.montant_ht for row in rows)
    total_tva = sum(row.montant_tva for row in rows)
    col1, col2 = st.columns(2)
    col1.metric("Total Montant HT", f"{total_ht:,.0f} XPF".replace(",", " "))
    col2.metric("Total TVA", f"{total_tva:,.0f} XPF".replace(",", " "))

    st.divider()
    col_back, col_generate = st.columns(2)
    with col_back:
        if st.button("← Retour à l'accueil"):
            st.session_state["step"] = "home"
            st.rerun()
    with col_generate:
        if st.button("Générer le bilan mensuel", type="primary"):
            month_key = st.session_state.get("bilan_month_key", "bilan")
            workbook = build_workbook(rows, month_label)
            st.session_state["generated_workbook"] = workbook.getvalue()
            st.session_state["generated_filename"] = build_filename(month_key)

    if st.session_state.get("generated_workbook"):
        st.success("Le bilan a été généré avec succès.")
        st.download_button(
            "📥 Télécharger le fichier Excel",
            data=st.session_state["generated_workbook"],
            file_name=st.session_state["generated_filename"],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
        )
