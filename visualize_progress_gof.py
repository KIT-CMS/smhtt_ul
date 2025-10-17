import os
import json
import time
import argparse
import platform
from pathlib import Path
from typing import List, Optional, Dict

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box # Needed for grid lines
from itertools import product

# --- Configuration ---
DEFAULT_PREFIX = "2018_mt"
# ---

def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Monitor Goodness-of-Fit p-values in a running process.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--folder", type=str, help="The root directory containing the result folders."
    )
    parser.add_argument(
        "--vars", required=True, nargs='+', type=str,
        help="A space-separated list of all variable names used for the matrix."
    )
    parser.add_argument(
        "--prefix", type=str, default=DEFAULT_PREFIX,
        help=f"The common prefix for result folders (e.g., '{DEFAULT_PREFIX}')."
    )
    parser.add_argument(
        "--test-type", choices=['gof', 'gof_KS', 'gof_AD'], default='gof',
        help="The type of Goodness-of-Fit test to display."
    )
    parser.add_argument(
        "--threshold", type=float, default=0.01,
        help="The p-value threshold for color-coding (values below are red)."
    )
    parser.add_argument(
        "--interval", type=int, default=10,
        help="The refresh interval in seconds."
    )
    parser.add_argument(
        "--no-live", action="store_true",
        help="Disable live updating and print the matrix just once."
    )
    parser.add_argument(
        "--header-wrap", type=int, default=1,
        help="Number of characters per line for wrapped column headers (e.g., 1 for vertical text)."
    )
    return parser.parse_args()

def clear_screen():
    """Clears the terminal screen."""
    command = "cls" if platform.system() == "Windows" else "clear"
    os.system(command)

def fetch_p_value(
    base_path: Path, prefix: str, var1: str, var2: str, test_type: str
) -> Optional[float]:
    """
    Finds and parses the p-value from the correct JSON file,
    handling both simple and nested JSON structures.
    """
    if var1 == var2: folder_name = f"{prefix}_{var1}"
    else: folder_name = f"{prefix}_{var1}_{var2}"
    
    folder_path = base_path / folder_name
    if not folder_path.exists() and var1 != var2:
        folder_path = base_path / f"{prefix}_{var2}_{var1}"

    if not folder_path.exists(): return None
    json_file = folder_path / f"{test_type}.json"
    if not json_file.exists(): return None

    try:
        with open(json_file, 'r') as f:
            content = f.read()
            if not content: return None
            data = json.loads(content)
        
        # Get the dictionary under "125.0"
        mass_dict = data.get("125.0")
        if not isinstance(mass_dict, dict):
            return None

        # --- NEW LOGIC TO HANDLE BOTH JSON STRUCTURES ---
        # First, try the simple structure (for 'gof.json')
        p_value = mass_dict.get("p")

        # If that fails, assume the nested structure (for 'gof_KS.json' / 'gof_AD.json')
        if p_value is None:
            # Check if there is a nested dictionary
            if mass_dict and isinstance(mass_dict, dict):
                # Get the first (and presumably only) nested dictionary's value
                nested_dict = next(iter(mass_dict.values()), None)
                if isinstance(nested_dict, dict):
                    p_value = nested_dict.get("p")
        
        return float(p_value) if p_value is not None else None
        
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        return None

def format_header(name: str, wrap_limit: int) -> str:
    """Wraps text by inserting newlines, e.g., limit=1 makes it vertical."""
    if wrap_limit <= 0: return name
    chunks = [name[i:i + wrap_limit] for i in range(0, len(name), wrap_limit)]
    return "\n".join(chunks)

def generate_results_matrix(
    p_values: Dict[tuple, Optional[float]], variables: List[str], threshold: float, header_wrap: int
) -> Table:
    """Creates a rich Table formatted as a lower-triangular matrix with wrapped headers."""
    
    matrix = Table(
        show_header=True,       # Enable headers
        header_style="bold magenta",
        box=box.SQUARE,         # Enable grid lines
        padding=(0, 1)          # Compact padding
    )
    
    # First column is for the row labels (variable names)
    matrix.add_column("Var", style="dim", justify="right", no_wrap=True)
    
    # Add columns with wrapped headers
    for var in variables:
        matrix.add_column(format_header(var, header_wrap), justify="center")

    # Populate the rows
    for row_index, row_var in enumerate(variables):
        row_data = [row_var]
        for col_index, col_var in enumerate(variables):
            if col_index > row_index:
                cell_content = Text("")
            else:
                p_val = p_values.get((row_var, col_var))
                if p_val is None:
                    cell_content = Text("--", style="dim")
                else:
                    color = "green" if p_val >= threshold else "red"
                    cell_content = Text(f"{p_val:.2f}", style=color)
            row_data.append(cell_content)
        matrix.add_row(*row_data)
        
    return matrix

def print_status(console: Console, variables: List[str], args: argparse.Namespace):
    """Fetches values, builds the matrix, and prints it."""
    p_values = {}
    for row_var, col_var in product(variables, repeat=2):
        val = fetch_p_value(Path(args.folder), args.prefix, row_var, col_var, args.test_type)
        p_values[(row_var, col_var)] = val
        p_values[(col_var, row_var)] = val
    
    matrix = generate_results_matrix(p_values, variables, args.threshold, args.header_wrap)
    console.print(matrix)
    
def main():
    """Main function to run the monitoring loop."""
    args = parse_arguments()
    console = Console()

    base_path = Path(args.folder)
    if not base_path.is_dir():
        console.print(f"[bold red]Error:[/bold red] Folder not found: {args.folder}")
        return

    # Run once to check for data and prevent blank screen on startup
    print_status(console, args.vars, args)
    
    if args.no_live:
        return

    try:
        while True:
            p_values_cache = {}  # Clear cache to refresh all values
            time.sleep(args.interval)
            clear_screen()
            console.print(f"[bold]Goodness-of-Fit Matrix ({args.test_type.upper()})[/bold]")
            print_status(console, args.vars, args)
            status_text = (
                f"\nLast updated: {time.strftime('%Y-%m-%d %H:%M:%S')}."
                f" Refreshing every {args.interval}s. Press Ctrl+C to exit."
            )
            console.print(status_text)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Monitoring stopped.[/bold yellow]")

if __name__ == "__main__":
    main()
