from typing import List, Optional, Tuple

import typer
from rich import print
from typing_extensions import Annotated

from shacl2md import ShaclMarkdownGenerator

app = typer.Typer(add_completion=False)

@app.command(
    context_settings={"allow_extra_args": True}
)
def generate(
    shacl_files : Annotated[List[str], typer.Argument(
        help="The path to SHACL files, with graph name to be processed, in the form of `graph_name:./path/to/shacl_file/ttl`",
    )],
    languages : Annotated[List[str], typer.Option(
        "-l",
        "--languages",
    )],
    output_dir : Annotated[Optional[str], typer.Option(
        "-o",
        "--output_dir"
    )] = "./docs",
    ontology_files : Annotated[List[str] , typer.Option(
        "-of",
        "--ontology_file"
    )] = [],
    shacl_shacl_validation : Annotated[bool, typer.Option(
        "-ssv",
        "--shacl_shacl_validation"
    )] = False,
    verion_directory : Annotated[bool, typer.Option(
        "-vd",
        "--verion_directory"
    )] = False,
    crosslink : Annotated[bool, typer.Option(
        "-cl",
        "--crosslink"
    )] = False,
    jekyll_parent_page : Annotated[Optional[str], typer.Option(
        "-jpp",
        "--jekyll_parent_page"
    )] = "index",
    jekyll_layout : Annotated[Optional[str], typer.Option(
        "-jl",
        "--jekyll_layout"
    )] = "default",
    jekyll_nav_order : Annotated[Optional[int], typer.Option(
        "-jno",
        "--jekyll_nav_order"
    )] = 1,


):
    shacl_files_dict = {}
    try:
        for shacl_file in shacl_files:
            graph_name, shacl_file_path = shacl_file.rsplit(":", 1)
            shacl_files_dict[graph_name] = shacl_file_path
    except ValueError as e:
        if str(e) == "not enough values to unpack (expected 2, got 1)":
            print(f"[bold red]Your shacl files must include the name of the graph of your file.[/bold red]\nTry <graph_name>:{shacl_file}")
            raise typer.Exit(1)
        else:
            raise e
    shacl2md_generator = ShaclMarkdownGenerator(
        languages=languages,
        output_dir=output_dir,
        shacl_shacl_validation=shacl_shacl_validation,
        version_directory=verion_directory,
        crosslink_between_graphs=crosslink,
        jekyll_parent_page=jekyll_parent_page,
        jekyll_layout=jekyll_layout,
        jekyll_nav_order=jekyll_nav_order,
        ontology_graphs=ontology_files
    )
    shacl2md_generator.generate(**shacl_files_dict)

if __name__ == "__main__":
    app()