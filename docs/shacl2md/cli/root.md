# Root

[Shacl2md Index](../../README.md#shacl2md-index) /
[Shacl2md](../index.md#shacl2md) /
[Cli](./index.md#cli) /
Root

> Auto-generated documentation for [shacl2md.cli.root](../../../shacl2md/cli/root.py) module.

- [Root](#root)
  - [download_plantuml_jar](#download_plantuml_jar)
  - [generate](#generate)

## download_plantuml_jar

[Show source in root.py:83](../../../shacl2md/cli/root.py#L83)

#### Signature

```python
@app.command(context_settings={"allow_extra_args": True})
def download_plantuml_jar(
    version: Annotated[
        Optional[str], typer.Argument(help="version of the plantuml jar to download")
    ] = "1.2023.11"
):
    ...
```



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
                " of `model_name:./path/to/shacl_file/ttl`"
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
        List[str], typer.Option("--ontology_file", help="The path to the ontology files")
    ] = [],
    shacl_shacl_validation: Annotated[
        bool,
        typer.Option(
            "--shacl_shacl_validation", help="Validate the SHACL files with SHACL"
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
        bool, typer.Option("--crosslink", help="Crosslink between graphs")
    ] = False,
    jekyll_parent_page: Annotated[
        Optional[str],
        typer.Option(
            "--jekyll_parent_page", help="The parent page for the Jekyll documentation"
        ),
    ] = "index",
    jekyll_layout: Annotated[
        Optional[str],
        typer.Option("--jekyll_layout", help="The layout for the Jekyll documentation"),
    ] = "default",
    jekyll_nav_order: Annotated[
        Optional[int],
        typer.Option(
            "--jekyll_nav_order",
            help="The navigation order for the Jekyll documentation",
        ),
    ] = 1,
):
    ...
```