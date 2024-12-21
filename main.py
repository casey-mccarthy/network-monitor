import sys
import asyncio
import subprocess
import time
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor
from qasync import QEventLoop

# Configure logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("network_monitor.log", mode='a')]
)

async def ping(host: str) -> bool:
    """Ping a host to check if it is reachable."""
    try:
        logging.info(f"Pinging {host}...")
        result = await asyncio.create_subprocess_shell(
            f"ping -c 1 -W 1 {host}",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        await result.communicate()
        success = result.returncode == 0
        logging.info(f"Ping to {host} {'succeeded' if success else 'failed'}.")
        return success
    except Exception as e:
        logging.error(f"Error pinging {host}: {e}")
        return False

def read_node_file(file_path: str) -> list[str]:
    """Read a file containing a list of IP addresses, one per line."""
    try:
        logging.info(f"Reading node file: {file_path}")
        with open(file_path, 'r') as file:
            nodes = [line.strip() for line in file if line.strip()]
        logging.info(f"Loaded {len(nodes)} nodes from file.")
        return nodes
    except FileNotFoundError:
        logging.error(f"Error: The file {file_path} was not found.")
        return []

class NetworkMonitorApp(QMainWindow):
    def __init__(self, nodes: list[str]):
        super().__init__()
        self.setWindowTitle("Network Monitor")
        self.nodes = nodes
        self.node_status = {node: ("Checking...", "-") for node in nodes}

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
        layout.setContentsMargins(10, 10, 10, 10)  # Add a buffer around the window

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
        logging.info("Updating dashboard...")
        tasks = {node: ping(node) for node in self.nodes}

        for row, (node, task) in enumerate(tasks.items()):
            status = await task
            status_text = "Online" if status else "Offline"
            timestamp = time.strftime("%H:%M:%S")
            self.node_status[node] = (status_text, timestamp)

            # Update the table widget with color coding
            status_item = QTableWidgetItem(status_text)
            if status:
                status_item.setForeground(QColor("green"))
            else:
                status_item.setForeground(QColor("red"))

            self.table_widget.setItem(row, 1, status_item)
            self.table_widget.setItem(row, 2, QTableWidgetItem(timestamp))

        logging.info("Dashboard updated.")

async def main(file_path: str):
    """Main function to set up and run the network monitor."""
    nodes = read_node_file(file_path)
    if not nodes:
        print("No nodes to monitor. Please check your node file.")
        return

    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = NetworkMonitorApp(nodes)
    window.show()

    with loop:
        await loop.run_forever()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python network_monitor.py <path_to_node_file>")
        sys.exit(1)

    node_file_path = sys.argv[1]
    try:
        logging.info("Starting network monitor...")
        asyncio.run(main(node_file_path))
    except KeyboardInterrupt:
        logging.info("Network Monitor Stopped.")
        print("Network Monitor Stopped.")
