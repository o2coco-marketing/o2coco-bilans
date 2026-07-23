"""Règles métier pures, indépendantes de l'IA et de l'interface."""
from __future__ import annotations

from calendar import monthrange
from datetime import date


def default_due_date(invoice_date: date) -> date:
    """Dernier jour du mois de la date de facture."""
    last_day = monthrange(invoice_date.year, invoice_date.month)[1]
    return date(invoice_date.year, invoice_date.month, last_day)


def default_vat_rate(vat_rate: int | None) -> int:
    return vat_rate if vat_rate is not None else 0


def requires_amortissement(designation: str) -> bool:
    return designation not in {"alimentaire", "service"}


def is_row_complete(designation: str, departement: str | None, amortissement_note: str | None) -> bool:
    if not departement:
        return False
    if requires_amortissement(designation) and not (amortissement_note and amortissement_note.strip()):
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
