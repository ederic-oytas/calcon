import typer


app = typer.Typer()


@app.command(no_args_is_help=True)
def main() -> None:
    print("Hello world!")
