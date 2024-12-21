import time
import asyncio
from PySide6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer
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
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(1000)  # Update every 1 second

    def start_node_tasks(self):
        """Start asynchronous tasks for each node."""
        self.node_tasks = [asyncio.create_task(self.check_node(node, row)) for row, node in enumerate(self.nodes)]

    async def check_node(self, node: str, row: int):
        """Check the status of a node and update the table."""
        while True:
            status = await ping(node)
            status_text = "Online" if status else "Offline"
            timestamp = time.strftime("%H:%M:%S")
            self.node_status[node] = (status_text, timestamp)

            # Log status to node-specific log
            node_logger = self.node_loggers[node]
            node_logger.info(f"Node {node} is {status_text}")

            # Update the table widget with color coding
            status_item = self.table_widget.item(row, 1)
            if not status_item:
                status_item = QTableWidgetItem()
                self.table_widget.setItem(row, 1, status_item)
            
            status_item.setText(status_text)
            status_item.setForeground(QColor("green") if status else QColor("red"))

            timestamp_item = self.table_widget.item(row, 2)
            if not timestamp_item:
                timestamp_item = QTableWidgetItem()
                self.table_widget.setItem(row, 2, timestamp_item)
            
            timestamp_item.setText(timestamp)

            await asyncio.sleep(5)  # Check every 5 seconds

    def update_dashboard(self):
        """Update the dashboard with the latest node statuses."""
        for row, node in enumerate(self.nodes):
            status_text, timestamp = self.node_status[node]
            
            # Update status text and color
            status_item = self.table_widget.item(row, 1)
            if not status_item:
                status_item = QTableWidgetItem()
                self.table_widget.setItem(row, 1, status_item)
            
            status_item.setText(status_text)
            status_item.setForeground(QColor("green") if status_text == "Online" else QColor("red"))

            # Update timestamp
            timestamp_item = self.table_widget.item(row, 2)
            if not timestamp_item:
                timestamp_item = QTableWidgetItem()
                self.table_widget.setItem(row, 2, timestamp_item)
            
            timestamp_item.setText(timestamp) 