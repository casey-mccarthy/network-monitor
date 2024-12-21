import networkx as nx
import matplotlib.pyplot as plt
import PIL
from network.node import NodeData

def draw_network_topology(nodes: list[NodeData]):
    """Draw a network topology using networkx and matplotlib.

    Args:
        nodes (list[NodeData]): List of nodes to include in the topology.
    """
    icons = {
        "router": "icons/router_black_144x144.png",
        "switch": "icons/switch_black_144x144.png",
        "PC": "icons/computer_black_144x144.png",
    }

    # Load images
    images = {k: PIL.Image.open(fname) for k, fname in icons.items()}

    # Generate the computer network graph
    G = nx.Graph()

    # Add nodes with images
    for node in nodes:
        G.add_node(node.ip, image=images.get(node.device_type, images["PC"]))

    # Add connections
    for node in nodes:
        for connected_node in node.connections:
            G.add_edge(node.ip, connected_node.ip)

    # Get a reproducible layout and create figure
    pos = nx.spring_layout(G, seed=1734289230)
    fig, ax = plt.subplots()

    # Draw edges
    nx.draw_networkx_edges(
        G,
        pos=pos,
        ax=ax,
        arrows=True,
        arrowstyle="-",
        min_source_margin=15,
        min_target_margin=15,
    )

    # Remove axes
    ax.set_axis_off()

    tr_figure = ax.transData.transform
    tr_axes = fig.transFigure.inverted().transform

    icon_size = (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.1
    icon_center = icon_size / 2.0

    for n in G.nodes:
        xf, yf = tr_figure(pos[n])
        xa, ya = tr_axes((xf, yf))
        a = plt.axes([xa - icon_center, ya - icon_center, icon_size, icon_size])
        a.imshow(G.nodes[n]["image"])
        a.axis("off")

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Adjust to fill the figure
    plt.show() 