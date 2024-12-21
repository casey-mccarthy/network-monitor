import asyncio
import logging
import subprocess

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