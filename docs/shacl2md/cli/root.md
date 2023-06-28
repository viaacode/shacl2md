# Root

[Shacl2md Index](../../README.md#shacl2md-index) /
[Shacl2md](../index.md#shacl2md) /
[Cli](./index.md#cli) /
Root

> Auto-generated documentation for [shacl2md.cli.root](../../../shacl2md/cli/root.py) module.

- [Root](#root)
  - [generate](#generate)

## generate

[Show source in root.py:11](../../../shacl2md/cli/root.py#L11)

#### Signature

```python
@app.command(context_settings={"allow_extra_args": True})
def generate(
    shacl_files: Annotated[
        List[str],
        typer.Argument(
            help=(
                "The path to SHACL files, with graph name to be processed, in the form"
                " of `graph_name:./path/to/shacl_file/ttl`"
            )
        ),
    ],
    languages: Annotated[
        List[str],
        typer.Option(
            "-l", "--languages", help="The languages to generate the documentation for"
        ),
    ],
    output_dir: Annotated[
        Optional[str],
        typer.Option(
            "-o", "--output_dir", help="The directory to output the documentation to"
        ),
    ] = "./docs",
    ontology_files: Annotated[
        List[str],
        typer.Option("-of", "--ontology_file", help="The path to the ontology files"),
    ] = [],
    shacl_shacl_validation: Annotated[
        bool,
        typer.Option(
            "-ssv",
            "--shacl_shacl_validation",
            help="Validate the SHACL files with SHACL",
        ),
    ] = False,
    verion_directory: Annotated[
        bool,
        typer.Option(
            "-vd",
            "--verion_directory",
            help="Create a version directory for the documentation",
        ),
    ] = False,
    crosslink: Annotated[
        bool, typer.Option("-cl", "--crosslink", help="Crosslink between graphs")
    ] = False,
    jekyll_parent_page: Annotated[
        Optional[str],
        typer.Option(
            "-jpp",
            "--jekyll_parent_page",
            help="The parent page for the Jekyll documentation",
        ),
    ] = "index",
    jekyll_layout: Annotated[
        Optional[str],
        typer.Option(
            "-jl", "--jekyll_layout", help="The layout for the Jekyll documentation"
        ),
    ] = "default",
    jekyll_nav_order: Annotated[
        Optional[int],
        typer.Option(
            "-jno",
            "--jekyll_nav_order",
            help="The navigation order for the Jekyll documentation",
        ),
    ] = 1,
):
    ...
```