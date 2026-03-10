"""
Árboles de diálogo para AUDReS-01 (Audrey).
"""
from dialogs.dialog_data import DialogNode, DialogTree

_P = "assets/characters/audres/"


def create_audres_intro():
    """Diálogo de introducción — se lanza automáticamente al entrar al nivel."""
    nodes = {
        "intro_1": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_neutral.jpg",
            text="... Sistema en línea. Calibración completada. ¡Hola! Soy AUDReS-01, tu Unidad Autónoma de Distribución y Reabastecimiento.",
            next_node="intro_2",
        ),
        "intro_2": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_happy.jpg",
            text="Puedes llamarme Audrey. He sido asignada para acompañarte en esta misión. No te preocupes, ¡aquí estaré!",
            next_node="intro_3",
        ),
        "intro_3": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_alert.jpg",
            text="He detectado presencia hostil en el perímetro. Hostiles clasificados como infectados de nivel bajo. Ten cuidado y... intenta no recibir demasiados golpes. Para eso tengo yo los nervios.",
            next_node=None,
        ),
    }
    return DialogTree("intro_1", nodes)


def create_audres_idle():
    """Diálogo de espera — se activa al interactuar con Audrey después del intro."""
    nodes = {
        "idle_root": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_neutral.jpg",
            text="¿Necesitas algo?",
            options=[
                ("¿Cómo estás, Audrey?",   "idle_howru"),
                ("Nada, gracias.",          None),
            ],
        ),
        "idle_howru": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_happy.jpg",
            text="¡Funcionando al 97.3%! El 2.7% restante son preocupaciones por ti. Sigue así y ese número podría subir.",
            next_node=None,
        ),
    }
    return DialogTree("idle_root", nodes)
