"""Console script for python_boilerplate."""
import python_boilerplate

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for python_boilerplate."""
    console.print("Replace this message by putting your code into "
               "python_boilerplate.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    


if __name__ == "__main__":
    app()
