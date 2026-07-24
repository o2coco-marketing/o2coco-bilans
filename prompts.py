"""Prompt d'extraction et schéma de l'outil utilisé pour forcer une réponse structurée."""
from config import DESIGNATIONS

TOOL_NAME = "extract_invoice_data"

# Toutes les propriétés sont "required" avec une valeur "vide" par défaut (chaîne vide / 0) plutôt
# que des types nullable : plus robuste et mieux supporté par les schémas de tool use.
INVOICE_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "est_facture_lisible": {
            "type": "boolean",
            "description": "false si l'image/le document n'est pas une facture, ou est trop flou/illisible pour être analysé.",
        },
        "code_facture": {
            "type": "string",
            "description": (
                "Numéro de repérage interne écrit À LA MAIN et entouré/encerclé par le personnel du "
                "restaurant, dans un des quatre coins de la facture (haut-gauche, haut-droite, "
                "bas-gauche ou bas-droite) — un simple chiffre repère, PAS le numéro de facture "
                "officiel imprimé par le fournisseur. Ne pas confondre les deux. Chaîne vide \"\" si "
                "aucun chiffre entouré à la main n'est visible sur le document."
            ),
        },
        "nom_fournisseur": {
            "type": "string",
            "description": (
                "Nom / raison sociale de l'entreprise fournisseur telle qu'imprimée sur la facture "
                "(ex: 'AUCHAN', 'Carrefour Tahiti', 'STGDN'...). Chaîne vide \"\" uniquement si le nom "
                "n'est vraiment pas identifiable sur le document — ne jamais inventer un nom."
            ),
        },
        "numero_facture": {
            "type": "string",
            "description": "Numéro de la facture tel qu'imprimé sur le document. Chaîne vide \"\" si absent du document — ne jamais inventer.",
        },
        "numero_client_fournisseur": {
            "type": "string",
            "description": "Numéro de compte CLIENT attribué par ce fournisseur (identifiant client) — PAS le numéro Tahiti/SIRET du fournisseur lui-même. Chaîne vide \"\" si absent.",
        },
        "numero_tahiti_siret": {
            "type": "string",
            "description": "Numéro d'identification du FOURNISSEUR : numéro Tahiti (TIN) ou numéro SIRET, l'un des deux selon ce qui est indiqué sur la facture. Chaîne vide \"\" si aucun des deux n'est visible.",
        },
        "date_facture": {
            "type": "string",
            "description": "Date d'émission de la facture, au format AAAA-MM-JJ.",
        },
        "date_echeance": {
            "type": "string",
            "description": "Date d'échéance/de paiement telle qu'imprimée sur la facture, au format AAAA-MM-JJ. Chaîne vide \"\" si elle n'est pas indiquée sur le document — ne jamais la calculer ou l'inventer, ce calcul est fait ailleurs.",
        },
        "designation": {
            "type": "string",
            "enum": DESIGNATIONS,
            "description": (
                "Catégorie de la dépense pour un restaurant. "
                "'alimentaire' = denrées, boissons, produits frais ou d'épicerie. "
                "'service' = prestation immatérielle ponctuelle (concert/animation, community management, "
                "freelance, prestation de nettoyage, honoraires...). "
                "'technologie' = catégorie par défaut pour tout achat matériel identifiable qui n'est ni "
                "alimentaire ni service (équipement, mobilier, matériel de cuisine, informatique, logiciel...). "
                "'à vérifier manuellement' = uniquement si le contenu de la facture ne permet vraiment pas de "
                "déterminer la catégorie — ne jamais deviner au hasard."
            ),
        },
        "montant_net_ht": {
            "type": "integer",
            "description": "Montant net hors taxes de la facture, en francs Pacifique (XPF), nombre entier (le XPF n'a pas de décimales).",
        },
        "taux_tva_pourcent": {
            "type": "integer",
            "description": "Taux de TVA en pourcentage entier (ex: 13 pour 13%). Mettre 0 si aucun taux de TVA n'est indiqué sur la facture.",
        },
        "montant_tva": {
            "type": "integer",
            "description": "Montant de la TVA en francs Pacifique (XPF), nombre entier. Mettre 0 si aucune TVA n'est indiquée sur la facture.",
        },
    },
    "required": [
        "est_facture_lisible",
        "code_facture",
        "nom_fournisseur",
        "numero_facture",
        "numero_client_fournisseur",
        "numero_tahiti_siret",
        "date_facture",
        "date_echeance",
        "designation",
        "montant_net_ht",
        "taux_tva_pourcent",
        "montant_tva",
    ],
}

SYSTEM_PROMPT = (
    "Tu es un assistant comptable qui lit des factures fournisseurs pour un restaurant de "
    "Polynésie française (devise : francs Pacifique, XPF, sans décimales). Tu extrais "
    "uniquement les informations réellement visibles sur le document fourni, en appelant "
    "l'outil demandé. Tu n'inventes jamais une valeur absente : dans ce cas tu utilises la "
    "valeur vide par défaut
