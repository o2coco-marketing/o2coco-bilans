"""Règles métier pures, indépendantes de l'IA et de l'interface."""
from __future__ import annotations

from calendar import monthrange
from datetime import date

from config import MISSING_SELECT_MARKER, MISSING_TEXT_MARKER


def default_due_date(invoice_date: date) -> date:
    """Dernier jour du mois de la date de facture."""
    last_day = monthrange(invoice_date.year, invoice_date.month)[1]
    return date(invoice_date.year, invoice_date.month, last_day)


def default_vat_rate(vat_rate: int | None) -> int:
    return vat_rate if vat_rate is not None else 0


def requires_amortissement(designation: str) -> bool:
    return designation == "technologie"


def is_effectively_blank(value: str | None) -> bool:
    """Vrai si vide, ou si la case ne contient encore que le marqueur « à remplir »."""
    if not value:
        return True
    stripped = str(value).strip()
    return stripped in ("", MISSING_TEXT_MARKER, MISSING_SELECT_MARKER)


def is_row_complete(
    designation: str,
    departement: str | None,
    amortissement_note: str | None,
    nom_fournisseur: str | None = None,
) -> bool:
    if is_effectively_blank(departement):
        return False
    if is_effectively_blank(nom_fournisseur):
        return False
    if requires_amortissement(designation) and is_effectively_blank(amortissement_note):
        return False
    return True


MONTH_NAMES_FR = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]


def format_month_label(year: int, month: int) -> str:
    return f"{MONTH_NAMES_FR[month - 1].capitalize()} {year}"


def format_month_key(year: int, month: int) -> str:
    return f"{year:04d}-{month:02d}"
