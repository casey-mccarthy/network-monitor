from dataclasses import dataclass, field
from typing import Set

@dataclass
class NodeData:
    """Data class representing a network node."""
    ip: str
    device_type: str = "PC"
    connections: Set['NodeData'] = field(default_factory=set)
    is_online: bool = False

    def __hash__(self):
        """Make NodeData hashable by using the IP address."""
        return hash(self.ip)

    def connect(self, other_node: 'NodeData'):
        """Connect this node to another node.

        Args:
            other_node (NodeData): The node to connect to.
        """
        self.connections.add(other_node)
        other_node.connections.add(self)

    def disconnect(self, other_node: 'NodeData'):
        """Disconnect this node from another node.

        Args:
            other_node (NodeData): The node to disconnect from.
        """
        self.connections.discard(other_node)
        other_node.connections.discard(self) 