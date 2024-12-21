import asyncio
import logging
import subprocess
from network.node import Node  # Import Node from the new module

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

def read_node_file(file_path: str) -> list[Node]:
    """Read a file containing a list of IP addresses, device types, and connections."""
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
                    nodes[ip] = Node(ip, device_type)
                elif len(parts) == 2:
                    connections.append(parts)

        # Establish connections
        for ip1, ip2 in connections:
            if ip1 in nodes and ip2 in nodes:
                nodes[ip1].connect(nodes[ip2])

    except FileNotFoundError:
        logging.error(f"Error: The file {file_path} was not found.")

    return list(nodes.values()) 