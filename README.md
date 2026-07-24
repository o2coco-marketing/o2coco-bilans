# O2 Coco — Bilans mensuels

Application pour automatiser la saisie des factures fournisseurs d'O2 Coco, en vue des bilans
mensuels destinés à l'expert-comptable.

**Usage recommandé : en ligne, via Streamlit Community Cloud** (voir plus bas). Vous ouvrez un
simple lien dans votre navigateur, depuis n'importe quel ordinateur ou téléphone, sans rien
installer. Le code peut aussi être lancé en local avec `lancer_application.bat` (nécessite Python)
si vous préférez.

## Ce que fait l'application

1. Vous importez toutes les photos/scans de factures d'un mois (jusqu'à 500 fichiers).
2. L'application lit automatiquement chaque facture grâce à l'intelligence artificielle Claude
   (Anthropic) : numéro de facture, dates, montants, TVA, catégorie de dépense...
3. Vous vérifiez et corrigez les informations dans un tableau, et complétez les deux informations
   toujours manuelles : le service du restaurant concerné (Bar-Restaurant / Bar à vin /
   Boulangerie) et, pour le matériel/équipement, une note d'amortissement.
4. Vous générez un fichier Excel professionnel avec le récapitulatif complet et les totaux, prêt à
   être transmis à votre expert-comptable.

Aucune donnée n'est envoyée nulle part, à l'exception de l'image de chaque facture envoyée au
service d'IA Claude (Anthropic) le temps de l'analyse — c'est nécessaire pour la lecture
automatique.

## Déploiement en ligne (Streamlit Community Cloud) — recommandé

1. Mettez le code de ce dossier sur un dépôt GitHub (public ou privé).
2. Sur [share.streamlit.io](https://share.streamlit.io), cliquez sur **New app**, choisissez le
   dépôt, la branche et indiquez `app.py` comme fichier principal.
3. Avant de déployer, ouvrez **Advanced settings → Secrets** et collez :
