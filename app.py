"""Point d'entrée Streamlit : routeur d'étapes de l'assistant."""
import streamlit as st

import config
from screens import home, processing, review, setup, upload
from state import init_session_state

st.set_page_config(page_title=config.APP_TITLE, page_icon="🧾", layout="wide")


def main() -> None:
    init_session_state()

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
