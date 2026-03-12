"""
Árboles de diálogo para AUDReS-01 (Audrey).
"""
from dialogs.dialog_data import DialogNode, DialogTree

_P = "assets/characters/audres/"


def create_audres_intro():
    """Diálogo de presentación — se activa cuando Audrey llega al jugador."""
    nodes = {
        "s1": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_neutral.jpg",
            text="Tuviste suerte de que te haya encontrado, soldado. Soy AUDReS-01, el robot de abastecimiento militar autónomo.",
            next_node="s2",
        ),
        "s2": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_alert.jpg",
            text="Espera un momento... creo que escucho ruidos. Son ZOMBIES. Hay infectados aproximándose al perímetro.",
            next_node="s3",
        ),
        "s3": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_happy.jpg",
            text="Por suerte resulta que soy un instructor de aniquilamiento de zombies de primer nivel.",
            next_node="s4",
        ),
        "s4": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_happy.jpg",
            text="Muévete con WASD, apunta manteniendo el click derecho del ratón, dispara con clic izquierdo y recarga con R.",
            next_node="s5",
        ),
        "s5": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_alert.jpg",
            text="Dicho esto... la verdad es que los zombies me dan bastante miedo.",
            next_node="s6",
        ),
         "s6": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_alert.jpg",
            text="Voy a quedarme sobrevolando desde las alturas vigilándote. ¡Buena suerte, soldado!",
            next_node=None,
        ),
    }
    return DialogTree("s1", nodes)


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


def create_audres_shop_hint():
    """Diálogo post-oleada — explica la tienda y pista sobre el Doc."""
    nodes = {
        "shop1": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_happy.jpg",
            text="¡Bien hecho, soldado! Has eliminado la primera oleada de infectados.",
            next_node="shop2",
        ),
        "shop2": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_neutral.jpg",
            text="Tengo suministros disponibles para ti. Pulsa P en cualquier momento para abrir la tienda y comprar mejoras antes de que llegue la siguiente oleada. ¡Úsala bien!",
            next_node="doc1",
        ),
        "doc1": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_neutral.jpg",
            text="Oye... mientras tengo tu atención. Mis sensores han detectado señales de vida en el laboratorio al norte.",
            next_node="doc2",
        ),
        "doc2": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_alert.jpg",
            text="Creo que podría ser el Doc. Si alguien sabe algo sobre una cura para esta infección, es él. Lleva años investigando el virus.",
            next_node="doc3",
        ),
        "doc3": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_happy.jpg",
            text="En cuanto acabes con los infectados que quedan en la zona, te mostraré el camino. No te preocupes, no te perderé de vista.",
            next_node=None,
        ),
    }
    return DialogTree("shop1", nodes)


def create_audres_wave2_clear():
    """Diálogo post-oleada 2 — Audrey felicita al jugador y lo guía al laboratorio."""
    nodes = {
        "w2_1": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_happy.jpg",
            text="¡Increíble, soldado! Has eliminado a todos los infectados de la zona. Eres mucho mejor de lo que esperaba.",
            next_node="w2_2",
        ),
        "w2_2": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_happy.jpg",
            text="El laboratorio al norte sigue en pie. Si el Doc sigue ahí dentro, podrá darnos respuestas.",
            next_node="w2_3",
        ),
        "w2_3": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_neutral.jpg",
            text="Vamos al laboratorio, sígueme.",
            next_node=None,
        ),
    }
    return DialogTree("w2_1", nodes)


def create_audres_north_room_entry():
    """Diálogo provisional al entrar en la sala norte — puerta se cierra tras esto."""
    nodes = {
        "n1": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_happy.jpg",
            text="si no recuerdo mal el laboratorio debería estar por aquí",
            next_node="n2",
        ),
        "n2": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_alert.jpg",
            text="ALERTA, detecto mas infectados acercandose, encárgate de ellos",
            next_node=None,
        ),
    }
    return DialogTree("n1", nodes)
