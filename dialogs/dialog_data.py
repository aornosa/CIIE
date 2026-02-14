class DialogNode:
    def __init__(self, speaker, text, options=None, next_node=None, on_complete=None):
        self.speaker = speaker
        self.text = text
        self.options = options or []
        self.next_node = next_node
        self.on_complete = on_complete


class DialogTree:
    def __init__(self, start_node_id, nodes):
        self.start_node_id = start_node_id
        self.nodes = nodes
        self.current_node_id = start_node_id
    
    def get_current_node(self):
        return self.nodes.get(self.current_node_id)
    
    def advance_to_node(self, node_id):
        if node_id in self.nodes:
            self.current_node_id = node_id
            return True
        return False
    
    def reset(self):
        self.current_node_id = self.start_node_id
