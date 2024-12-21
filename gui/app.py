from PySide6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor
import asyncio
from network.checker import ping
from network.logger import setup_node_logging

class NetworkMonitorApp(QMainWindow):
    def __init__(self, nodes: list[str]):
        super().__init__()
        self.setWindowTitle("Network Monitor")
        self.nodes = nodes
        self.node_status = {node: ("Checking...", "-") for node in nodes}
        self.node_loggers = {node: setup_node_logging(node) for node in nodes}

        # Set up the table widget
        self.table_widget = QTableWidget(len(nodes), 3)
        self.table_widget.setHorizontalHeaderLabels(["Node", "Status", "Last Checked"])

        # Initialize the table
        for row, node in enumerate(nodes):
            self.table_widget.setItem(row, 0, QTableWidgetItem(node))
            self.table_widget.setItem(row, 1, QTableWidgetItem("Checking..."))
            self.table_widget.setItem(row, 2, QTableWidgetItem("-"))

        # Set up the layout with margins
        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Set up a timer to update the dashboard
        self.timer = QTimer()
        self.timer.timeout.connect(self.schedule_update_dashboard)
        self.timer.start(5000)  # Update every 5 seconds

    def schedule_update_dashboard(self):
        """Schedule the update_dashboard coroutine."""
        asyncio.create_task(self.update_dashboard())

    async def update_dashboard(self):
        for row, node in enumerate(self.nodes):
            status = await ping(node)
            status_text = "Online" if status else "Offline"
            timestamp = time.strftime("%H:%M:%S")
            self.node_status[node] = (status_text, timestamp)

            # Log status to node-specific log
            node_logger = self.node_loggers[node]
            node_logger.info(f"Node {node} is {status_text}")

            # Update the table widget with color coding
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QColor("green") if status else QColor("red"))

            self.table_widget.setItem(row, 1, status_item)
            self.table_widget.setItem(row, 2, QTableWidgetItem(timestamp)) 