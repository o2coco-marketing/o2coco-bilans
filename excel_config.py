"""Mapping colonnes -> champs pour l'export Excel.

Isolé du code de génération pour pouvoir facilement adapter la mise en page si un format
d'import précis de Pacific Promotion (COMPTA20) est obtenu plus tard : il suffira de modifier
cette liste (ordre, en-têtes, colonnes) sans toucher à excel_export.py.
"""

COLUMNS = [
    {"header": "Nom fournisseur", "field": "nom_fournisseur", "width": 22, "format": "text"},
    {"header": "N° facture", "field": "numero_facture", "width": 16, "format": "text"},
    {"header": "N° client fournisseur", "field": "numero_client_fournisseur", "width": 20, "format": "text"},
    {"header": "N° Tahiti / SIRET", "field": "numero_tahiti_siret", "width": 18, "format": "text"},
    {"header": "Date facture", "field": "date_facture", "width": 14, "format": "date"},
    {"header": "Date d'échéance", "field": "date_echeance", "width": 14, "format": "date"},
    {"header": "Désignation", "field": "designation", "width": 20, "format": "text"},
    {"header": "Service du restaurant", "field": "departement", "width": 18, "format": "text"},
    {"header": "Montant net (HT)", "field": "montant_ht", "width": 16, "format": "amount", "totals": True},
    {"header": "Taux TVA (%)", "field": "taux_tva", "width": 12, "format": "percent_int"},
    {"header": "Montant TVA", "field": "montant_tva", "width": 16, "format": "amount", "totals": True},
    {"header": "Amortissement (à vérifier)", "field": "amortissement_note", "width": 26, "format": "text"},
    {"header": "Fichier source", "field": "source_filename", "width": 24, "format": "text"},
]
