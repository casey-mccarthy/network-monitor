from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import networkx as nx
import PIL

class StaticNetworkMap(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.draw_static_map()

    def draw_static_map(self):
        icons = {
            "router": "icons/router_black_144x144.png",
            "switch": "icons/switch_black_144x144.png",
            "PC": "icons/computer_black_144x144.png",
        }

        images = {k: PIL.Image.open(fname) for k, fname in icons.items()}

        G = nx.Graph()

        G.add_node("router", image=images["router"])
        for i in range(1, 4):
            G.add_node(f"switch_{i}", image=images["switch"])
            for j in range(1, 4):
                G.add_node("PC_" + str(i) + "_" + str(j), image=images["PC"])

        G.add_edge("router", "switch_1")
        G.add_edge("router", "switch_2")
        G.add_edge("router", "switch_3")
        for u in range(1, 4):
            for v in range(1, 4):
                G.add_edge("switch_" + str(u), "PC_" + str(u) + "_" + str(v))

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

        tr_figure = ax.transData.transform
        tr_axes = self.figure.transFigure.inverted().transform

        icon_size = (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.025
        icon_center = icon_size / 2.0

        for n in G.nodes:
            xf, yf = tr_figure(pos[n])
            xa, ya = tr_axes((xf, yf))
            a = self.figure.add_axes([xa - icon_center, ya - icon_center, icon_size, icon_size])
            a.imshow(G.nodes[n]["image"])
            a.axis("off")

        self.canvas.draw() 