# O2 Coco — Bilans mensuels

Application pour automatiser la saisie des factures fournisseurs d'O2 Coco, en vue des bilans
mensuels destinés à l'expert-comptable.

**Usage recommandé : en ligne, via Streamlit Community Cloud** (voir plus bas). Vous ouvrez un
simple lien dans votre navigateur, depuis n'importe quel ordinateur ou téléphone, sans rien
installer. Le code peut aussi être lancé en local avec `lancer_application.bat` (nécessite Python)
si vous préférez.

## Ce que fait l'application

1. Vous importez toutes les photos/scans de factures d'un mois (entre 5 et 300 fichiers).
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
   ```
   ANTHROPIC_API_KEY = "sk-ant-votre-clé-ici"
   ```
4. Cliquez sur **Deploy**. Une adresse du type `https://o2coco-xxxx.streamlit.app` est générée —
   c'est le lien à garder et à ouvrir à chaque utilisation, depuis n'importe quel appareil.

**Ne collez jamais votre vraie clé API dans un fichier du dépôt GitHub** (y compris `.env`) : elle
doit uniquement être renseignée dans les Secrets de Streamlit Cloud, qui ne sont pas publics.

Limites du plan gratuit à connaître : l'application se met en veille après une période
d'inactivité (elle se réveille automatiquement à la prochaine visite, en quelques secondes), et les
ressources (mémoire/processeur) sont partagées. Pour un lot de 200-300 factures d'un coup, cela
peut être plus lent qu'en local ; en cas de lenteur, traitez le lot en plusieurs imports plus
petits.

## Installation locale (optionnelle, sur votre ordinateur)

1. Installez **Python** (version 3.10 ou plus récente) depuis
   [python.org/downloads](https://www.python.org/downloads/). Pendant l'installation, cochez bien
   la case **"Add python.exe to PATH"**.
2. Double-cliquez sur **`lancer_application.bat`**. Le premier démarrage prend quelques minutes
   (installation automatique des composants nécessaires) ; les démarrages suivants sont rapides.
3. Une page s'ouvre dans votre navigateur, vous demandant de créer et coller votre clé API
   personnelle Anthropic (les instructions sont affichées directement dans l'application).

## Utilisation

Double-cliquez simplement sur **`lancer_application.bat`** à chaque fois que vous voulez utiliser
l'application.

## Coût

L'application elle-même est gratuite (le plan gratuit de Streamlit Community Cloud aussi). Seul le
service d'IA (Anthropic) est payant, à l'usage, sans abonnement : environ **1 à 2 XPF par
facture** avec le modèle par défaut (`claude-sonnet-5`) — de quoi analyser des centaines de
factures pour quelques centaines de francs. Anthropic exige un crédit prépayé minimum d'environ
5 USD (~550 XPF) à l'ouverture du compte ; à ce rythme, ce crédit dure très longtemps.

Pour un résultat encore plus précis sur des factures difficiles à lire (à un coût plus élevé), vous
pouvez changer `ANTHROPIC_API_KEY`/`CLAUDE_MODEL` dans les Secrets Streamlit Cloud (ou le fichier
`.env` en local) en remplaçant `CLAUDE_MODEL=claude-sonnet-5` par `CLAUDE_MODEL=claude-opus-4-8`.

## Format d'export

Le bilan est généré au format Excel (`.xlsx`), avec une mise en forme professionnelle et une ligne
de totaux (montant HT total, TVA totale). Aucune spécification publique d'import n'a été trouvée
pour le logiciel comptable Pacific Promotion (COMPTA20) : ce format Excel est donc le point de
départ. Si vous obtenez un jour le format d'import exact auprès de Pacific Promotion ou de votre
expert-comptable, la mise en page de l'export peut être adaptée facilement (fichier
`excel_config.py`) sans reconstruire l'application.

## En cas de problème

- **"Python n'est pas installé"** : réinstallez Python en cochant bien "Add python.exe to PATH",
  puis relancez `lancer_application.bat`.
- **Message d'erreur sur la clé API** : vérifiez que vous avez bien copié l'intégralité de la clé
  depuis console.anthropic.com (elle commence par `sk-ant-`), et qu'un moyen de paiement est
  enregistré sur votre compte Anthropic.
- **Une facture n'a pas été lue correctement** : c'est normal pour une photo floue ou mal cadrée —
  corrigez simplement ses informations à la main dans le tableau de révision.
- **L'application ne s'ouvre pas dans le navigateur** : ouvrez manuellement l'adresse
  `http://localhost:8501` dans votre navigateur pendant que la fenêtre noire reste ouverte.
