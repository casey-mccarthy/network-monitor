import time
import asyncio
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QSplitter, QLabel, QFrame, QPushButton, QTableWidget, QTableWidgetItem, QStackedWidget, QListWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from network.checker import ping
from network.logger import setup_node_logging

class NetworkMonitorApp(QMainWindow):
    def __init__(self, nodes: list[str]):
        super().__init__()
        self.setWindowTitle("Network Monitor")
        self.nodes = sorted(nodes)  # Sort nodes by IP address
        self.node_status = {node: ("Checking...", "-") for node in nodes}
        self.node_loggers = {node: setup_node_logging(node) for node in nodes}

        # Create the main splitter
        splitter = QSplitter(Qt.Horizontal)

        # Create the menu bar (left 1/3)
        menu_bar = QFrame()
        menu_bar.setFrameShape(QFrame.StyledPanel)
        menu_layout = QVBoxLayout()
        menu_layout.setAlignment(Qt.AlignTop)  # Align widgets to the top
        menu_layout.setContentsMargins(10, 10, 10, 10)  # Add padding around the layout
        menu_bar.setLayout(menu_layout)
        splitter.addWidget(menu_bar)

        # Add navigation buttons to the menu bar
        nodes_button = QPushButton("Nodes")
        history_button = QPushButton("History")
        menu_layout.addWidget(nodes_button)
        menu_layout.addWidget(history_button)

        # Create a stacked widget for the right pane
        self.stacked_widget = QStackedWidget()

        # Create the node status table
        self.table_widget = QTableWidget(len(nodes), 3)
        self.table_widget.setHorizontalHeaderLabels(["Node", "Status", "Last Checked"])
        self.table_widget.setSortingEnabled(False)  # Disable sorting

        # Initialize the table
        for row, node in enumerate(self.nodes):
            node_item = QTableWidgetItem(node)
            node_item.setFlags(node_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
            self.table_widget.setItem(row, 0, node_item)

            status_item = QTableWidgetItem("Checking...")
            status_item.setForeground(QColor("yellow"))  # Initial status color
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
            self.table_widget.setItem(row, 1, status_item)

            timestamp_item = QTableWidgetItem("-")
            timestamp_item.setFlags(timestamp_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
            self.table_widget.setItem(row, 2, timestamp_item)

        # Add the table widget to the stacked widget
        self.stacked_widget.addWidget(self.table_widget)

        # Create a placeholder for the history view
        self.history_list = QListWidget()
        self.stacked_widget.addWidget(self.history_list)

        # Connect buttons to change the stacked widget's current widget
        nodes_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.table_widget))
        history_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.history_list))

        # Add the stacked widget to the splitter
        splitter.addWidget(self.stacked_widget)

        # Set the splitter sizes
        splitter.setSizes([1, 2])

        self.setCentralWidget(splitter)

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
            status_item.setText(status_text)
            if status_text == "Online":
                status_item.setForeground(QColor("green"))
            elif status_text == "Offline":
                status_item.setForeground(QColor("red"))
            else:
                status_item.setForeground(QColor("yellow"))

            timestamp_item = self.table_widget.item(row, 2)
            timestamp_item.setText(timestamp)

            # Update history list
            self.history_list.addItem(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {node} is {status_text}")

            await asyncio.sleep(5)  # Check every 5 seconds

    def update_dashboard(self):
        """Update the dashboard with the latest node statuses."""
        for row, node in enumerate(self.nodes):
            status_text, timestamp = self.node_status[node]

            # Ensure the status item exists
            status_item = self.table_widget.item(row, 1)
            if status_item is None:
                status_item = QTableWidgetItem()
                status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
                self.table_widget.setItem(row, 1, status_item)

            status_item.setText(status_text)
            if status_text == "Online":
                status_item.setForeground(QColor("green"))
            elif status_text == "Offline":
                status_item.setForeground(QColor("red"))
            else:
                status_item.setForeground(QColor("yellow"))

            # Ensure the timestamp item exists
            timestamp_item = self.table_widget.item(row, 2)
            if timestamp_item is None:
                timestamp_item = QTableWidgetItem()
                timestamp_item.setFlags(timestamp_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
                self.table_widget.setItem(row, 2, timestamp_item)

            timestamp_item.setText(timestamp)