import typer

from pdf_editor.cli.commands.bulk import app as bulk_app
from pdf_editor.cli.commands.compress import compress_command
from pdf_editor.cli.commands.image import app as image_app
from pdf_editor.cli.commands.merge import merge_command
from pdf_editor.cli.commands.pages import app as pages_app

app = typer.Typer(
    name="pdf-editor",
    help="PDF Editor CLI — bulk PDF operations from the command line.",
    no_args_is_help=True,
)

app.add_typer(pages_app, name="pages")
app.add_typer(image_app, name="image")
app.add_typer(bulk_app, name="bulk")
app.command(name="merge")(merge_command)
app.command(name="compress")(compress_command)
