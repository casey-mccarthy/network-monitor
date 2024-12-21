class Node:
    def __init__(self, ip: str, device_type: str = "PC"):
        self.ip = ip
        self.device_type = device_type
        self.connections = set()

    def connect(self, other_node: 'Node'):
        """Connect this node to another node."""
        self.connections.add(other_node)
        other_node.connections.add(self)

    def disconnect(self, other_node: 'Node'):
        """Disconnect this node from another node."""
        self.connections.discard(other_node)
        other_node.connections.discard(self) 