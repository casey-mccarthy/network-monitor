import asyncio
import logging
import subprocess
from network.node import NodeData  # Import NodeData from the new module

async def ping(host: str) -> bool:
    """Ping a host to check if it is reachable.

    Args:
        host (str): The IP address or hostname to ping.

    Returns:
        bool: True if the host is reachable, False otherwise.
    """
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

def read_node_file(file_path: str) -> list[NodeData]:
    """Read a file containing a list of IP addresses, device types, and connections.

    Args:
        file_path (str): The path to the node file.

    Returns:
        list[NodeData]: A list of NodeData objects representing the nodes.
    """
    nodes = {}
    connections = []

    try:
        logging.info(f"Reading node file: {file_path}")
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(',')
                if len(parts) == 2:
                    ip, device_type = parts
                    if device_type.lower() in ["router", "switch", "pc"]:
                        nodes[ip] = NodeData(ip, device_type)
                    else:
                        connections.append(parts)
                elif len(parts) == 2:
                    connections.append(parts)

        # Establish connections
        for ip1, ip2 in connections:
            if ip1 in nodes and ip2 in nodes:
                nodes[ip1].connect(nodes[ip2])

    except FileNotFoundError:
        logging.error(f"Error: The file {file_path} was not found.")

    return list(nodes.values()) 