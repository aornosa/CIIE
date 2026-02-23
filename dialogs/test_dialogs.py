from dialogs.dialog_data import DialogNode, DialogTree


def create_blue_zone_intro_dialog():
    nodes = {
        "A": DialogNode(
            speaker="Jugador",
            text="¿Qué es ese ruido...?",
            next_node="B"
        ),
        "B": DialogNode(
            speaker="Jugador",
            text="¡Algo se está acercando!",
            next_node=None
        ),
    }
    return DialogTree("A", nodes)


def create_blue_zone_final_dialog():
    nodes = {
        "A": DialogNode(
            speaker="Jugador",
            text="Ha venido directo hacia mí. No puedo bajar la guardia.",
            next_node=None
        ),
    }
    return DialogTree("A", nodes)


def create_red_zone_dialog():
    nodes = {
        "A": DialogNode(
            speaker="Sistema",
            text="Esta es una prueba.",
            next_node="B"
        ),
        "B": DialogNode(
            speaker="Sistema",
            text="Has entrado en la zona roja y ahora ves una escena de prueba.",
            next_node=None
        ),
    }
    return DialogTree("A", nodes)


def create_test_dialog_simple():
    nodes = {
        "A": DialogNode(
            speaker="npc",
            text="Prueba de diálogo A",
            next_node="B"
        ),
        "B": DialogNode(
            speaker="npc",
            text="Prueba de diálogo B",
            next_node="C"
        ),
        "C": DialogNode(
            speaker="npc",
            text="Prueba de diálogo C",
            next_node=None
        ),
        
    }
    
    return DialogTree("A", nodes)
