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
    return designation == "technologie"


def is_row_complete(
    designation: str,
    departement: str | None,
    amortissement_note: str | None,
    nom_fournisseur: str | None = None,
) -> bool:
    if not departement:
        return False
    if not (nom_fournisseur and nom_fournisseur.strip()):
        return False
    if requires_amortissement(designation) and not (amortissement_note and amortissement_note.strip()):
        return False
    return True


RED_FLAG_LABELS = {
    "nom_fournisseur": "Nom fournisseur manquant",
    "departement": "Service du restaurant manquant",
    "amortissement_note": "Amortissement manquant",
    "montant_ht": "Montant HT non détecté",
    "designation": "Désignation à vérifier",
}


def compute_red_flags(
    designation: str,
    departement: str | None,
    amortissement_note: str | None,
    nom_fournisseur: str | None,
    montant_ht: int,
) -> list[str]:
    """Liste des champs obligatoires manquants ou visiblement non détectés pour cette facture."""
    flags = []
    if not (nom_fournisseur and nom_fournisseur.strip()):
        flags.append("nom_fournisseur")
    if not departement:
        flags.append("departement")
    if requires_amortissement(designation) and not (amortissement_note and amortissement_note.strip()):
        flags.append("amortissement_note")
    if montant_ht == 0:
        flags.append("montant_ht")
    if designation == "à vérifier manuellement":
        flags.append("designation")
    return flags


MONTH_NAMES_FR = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]


def format_month_label(year: int, month: int) -> str:
    return f"{MONTH_NAMES_FR[month - 1].capitalize()} {year}"


def format_month_key(year: int, month: int) -> str:
    return f"{year:04d}-{month:02d}"
