"""Point d'entrée Streamlit : routeur d'étapes de l'assistant."""
import hmac

import streamlit as st

import config
from screens import home, processing, review, setup, upload
from state import init_session_state

st.set_page_config(page_title=config.APP_TITLE, page_icon="🥥", layout="wide")


def _check_password() -> bool:
    """Affiche un écran de mot de passe si APP_PASSWORD est configuré. Sinon, accès libre."""
    app_password = config.get_app_password()
    if not app_password:
        return True

    if st.session_state.get("authenticated"):
        return True

    st.title(config.APP_TITLE)
    st.write("Cette application est protégée. Entrez le mot de passe pour continuer.")
    entered = st.text_input("Mot de passe", type="password", key="password_input")
    if st.button("Entrer", type="primary"):
        if hmac.compare_digest(entered, app_password):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect.")
    return False


def main() -> None:
    init_session_state()

    if not _check_password():
        return

    if not config.get_api_key():
        setup.render()
        return

    step = st.session_state["step"]
    screens = {
        "setup": setup.render,
        "home": home.render,
        "upload": upload.render,
        "processing": processing.render,
        "review": review.render,
    }
    render_fn = screens.get(step)
    if render_fn is None:
        st.session_state["step"] = "home"
        st.rerun()
    else:
        render_fn()


if __name__ == "__main__":
    main()
