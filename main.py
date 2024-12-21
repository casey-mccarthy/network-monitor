import sys
import asyncio
import logging
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop
from gui.app import NetworkMonitorApp
from network.logger import setup_logging
from network.checker import read_node_file

def main(file_path: str):
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
        loop.run_forever()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_node_file>")
        sys.exit(1)

    node_file_path = sys.argv[1]
    setup_logging()  # Initialize logging
    try:
        logging.info("Starting network monitor...")
        main(node_file_path)
    except KeyboardInterrupt:
        logging.info("Network Monitor Stopped.")
        print("Network Monitor Stopped.")
