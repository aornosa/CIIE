# Developer Manual: Dialog System
The dialog system provides a flexible way to create conversations with NPCs, cutscenes, and scripted events. It consists of `DialogNode`, `DialogTree`, and `DialogManager` classes that work together to manage interactive conversations.

## Core Components

### DialogNode
Represents a single piece of dialog with speaker, text, and optional branching.

**Attributes:**
- `speaker`: Name of the character speaking
- `text`: Dialog text content
- `options`: List of tuples `[(text, next_node_id), ...]` for player choices
- `next_node`: ID of next node (if no options)
- `on_complete`: Callback function executed when node finishes

### DialogTree
Container for multiple nodes that form a complete conversation.

**Attributes:**
- `start_node_id`: ID of the first node
- `nodes`: Dictionary of `{node_id: DialogNode}`
- `current_node_id`: Tracks current position in tree

### DialogManager (Singleton)
Global manager that handles active dialogs and input. Already instantiated in `game.py`.

**Methods:**
- `start_dialog(dialog_tree)`: Begin a dialog
- `end_dialog()`: Close current dialog
- `is_dialog_active`: Check if dialog is open

## Creating Dialogs

### Simple Linear Dialog
```python
from dialogs.dialog_data import DialogNode, DialogTree

def create_greeting_dialog():
    nodes = {
        "start": DialogNode(
            speaker="Merchant",
            text="Welcome to my shop!",
            next_node="end"
        ),
        "end": DialogNode(
            speaker="Merchant",
            text="Come back soon!",
            next_node=None
        )
    }
    return DialogTree("start", nodes)
```

### Dialog with Choices
```python
def create_quest_dialog():
    nodes = {
        "quest": DialogNode(
            speaker="Guard",
            text="Can you help us?",
            options=[
                ("Yes, I'll help", "accept"),
                ("Not interested", "decline")
            ]
        ),
        "accept": DialogNode(
            speaker="Guard",
            text="Thank you, hero!",
            next_node=None
        ),
        "decline": DialogNode(
            speaker="Guard",
            text="I understand...",
            next_node=None
        )
    }
    return DialogTree("quest", nodes)
```

### Dialog with Callbacks
```python
def create_item_dialog():
    def give_item():
        player.inventory.add_item("Health Potion")
    
    nodes = {
        "gift": DialogNode(
            speaker="Healer",
            text="Take this potion.",
            next_node=None,
            on_complete=give_item  # Executes when node ends
        )
    }
    return DialogTree("gift", nodes)
```

## Using Dialogs

### NPC Dialog
```python
# In game.py or similar
from dialogs.test_dialogs import create_greeting_dialog

npc_merchant = NPC(
    name="Merchant",
    position=(300, 200),
    dialog_tree=create_greeting_dialog()
)
```

### Scripted Event Dialog
```python
# Trigger dialog without NPC
from dialogs.dialog_manager import DialogManager

dialog_manager = DialogManager()

# On game event
if player_entered_zone:
    dialog_manager.start_dialog(create_cutscene_dialog())
```


## Controls
- `E` or `Enter`: Advance dialog / Select option
- `W/Up` or `S/Down`: Navigate options (when available)

## File Structure
```
dialogs/
├── dialog_data.py      # DialogNode & DialogTree classes
├── dialog_manager.py   # DialogManager singleton
└── test_dialogs.py     # Example dialogs

ui/
└── dialog.py           # Rendering & UI layout
```
