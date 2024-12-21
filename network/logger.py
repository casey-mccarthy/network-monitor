import logging
import os

def setup_logging():
    """Set up logging for the main application."""
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler("logs/network_monitor.log", mode='a')]
    )

def setup_node_logging(node: str):
    """Set up logging for a specific node."""
    node_log_file = f"logs/{node}.log"
    node_logger = logging.getLogger(node)
    node_logger.setLevel(logging.INFO)
    handler = logging.FileHandler(node_log_file, mode='a')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    node_logger.addHandler(handler)
    return node_logger 