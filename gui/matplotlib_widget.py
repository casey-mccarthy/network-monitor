from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal, QEvent
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import networkx as nx
import PIL
from network.checker import read_node_file
import matplotlib.pyplot as plt
from network.node import NodeData
import logging

# Initialize a logger for this module
logger = logging.getLogger(__name__)

class DynamicNetworkMap(QWidget):
    update_map_signal = Signal()

    def __init__(self, nodes: list[NodeData], file_path: str, parent=None):
        super().__init__(parent)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.file_path = file_path
        self.nodes = nodes  # Store the nodes list as an instance attribute

        # Connect the signal to the draw method
        self.update_map_signal.connect(self.draw_dynamic_map)

        self.draw_dynamic_map()

    def resizeEvent(self, event: QEvent):
        """Handle the resize event to clear and redraw the map."""
        self.figure.clear()  # Clear the figure to remove artifacts
        self.draw_dynamic_map()  # Redraw the map
        super().resizeEvent(event)  # Call the base class implementation

    def draw_dynamic_map(self):

        G = nx.Graph()

        for node in self.nodes:
            device_type = node.device_type.lower()
            G.add_node(node.ip, device_type=device_type, is_online=node.is_online)
            logger.debug(f"Node {node.ip} is {'online' if node.is_online else 'offline'} in draw")

        for node in self.nodes:
            for connected_node in node.connections:
                G.add_edge(node.ip, connected_node.ip)

        pos = nx.spring_layout(G, seed=1734289230)
        ax = self.figure.add_subplot(111)
        ax.set_axis_off()

        nx.draw_networkx_edges(
            G,
            pos=pos,
            ax=ax,
            arrows=True,
            arrowstyle="-",
            min_source_margin=15,
            min_target_margin=15,
        )

        for n in G.nodes:
            x, y = pos[n]
            device_type = G.nodes[n]["device_type"]
            is_online = G.nodes[n]["is_online"]

            # Determine box color based on online status
            box_color = "lightgreen" if is_online else "lightcoral"
            logger.debug(f"Drawing node {n} with color {box_color}")

            # Add the IP address inside the box
            text = ax.text(
                x, y, n, fontsize=6, ha='center', va='center', transform=ax.transData
            )

            # Get the bounding box of the text
            renderer = self.figure.canvas.get_renderer()
            bbox = text.get_window_extent(renderer=renderer)

            # Convert bbox to data coordinates
            bbox_data = bbox.transformed(ax.transData.inverted())

            # Calculate the rectangle with padding
            padding = 0.05  # Adjust padding as needed
            rect = plt.Rectangle(
                (bbox_data.x0 - padding, bbox_data.y0 - padding),
                bbox_data.width + 2 * padding,
                bbox_data.height + 2 * padding,
                color=box_color,
                transform=ax.transData,
                zorder=text.get_zorder() - 1  # Ensure the rectangle is below the text
            )
            ax.add_patch(rect)

            # Add a glow effect
            glow_color = "green" if is_online else "red"
            glow_rect = plt.Rectangle(
                (bbox_data.x0 - padding - 0.005, bbox_data.y0 - padding - 0.005),
                bbox_data.width + 2 * (padding + 0.005),
                bbox_data.height + 2 * (padding + 0.005),
                color=glow_color,
                alpha=0.3,
                transform=ax.transData,
                zorder=rect.get_zorder() - 1  # Ensure the glow is below the rectangle
            )
            ax.add_patch(glow_rect)

        self.canvas.draw()