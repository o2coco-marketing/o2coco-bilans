"""Client Anthropic : préparation des documents et appel d'extraction par facture."""
from __future__ import annotations

import base64
import io

import anthropic
import streamlit as st
from PIL import Image

from prompts import INVOICE_TOOL_SCHEMA, SYSTEM_PROMPT, TOOL_NAME, USER_PROMPT

MAX_IMAGE_DIMENSION = 1568  # recommandation Anthropic pour un traitement optimal
JPEG_QUALITY = 85
MAX_OUTPUT_TOKENS = 1024


@st.cache_resource(show_spinner=False)
def get_client(api_key: str) -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=api_key)


def prepare_document(file_bytes: bytes, filename: str) -> tuple[bytes, str, str]:
    """Retourne (données prêtes à envoyer, media_type, type_de_bloc) pour un fichier importé."""
    if filename.lower().endswith(".pdf"):
        return file_bytes, "application/pdf", "document"

    image = Image.open(io.BytesIO(file_bytes))
    image = image.convert("RGB")
    largest_side = max(image.size)
    if largest_side > MAX_IMAGE_DIMENSION:
        scale = MAX_IMAGE_DIMENSION / largest_side
        new_size = (round(image.width * scale), round(image.height * scale))
        image = image.resize(new_size, Image.LANCZOS)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return buffer.getvalue(), "image/jpeg", "image"


def extract_invoice_prepared(
    client: anthropic.Anthropic, model: str, data: bytes, media_type: str, block_type: str
) -> dict:
    """Analyse un document déjà préparé (voir prepare_document) et retourne les champs extraits.

    Lève une exception anthropic.* en cas d'échec — à gérer par l'appelant.
    """
    encoded = base64.b64encode(data).decode("ascii")

    message = client.messages.create(
        model=model,
        max_tokens=MAX_OUTPUT_TOKENS,
        system=SYSTEM_PROMPT,
        tools=[
            {
                "name": TOOL_NAME,
                "description": "Enregistre les informations extraites d'une facture fournisseur.",
                "input_schema": INVOICE_TOOL_SCHEMA,
            }
        ],
        tool_choice={"type": "tool", "name": TOOL_NAME},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": block_type,
                        "source": {"type": "base64", "media_type": media_type, "data": encoded},
                    },
                    {"type": "text", "text": USER_PROMPT},
                ],
            }
        ],
    )

    for block in message.content:
        if block.type == "tool_use" and block.name == TOOL_NAME:
            return block.input

    raise ValueError("Le modèle n'a pas retourné de résultat structuré exploitable.")


def check_api_key(api_key: str) -> None:
    """Lève une exception anthropic.* si la clé est invalide ou le service inaccessible."""
    client = anthropic.Anthropic(api_key=api_key)
    client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1,
        messages=[{"role": "user", "content": "ping"}],
    )
