from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import networkx as nx
import PIL
from network.checker import read_node_file
import matplotlib.pyplot as plt

class DynamicNetworkMap(QWidget):
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        
        # Add the navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)  # Add the toolbar to the layout
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.file_path = file_path
        self.draw_dynamic_map()

    def draw_dynamic_map(self):
        # Define colors for each device type
        colors = {
            "router": "red",
            "switch": "blue",
            "pc": "green",
        }

        nodes = read_node_file(self.file_path)
        G = nx.Graph()

        for node in nodes:
            device_type = node.device_type.lower()
            G.add_node(node.ip, device_type=device_type)

        for node in nodes:
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
            color = colors.get(device_type, "gray")

            # Determine online status (for demonstration, assume all are online)
            is_online = True  # Replace with actual status check

            # Draw a rectangle (box) for each node
            rect = plt.Rectangle(
                (x - 0.05, y - 0.05), 0.1, 0.1, color=color, transform=ax.transData
            )
            ax.add_patch(rect)

            # Add a glow effect
            glow_color = "green" if is_online else "red"
            glow_rect = plt.Rectangle(
                (x - 0.055, y - 0.055), 0.11, 0.11, color=glow_color, alpha=0.3, transform=ax.transData
            )
            ax.add_patch(glow_rect)

            # Add the IP address inside the box
            ax.text(
                x, y, n, fontsize=6, ha='center', va='center', transform=ax.transData
            )

        self.canvas.draw()