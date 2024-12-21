import time
import asyncio
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QStackedWidget, QListWidget, QFileDialog
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from network.checker import ping, read_node_file
from network.logger import setup_node_logging
from network.node import Node
from network.mapper import draw_network_topology
from gui.matplotlib_widget import StaticNetworkMap

class NetworkMonitorApp(QMainWindow):
    def __init__(self, nodes: list[Node], file_path: str):
        super().__init__()
        self.setWindowTitle("Network Monitor")
        self.nodes = sorted(nodes, key=lambda node: node.ip)  # Sort nodes by IP address
        self.node_status = {node.ip: ("Checking...", "-") for node in nodes}
        self.previous_status = {node.ip: None for node in nodes}  # Track previous status
        self.node_loggers = {node.ip: setup_node_logging(node.ip) for node in nodes}
        self.file_path = file_path

        # Main layout
        main_layout = QVBoxLayout()

        # Header with menu buttons
        header = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        self.nodes_button = QPushButton("Nodes")
        self.history_button = QPushButton("History")
        self.map_button = QPushButton("Map")
        self.nodes_button.setCheckable(True)
        self.history_button.setCheckable(True)
        self.map_button.setCheckable(True)
        self.nodes_button.setChecked(True)  # Default to nodes view
        self.update_button_styles()
        self.nodes_button.clicked.connect(self.show_nodes)
        self.history_button.clicked.connect(self.show_history)
        self.map_button.clicked.connect(self.show_map)
        header_layout.addWidget(self.nodes_button)
        header_layout.addWidget(self.history_button)
        header_layout.addWidget(self.map_button)
        header.setLayout(header_layout)
        main_layout.addWidget(header)

        # Create a stacked widget for the main content
        self.stacked_widget = QStackedWidget()

        # Create the node status table
        self.table_widget = QTableWidget(len(nodes), 3)
        self.table_widget.setHorizontalHeaderLabels(["Node", "Status", "Last Checked"])
        self.table_widget.setSortingEnabled(False)  # Disable sorting

        # Hide row and column headers
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.horizontalHeader().setVisible(False)

        # Initialize the table
        for row, node in enumerate(self.nodes):
            node_item = QTableWidgetItem(node.ip)
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

        # Add the StaticNetworkMap widget for the network map
        self.map_widget = StaticNetworkMap()
        self.stacked_widget.addWidget(self.map_widget)

        # Add the stacked widget to the main layout
        main_layout.addWidget(self.stacked_widget)

        # Footer with file path and change button
        footer = QWidget()
        footer_layout = QVBoxLayout()
        footer_layout.setAlignment(Qt.AlignCenter)
        self.file_label = QLabel(f"Monitoring file: {self.file_path}")
        change_file_button = QPushButton("Change File")
        change_file_button.clicked.connect(self.change_file)
        footer_layout.addWidget(self.file_label)
        footer_layout.addWidget(change_file_button)

        footer.setLayout(footer_layout)
        main_layout.addWidget(footer)

        # Set the main layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Set up a timer to update the dashboard
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(1000)  # Update every 1 second

    def show_nodes(self):
        """Show the nodes view."""
        self.stacked_widget.setCurrentWidget(self.table_widget)
        self.nodes_button.setChecked(True)
        self.history_button.setChecked(False)
        self.map_button.setChecked(False)
        self.update_button_styles()

    def show_history(self):
        """Show the history view."""
        self.stacked_widget.setCurrentWidget(self.history_list)
        self.nodes_button.setChecked(False)
        self.history_button.setChecked(True)
        self.map_button.setChecked(False)
        self.update_button_styles()

    def show_map(self):
        """Show the network topology map."""
        self.stacked_widget.setCurrentWidget(self.map_widget)
        self.nodes_button.setChecked(False)
        self.history_button.setChecked(False)
        self.map_button.setChecked(True)
        self.update_button_styles()

    def update_button_styles(self):
        """Update the styles of the header buttons to indicate the active view."""
        active_style = "background-color: lightblue; font-weight: bold;"
        inactive_style = "background-color: none; font-weight: normal;"
        self.nodes_button.setStyleSheet(active_style if self.nodes_button.isChecked() else inactive_style)
        self.history_button.setStyleSheet(active_style if self.history_button.isChecked() else inactive_style)
        self.map_button.setStyleSheet(active_style if self.map_button.isChecked() else inactive_style)

    def start_node_tasks(self):
        """Start asynchronous tasks for each node."""
        self.node_tasks = [asyncio.create_task(self.check_node(node, row)) for row, node in enumerate(self.nodes)]

    async def check_node(self, node: Node, row: int):
        """Check the status of a node and update the table."""
        while True:
            status = await ping(node.ip)
            status_text = "Online" if status else "Offline"
            timestamp = time.strftime("%H:%M:%S")
            self.node_status[node.ip] = (status_text, timestamp)

            # Log status to node-specific log
            node_logger = self.node_loggers[node.ip]
            node_logger.info(f"Node {node.ip} is {status_text}")

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

            # Update history list only if status changes
            if self.previous_status[node.ip] != status_text:
                self.history_list.addItem(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Node {node.ip} has {'come online' if status_text == 'Online' else 'gone offline'} at {timestamp}")
                self.previous_status[node.ip] = status_text

            await asyncio.sleep(5)  # Check every 5 seconds

    def update_dashboard(self):
        """Update the dashboard with the latest node statuses."""
        for row, node in enumerate(self.nodes):
            status_text, timestamp = self.node_status[node.ip]

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

    def change_file(self):
        """Open a file dialog to change the monitored file."""
        new_file_path, _ = QFileDialog.getOpenFileName(self, "Select Node File", "", "Text Files (*.txt);;All Files (*)")
        if new_file_path:
            self.file_path = new_file_path
            self.file_label.setText(f"Monitoring file: {self.file_path}")
            # Reload nodes from the new file
            self.nodes = sorted(read_node_file(self.file_path), key=lambda node: node.ip)
            self.node_status = {node.ip: ("Checking...", "-") for node in self.nodes}
            self.previous_status = {node.ip: None for node in self.nodes}
            self.node_loggers = {node.ip: setup_node_logging(node.ip) for node in self.nodes}
            self.table_widget.setRowCount(len(self.nodes))
            for row, node in enumerate(self.nodes):
                node_item = QTableWidgetItem(node.ip)
                node_item.setFlags(node_item.flags() & ~Qt.ItemIsEditable)
                self.table_widget.setItem(row, 0, node_item)

                status_item = QTableWidgetItem("Checking...")
                status_item.setForeground(QColor("yellow"))
                status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
                self.table_widget.setItem(row, 1, status_item)

                timestamp_item = QTableWidgetItem("-")
                timestamp_item.setFlags(timestamp_item.flags() & ~Qt.ItemIsEditable)
                self.table_widget.setItem(row, 2, timestamp_item)

            # Restart node tasks
            for task in self.node_tasks:
                task.cancel()
            self.start_node_tasks()