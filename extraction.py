"""Orchestration du traitement d'un lot de factures : parallélisme et résilience aux erreurs."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from typing import Callable

import business_rules
from claude_client import extract_invoice_prepared, get_client, prepare_document
from config import DESIGNATIONS
from errors import friendly_error_message, technical_detail
from state import InvoiceRow

# Mapping des clés de schéma (côté IA) vers les noms de champs internes de l'application.
RAW_TO_INTERNAL_FIELD = {
    "code_facture": "code_facture",
    "nom_fournisseur": "nom_fournisseur",
    "numero_facture": "numero_facture",
    "numero_client_fournisseur": "numero_client_fournisseur",
    "numero_tahiti_siret": "numero_tahiti_siret",
    "date_facture": "date_facture",
    "date_echeance": "date_echeance",
    "designation": "designation",
    "montant_net_ht": "montant_ht",
    "taux_tva_pourcent": "taux_tva",
    "montant_tva": "montant_tva",
}


def _parse_date(value: str | None) -> date | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _row_from_raw(filename: str, raw: dict, preview_bytes: bytes, preview_media_type: str) -> InvoiceRow:
    date_facture = _parse_date(raw.get("date_facture")) or date.today()
    date_echeance = _parse_date(raw.get("date_echeance")) or business_rules.default_due_date(date_facture)

    designation = raw.get("designation") or "à vérifier manuellement"
    if designation not in DESIGNATIONS:
        designation = "à vérifier manuellement"

    status, error_message = "ok", None
    if not raw.get("est_facture_lisible", True):
        status = "error"
        error_message = (
            "Ce document n'a pas été reconnu comme une facture lisible. "
            "Vérifiez-le et complétez les champs manuellement."
        )

    raw_uncertain = raw.get("champs_incertains") or []
    uncertain_fields = [
        RAW_TO_INTERNAL_FIELD[key] for key in raw_uncertain if key in RAW_TO_INTERNAL_FIELD
    ]

    return InvoiceRow(
        source_filename=filename,
        code_facture=(raw.get("code_facture") or "").strip() or None,
        nom_fournisseur=(raw.get("nom_fournisseur") or "").strip() or None,
        numero_facture=(raw.get("numero_facture") or "").strip() or None,
        numero_client_fournisseur=(raw.get("numero_client_fournisseur") or "").strip() or None,
        numero_tahiti_siret=(raw.get("numero_tahiti_siret") or "").strip() or None,
        date_facture=date_facture,
        date_echeance=date_echeance,
        designation=designation,
        montant_ht=int(raw.get("montant_net_ht") or 0),
        taux_tva=business_rules.default_vat_rate(raw.get("taux_tva_pourcent")),
        montant_tva=int(raw.get("montant_tva") or 0),
        uncertain_fields=uncertain_fields,
        extraction_status=status,
        extraction_error_message=error_message,
        preview_bytes=preview_bytes,
        preview_media_type=preview_media_type,
    )


def _process_single(client, model: str, filename: str, file_bytes: bytes) -> InvoiceRow:
    """Ne lève jamais d'exception : toute erreur est capturée et renvoyée comme ligne en erreur."""
    try:
        data, media_type, block_type = prepare_document(file_bytes, filename)
    except Exception as exc:
        return InvoiceRow(
            source_filename=filename,
            date_facture=date.today(),
            date_echeance=business_rules.default_due_date(date.today()),
            extraction_status="error",
            extraction_error_message="Ce fichier n'a pas pu être ouvert (format d'image ou de PDF non reconnu).",
            extraction_technical_detail=technical_detail(exc),
        )

    try:
        raw = extract_invoice_prepared(client, model, data, media_type, block_type)
    except Exception as exc:
        return InvoiceRow(
            source_filename=filename,
            date_facture=date.today(),
            date_echeance=business_rules.default_due_date(date.today()),
            extraction_status="error",
            extraction_error_message=friendly_error_message(exc),
            extraction_technical_detail=technical_detail(exc),
            preview_bytes=data,
            preview_media_type=media_type,
        )

    return _row_from_raw(filename, raw, data, media_type)


def process_batch(
    file_items: list[tuple[str, bytes]],
    api_key: str,
    model: str,
    max_workers: int,
    on_progress: Callable[[int, int], None] | None = None,
) -> list[InvoiceRow]:
    """Analyse tous les fichiers en parallèle. Une facture en erreur n'interrompt jamais le lot."""
    client = get_client(api_key)
    total = len(file_items)
    results: list[InvoiceRow | None] = [None] * total
    completed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(_process_single, client, model, filename, data): index
            for index, (filename, data) in enumerate(file_items)
        }
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            results[index] = future.result()
            completed += 1
            if on_progress:
                on_progress(completed, total)

    return results  # type: ignore[return-value]
