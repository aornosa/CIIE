from dialogs.dialog_data import DialogNode, DialogTree

_P = "assets/characters/audres/"

def create_audres_intro():
    """Diálogo de presentación """
    nodes = {
        "s1": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_neutral.jpg",
            text="Hola, soldado. Soy AUDReS-01, el robot de abastecimiento militar autónomo.",
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
            text="Muévete con WASD, dispara con clic izquierdo y recarga con R.",
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



def create_audres_shop_hint():
    """Diálogo post-oleada."""
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
    """Diálogo post-oleada 2"""
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
    """Diálogo provisional al entrar en la sala norte"""
    nodes = {
        "n1": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_happy.jpg",
            text="Creo que más adelante hay un helipuerto con una unidad operativa, podemos tomar un atajo por lo aires",
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

def create_audres_exit_door():
    """Diálogo al abrir la puerta de salida"""
    nodes = {
        "exit1": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_happy.jpg",
            text="Allí se encuentra el helicóptero, deberia tener suficiente combustible",
            next_node="exit2",
        ),
        "exit2": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_neutral.jpg",
            text="Corre hacia él y pulsa E para subir. Ha sido un placer luchar a tu lado.",
            next_node="exit3",
        ),
        "exit3": DialogNode(
            speaker="AUDReS-01",
            portrait=_P + "portrait_happy.jpg",
            text="Y no te preocupes por mí, me engancharé en el tren de aterrizaje.",
            next_node=None,
        ),
    }
    return DialogTree("exit1", nodes)