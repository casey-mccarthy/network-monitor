import sys
import asyncio
import logging
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop
from gui.app import NetworkMonitorApp
from network.logger import setup_logging
from network.checker import read_node_file

def main(file_path: str = "nodes.txt"):
    """Main function to set up and run the network monitor."""
    nodes = read_node_file(file_path)
    if not nodes:
        logging.error("No nodes to monitor. Please check your node file.")
        return

    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = NetworkMonitorApp(nodes, file_path)
    window.show()

    # Start node tasks after the event loop is running
    loop.call_soon(window.start_node_tasks)

    with loop:
        loop.run_forever()

if __name__ == "__main__":
    setup_logging()  # Initialize logging
    try:
        logging.info("Starting network monitor...")
        # Use default file path if no argument is provided
        node_file_path = sys.argv[1] if len(sys.argv) > 1 else "nodes.txt"
        main(node_file_path)
    except KeyboardInterrupt:
        logging.info("Network Monitor Stopped.")
        logging.info("Network Monitor Stopped.")
