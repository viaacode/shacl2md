# Generator

[Shacl2md Index](../README.md#shacl2md-index) /
[Shacl2md](./index.md#shacl2md) /
Generator

> Auto-generated documentation for [shacl2md.generator](../../shacl2md/generator.py) module.

- [Generator](#generator)
  - [ShaclGraph](#shaclgraph)
    - [ShaclGraph().generate_md](#shaclgraph()generate_md)
    - [ShaclGraph().generate_puml](#shaclgraph()generate_puml)
    - [ShaclGraph().validate](#shaclgraph()validate)
  - [ShaclMarkdownGenerator](#shaclmarkdowngenerator)
    - [ShaclMarkdownGenerator().filter_graph](#shaclmarkdowngenerator()filter_graph)
    - [ShaclMarkdownGenerator().filter_language](#shaclmarkdowngenerator()filter_language)
    - [ShaclMarkdownGenerator().generate](#shaclmarkdowngenerator()generate)
    - [ShaclMarkdownGenerator().get_graph](#shaclmarkdowngenerator()get_graph)

## ShaclGraph

[Show source in generator.py:156](../../shacl2md/generator.py#L156)

#### Signature

```python
class ShaclGraph:
    def __init__(self, name: str, lang: str, generator: ShaclMarkdownGenerator):
        ...
```

#### See also

- [ShaclMarkdownGenerator](#shaclmarkdowngenerator)

### ShaclGraph().generate_md

[Show source in generator.py:222](../../shacl2md/generator.py#L222)

Generate markdown documentation from the SHACL graph.

#### Signature

```python
def generate_md(self):
    ...
```

### ShaclGraph().generate_puml

[Show source in generator.py:185](../../shacl2md/generator.py#L185)

Generate a PlantUML diagram from the SHACL graph.

#### Signature

```python
def generate_puml(self):
    ...
```

### ShaclGraph().validate

[Show source in generator.py:300](../../shacl2md/generator.py#L300)

Validate the SHACL graph against the SHACL specification.

#### Signature

```python
def validate(self):
    ...
```



## ShaclMarkdownGenerator

[Show source in generator.py:20](../../shacl2md/generator.py#L20)

#### Signature

```python
class ShaclMarkdownGenerator:
    def __init__(
        self,
        languages: List[str],
        output_dir: str = "./",
        shacl_shacl_validation: bool = False,
        version_directory: bool = False,
        crosslink_between_graphs: bool = False,
        jekyll_parent_page: str = "index",
        jekyll_layout: str = "default",
        jekyll_nav_order: int = 1,
        ontology_graphs: List[Union[str, Graph]] = [],
    ):
        ...
```

### ShaclMarkdownGenerator().filter_graph

[Show source in generator.py:91](../../shacl2md/generator.py#L91)

Get all other graphs.

#### Arguments

- `graph_name` *str* - Name of the graph to filter.

#### Signature

```python
def filter_graph(self, graph_name: str):
    ...
```

### ShaclMarkdownGenerator().filter_language

[Show source in generator.py:82](../../shacl2md/generator.py#L82)

Get all other languages.

#### Arguments

- `lang` *str* - language to filter

#### Signature

```python
def filter_language(self, lang: str):
    ...
```

### ShaclMarkdownGenerator().generate

[Show source in generator.py:100](../../shacl2md/generator.py#L100)

Generate markdown documentation from SHACL files.

#### Arguments

- `**shacls` - Dictionary of SHACL files or Graphs to generate documentation for. The key is the name of the SHACL graph, the value is the filename of the SHACL file.

#### Raises

- `ValidationFailure` *pyshacl.errors.ValidationFailure* - Raised when the SHACL files do not validate against the SHACL specification.

#### Examples

```python
>>> from shacl2md import ShaclMarkdownGenerator
>>> sh_md = ShaclMarkdownGenerator(
...     ["nl", "en", "fr"],
...     "./output",
...     shacl_shacl_validation=True,
...     version_directory=True,
...     crosslink_between_graphs=True,
...     ontology_graphs=[
...         "/path_to_ontology/rdfs.ttl",
...     ]
... )
>>> sh_md.generate(
...     organizations="/path_to_shacl/organizations.shacl.ttl",
...     description="/path_to_shacl/description.shacl.ttl",
... )
```

#### Signature

```python
def generate(self, **shacls) -> None:
    ...
```

### ShaclMarkdownGenerator().get_graph

[Show source in generator.py:73](../../shacl2md/generator.py#L73)

Get a graph by name.

#### Arguments

- `graph_name` *str* - Name of the graph to get.

#### Signature

```python
def get_graph(self, graph_name: str):
    ...
```