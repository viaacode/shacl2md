from typing import List, Optional

import typer
from rich import print
from typing_extensions import Annotated

from shacl2md import ShaclMarkdownGenerator, download_jar

app = typer.Typer(add_completion=False)


@app.command(context_settings={"allow_extra_args": True})
def generate(
    shacl_files: Annotated[
        List[str],
        typer.Argument(
            help="The path to SHACL files, with graph name to be processed, in the form of `model_name:./path/to/shacl_file/ttl`",
        ),
    ],
    languages: Annotated[
        List[str],
        typer.Option(
            "-l",
            "--languages",
            help="The languages to generate the documentation for",
        ),
    ],
    output_dir: Annotated[
        Optional[str],
        typer.Option(
            "-o",
            "--output_dir",
            help="The directory to output the documentation to",
        ),
    ] = "./docs",
    ontology_files: Annotated[
        List[str],
        typer.Option(
            "--ontology_file",
            help="The path to the ontology files",
        ),
    ] = [],
    shacl_shacl_validation: Annotated[
        bool,
        typer.Option(
            "--shacl_shacl_validation",
            help="Validate the SHACL files with SHACL",
        ),
    ] = False,
    version_directory: Annotated[
        bool,
        typer.Option(
            "--version_directory",
            help="Create a version directory for the documentation",
        ),
    ] = False,
    crosslink: Annotated[
        bool,
        typer.Option(
            "--crosslink",
            help="Crosslink between graphs",
        ),
    ] = False,
    jekyll_parent_page: Annotated[
        Optional[str],
        typer.Option(
            "--jekyll_parent_page",
            help="The parent page for the Jekyll documentation",
        ),
    ] = "index",
    jekyll_layout: Annotated[
        Optional[str],
        typer.Option(
            "--jekyll_layout",
            help="The layout for the Jekyll documentation",
        ),
    ] = "default",
    jekyll_nav_order: Annotated[
        Optional[int],
        typer.Option(
            "--jekyll_nav_order",
            help="The navigation order for the Jekyll documentation",
        ),
    ] = 1,
):
    shacl_files_dict = {}
    try:
        for shacl_file in shacl_files:
            graph_name, shacl_file_path = shacl_file.rsplit(":", 1)
            shacl_files_dict[graph_name] = shacl_file_path.split(",")
    except ValueError as e:
        if str(e) == "not enough values to unpack (expected 2, got 1)":
            print(
                f"[bold red]Your shacl files must include the name of the graph of your file.[/bold red]\nTry <graph_name>:{shacl_file}"
            )
            raise typer.Exit(1)
        else:
            raise e
    shacl2md_generator = ShaclMarkdownGenerator(
        languages=languages,
        output_dir=output_dir,
        shacl_shacl_validation=shacl_shacl_validation,
        version_directory=version_directory,
        crosslink_between_graphs=crosslink,
        jekyll_parent_page=jekyll_parent_page,
        jekyll_layout=jekyll_layout,
        jekyll_nav_order=jekyll_nav_order,
        ontology_graphs=ontology_files,
    )
    shacl2md_generator.generate(**shacl_files_dict)


@app.command(context_settings={"allow_extra_args": True})
def download_plantuml_jar(
    version: Annotated[
        Optional[str],
        typer.Argument(
            help="version of the plantuml jar to download",
        ),
    ] = "1.2023.11",
):
    download_jar(version)


if __name__ == "__main__":
    app()
