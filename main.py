import asyncio
import subprocess
import time
import logging
from rich.live import Live
from rich.table import Table
from rich.console import Console

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

def create_dashboard(nodes: list[str]) -> Table:
    """Create an initial dashboard table for the network monitor."""
    table = Table(title="Network Monitor Dashboard")
    table.add_column("Node", justify="left", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center", style="bold")
    table.add_column("Last Checked", justify="right", style="dim")
    
    # Initialize the table with nodes and default status
    for node in nodes:
        table.add_row(node, "[yellow]Checking...", "-")
    
    return table

async def update_dashboard(live: Live, nodes: list[str]) -> None:
    """Update the dashboard with the status of each node."""
    node_status = {node: ("[yellow]Checking...", "-") for node in nodes}
    
    while True:
        logging.info("Updating dashboard...")
        tasks = {node: ping(node) for node in nodes}
        
        for node, task in tasks.items():
            status = await task
            status_text = "[green]Online" if status else "[red]Offline"
            timestamp = time.strftime("%H:%M:%S")
            node_status[node] = (status_text, timestamp)
        
        table = Table(title="Network Monitor Dashboard")
        table.add_column("Node", justify="left", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center", style="bold")
        table.add_column("Last Checked", justify="right", style="dim")
        
        for node in nodes:
            status_text, last_checked = node_status[node]
            table.add_row(node, status_text, last_checked)
        
        live.update(table)
        logging.info("Dashboard updated.")
        await asyncio.sleep(5)

async def main(file_path: str):
    """Main function to set up and run the network monitor."""
    console = Console()
    nodes = read_node_file(file_path)
    
    if not nodes:
        console.print("[bold red]No nodes to monitor. Please check your node file.")
        return
    
    console.print(f"[bold green]Starting network monitor for {len(nodes)} nodes.")
    table = create_dashboard(nodes)
    
    with Live(table, refresh_per_second=1) as live:
        await update_dashboard(live, nodes)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python network_monitor.py <path_to_node_file>")
        sys.exit(1)
    
    node_file_path = sys.argv[1]
    try:
        logging.info("Starting network monitor...")
        asyncio.run(main(node_file_path))
    except KeyboardInterrupt:
        logging.info("Network Monitor Stopped.")
        print("\n[bold red]Network Monitor Stopped.")
