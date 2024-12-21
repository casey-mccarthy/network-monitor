import time
import asyncio
from PySide6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QSplitter, QLabel, QFrame
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from network.checker import ping
from network.logger import setup_node_logging

class NetworkMonitorApp(QMainWindow):
    def __init__(self, nodes: list[str]):
        super().__init__()
        self.setWindowTitle("Network Monitor")
        self.nodes = nodes
        self.node_status = {node: ("Checking...", "-") for node in nodes}
        self.node_loggers = {node: setup_node_logging(node) for node in nodes}

        # Create the main splitter
        splitter = QSplitter(Qt.Horizontal)

        # Create the menu bar (left 1/3)
        menu_bar = QFrame()
        menu_bar.setFrameShape(QFrame.StyledPanel)
        menu_layout = QVBoxLayout()
        menu_bar.setLayout(menu_layout)
        splitter.addWidget(menu_bar)

        # Create the node status area (right 2/3)
        node_area = QWidget()
        node_layout = QVBoxLayout()
        node_area.setLayout(node_layout)
        splitter.addWidget(node_area)

        # Set the splitter sizes
        splitter.setSizes([1, 2])

        # Add node status widgets
        self.node_widgets = {}
        for node in nodes:
            node_widget = QWidget()
            node_layout = QVBoxLayout()
            node_name_label = QLabel(node)
            node_status_label = QLabel("Checking...")
            node_layout.addWidget(node_name_label)
            node_layout.addWidget(node_status_label)
            node_widget.setLayout(node_layout)
            node_area.layout().addWidget(node_widget)
            self.node_widgets[node] = node_status_label

        self.setCentralWidget(splitter)

        # Set up a timer to update the dashboard
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(1000)  # Update every 1 second

    def start_node_tasks(self):
        """Start asynchronous tasks for each node."""
        self.node_tasks = [asyncio.create_task(self.check_node(node)) for node in self.nodes]

    async def check_node(self, node: str):
        """Check the status of a node and update the table."""
        while True:
            status = await ping(node)
            status_text = "Online" if status else "Offline"
            timestamp = time.strftime("%H:%M:%S")
            self.node_status[node] = (status_text, timestamp)

            # Log status to node-specific log
            node_logger = self.node_loggers[node]
            node_logger.info(f"Node {node} is {status_text}")

            await asyncio.sleep(5)  # Check every 5 seconds

    def update_dashboard(self):
        """Update the dashboard with the latest node statuses."""
        for node, (status_text, timestamp) in self.node_status.items():
            node_status_label = self.node_widgets[node]
            node_status_label.setText(f"{status_text} - Last checked: {timestamp}")
            node_status_label.setStyleSheet(f"color: {'green' if status_text == 'Online' else 'red'};") 