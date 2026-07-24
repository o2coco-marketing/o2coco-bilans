"""Modèle de données d'une facture et gestion de st.session_state."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import uuid

import pandas as pd
import streamlit as st


@dataclass
class InvoiceRow:
    source_filename: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    code_facture: str | None = None
    nom_fournisseur: str | None = None
    numero_facture: str | None = None
    numero_client_fournisseur: str | None = None
    numero_tahiti_siret: str | None = None
    date_facture: date | None = None
    date_echeance: date | None = None
    designation: str = "à vérifier manuellement"
    montant_ht: int = 0
    taux_tva: int = 0
    montant_tva: int = 0

    amortissement_note: str | None = None
    departement: str | None = None

    extraction_status: str = "ok"  # "ok" | "error"
    extraction_error_message: str | None = None
    extraction_technical_detail: str | None = None
    preview_bytes: bytes | None = None
    preview_media_type: str | None = None


CORE_COLUMNS = [
    "id",
    "code_facture",
    "nom_fournisseur",
    "numero_facture",
    "numero_client_fournisseur",
    "numero_tahiti_siret",
    "date_facture",
    "date_echeance",
    "designation",
    "montant_ht",
    "taux_tva",
    "montant_tva",
    "departement",
]

COLUMN_LABELS = {
    "code_facture": "Code facture",
    "nom_fournisseur": "Nom fournisseur",
    "numero_facture": "N° facture",
    "numero_client_fournisseur": "N° client fournisseur",
    "numero_tahiti_siret": "N° Tahiti / SIRET",
    "date_facture": "Date facture",
    "date_echeance": "Date d'échéance",
    "designation": "Désignation",
    "montant_ht": "Montant net (HT)",
    "taux_tva": "Taux TVA (%)",
    "montant_tva": "Montant TVA",
    "departement": "Service du restaurant",
}


def init_session_state() -> None:
    st.session_state.setdefault("step", "home")
    st.session_state.setdefault("invoices_df", pd.DataFrame(columns=CORE_COLUMNS))
    st.session_state.setdefault("invoice_extra", {})
    st.session_state.setdefault("bilan_month_label", "")


def rows_to_dataframe(rows: list[InvoiceRow]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=CORE_COLUMNS)
    data = [{col: getattr(row, col) for col in CORE_COLUMNS} for row in rows]
    df = pd.DataFrame(data, columns=CORE_COLUMNS)
    df["date_facture"] = pd.to_datetime(df["date_facture"]).dt.date
    df["date_echeance"] = pd.to_datetime(df["date_echeance"]).dt.date
    return df


def build_extra_map(rows: list[InvoiceRow]) -> dict[str, dict]:
    return {
        row.id: {
            "source_filename": row.source_filename,
            "amortissement_note": row.amortissement_note,
            "extraction_status": row.extraction_status,
            "extraction_error_message": row.extraction_error_message,
            "extraction_technical_detail": row.extraction_technical_detail,
            "preview_bytes": row.preview_bytes,
            "preview_media_type": row.preview_media_type,
        }
        for row in rows
    }


def _safe_int(value, default: int = 0) -> int:
    if value is None or pd.isna(value):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_date(value, default: date) -> date:
    if value is None or pd.isna(value):
        return default
    if isinstance(value, date):
        return value
    try:
        return pd.to_datetime(value).date()
    except (TypeError, ValueError):
        return default


def dataframe_to_rows(df: pd.DataFrame, extra: dict[str, dict]) -> list[InvoiceRow]:
    rows = []
    today = date.today()
    for record in df.to_dict("records"):
        extra_fields = extra.get(record["id"], {})
        invoice_date = _safe_date(record.get("date_facture"), today)
        rows.append(
            InvoiceRow(
                id=record["id"],
                source_filename=extra_fields.get("source_filename", ""),
                code_facture=record.get("code_facture") or None,
                nom_fournisseur=record.get("nom_fournisseur") or None,
                numero_facture=record.get("numero_facture") or None,
                numero_client_fournisseur=record.get("numero_client_fournisseur") or None,
                numero_tahiti_siret=record.get("numero_tahiti_siret") or None,
                date_facture=invoice_date,
                date_echeance=_safe_date(record.get("date_echeance"), invoice_date),
                designation=record.get("designation") or "à vérifier manuellement",
                montant_ht=_safe_int(record.get("montant_ht")),
                taux_tva=_safe_int(record.get("taux_tva")),
                montant_tva=_safe_int(record.get("montant_tva")),
                departement=record.get("departement") or None,
                amortissement_note=extra_fields.get("amortissement_note"),
                extraction_status=extra_fields.get("extraction_status", "ok"),
                extraction_error_message=extra_fields.get("extraction_error_message"),
                extraction_technical_detail=extra_fields.get("extraction_technical_detail"),
                preview_bytes=extra_fields.get("preview_bytes"),
                preview_media_type=extra_fields.get("preview_media_type"),
            )
        )
    return rows
