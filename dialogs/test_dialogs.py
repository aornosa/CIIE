from dialogs.dialog_data import DialogNode, DialogTree

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
