"""Écran de configuration de la clé API Anthropic (premier lancement ou modification)."""
import streamlit as st

import config
from claude_client import check_api_key
from errors import friendly_error_message


def render() -> None:
    st.title("Configuration — Clé API")
    st.write(
        "Cette application utilise le service d'intelligence artificielle Claude (Anthropic) "
        "pour lire vos factures automatiquement. Vous devez créer une clé API personnelle "
        "avant de pouvoir commencer."
    )

    with st.expander("Comment créer ma clé API ?", expanded=True):
        st.markdown(
            "1. Allez sur [console.anthropic.com](https://console.anthropic.com) et créez un compte.\n"
            "2. Ajoutez un moyen de paiement — l'utilisation est facturée à la facture analysée "
            "(quelques centimes chacune environ), il n'y a pas d'abonnement.\n"
            "3. Dans le menu **API Keys**, cliquez sur **Create Key**.\n"
            "4. Copiez la clé générée (elle commence par `sk-ant-`)."
        )

    st.info(
        "📌 **Vous utilisez la version en ligne (Streamlit Community Cloud) ?** "
        "N'entrez pas votre clé ci-dessous — elle ne serait pas conservée après un "
        "redémarrage du serveur. Ajoutez-la plutôt dans les réglages de votre application sur "
        "share.streamlit.io (menu **⋮ → Settings → Secrets**), voir le README pour le détail. "
        "Une fois la clé ajoutée là-bas, revenez simplement sur cette page et actualisez-la."
    )

    st.caption("La solution ci-dessous ne fonctionne que pour un usage local, sur votre ordinateur.")
    api_key = st.text_input("Clé API Anthropic", type="password", placeholder="sk-ant-...")

    if st.button("Enregistrer et vérifier", type="primary", disabled=not api_key):
        with st.spinner("Vérification de la clé en cours..."):
            try:
                check_api_key(api_key)
            except Exception as exc:
                st.error(friendly_error_message(exc))
            else:
                try:
                    config.save_api_key(api_key)
                except OSError:
                    st.warning(
                        "La clé est valide, mais n'a pas pu être enregistrée sur ce serveur "
                        "(normal en hébergement en ligne). Utilisez plutôt les Secrets de "
                        "Streamlit Cloud comme indiqué ci-dessus."
                    )
                else:
                    st.session_state["step"] = "home"
                    st.success("Clé enregistrée avec succès !")
                    st.rerun()
