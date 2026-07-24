"""Traduction des erreurs techniques en messages français compréhensibles."""
import anthropic


def friendly_error_message(exc: Exception) -> str:
    if isinstance(exc, anthropic.AuthenticationError):
        return "Votre clé API semble invalide ou expirée. Allez dans « Modifier la clé API » pour la corriger."
    if isinstance(exc, anthropic.PermissionDeniedError):
        return "Votre compte Anthropic n'a pas l'autorisation d'utiliser ce service. Vérifiez votre compte sur console.anthropic.com."
    if isinstance(exc, anthropic.RateLimitError):
        return "Le service d'analyse est temporairement surchargé (trop de factures envoyées d'un coup). Réessayez, ou réduisez le nombre de factures traitées en même temps."
    if isinstance(exc, anthropic.APIConnectionError):
        return "Impossible de contacter le service d'analyse. Vérifiez votre connexion internet et réessayez."
    if isinstance(exc, anthropic.BadRequestError):
        return "Ce fichier n'a pas pu être envoyé pour analyse (format ou taille non pris en charge)."
    if isinstance(exc, anthropic.APIStatusError):
        return "Le service d'analyse a rencontré un problème temporaire. Réessayez dans quelques instants."
    return "Cette facture n'a pas pu être analysée automatiquement. Vous pouvez remplir ses informations manuellement ci-dessous."


def technical_detail(exc: Exception) -> str:
    """Détail technique brut, à afficher dans une section repliable pour le diagnostic."""
    detail = str(exc).strip()
    label = f"{type(exc).__name__}"
    return f"{label}: {detail}" if detail else label
