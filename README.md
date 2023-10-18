# shacl2md

## Synopsis
Generates datamodel documentation from SHACL and/or RDFS files.


## Documentation

For more information about the internals of this library: see the automatically generated [documentation](/docs/README.md)
## Usage:

### Python code
```python
sh_md = ShaclMarkdownGenerator(
    languages=["nl", "en", "fr"],
    output_dir="./",
    shacl_shacl_validation=True,
    version_directory=True,
    crosslink_between_graphs=True,
    ontology_graphs=[
        "/datamodels/ontologies/dct.rdfs.ttl",
        "/datamodels/ontologies/ebucore.rdfs.ttl",
        "/datamodels/ontologies/edm.rdfs.ttl",
        "/datamodels/ontologies/foaf.rdfs.ttl",
        "/datamodels/ontologies/org.rdfs.ttl",
        "/datamodels/ontologies/premis.rdfs.ttl",
        "/datamodels/ontologies/prov.rdfs.ttl",
        "/datamodels/ontologies/rdf.rdfs.ttl",
        "/datamodels/ontologies/schema.rdfs.ttl",
        "/datamodels/ontologies/seq.rdfs.ttl",
        "/datamodels/ontologies/skos.rdfs.ttl",
        "/datamodels/ontologies/skos-xl.rdfs.ttl",
        "/datamodels/organizations/organizations.rdfs.ttl",
        "/datamodels/organizations/organization-roles.skos.ttl",
        "/datamodels/organizations/organization-types.skos.ttl",
        "/datamodels/objects/objects.rdfs.ttl",

    ]
)
sh_md.generate(organization="/datamodels/organizations/organizations.shacl.ttl",
               descriptive="/datamodels/description/description.shacl.ttl",
               events="/datamodels/events/events.shacl.ttl",
               object="/datamodels/objects/objects.shacl.ttl",
               terms="/datamodels/terms/terms.shacl.ttl",)
```

### CLI
#### Instalation
```console
$ pip install shacl2md
```

#### `shacl2md generate`

**Usage**:

```console
$ shacl2md generate [OPTIONS] SHACL_FILES...
```

**Arguments**:

* `SHACL_FILES...`: The path to SHACL files, with graph name to be processed, in the form of `graph_name:./path/to/shacl_file/ttl`  [required]

**Options**:

* `-l, --languages TEXT`: The languages to generate the documentation for  [required]
* `-o, --output_dir TEXT`: The directory to output the documentation to  [default: ./docs]
* `--ontology_file TEXT`: The path to the ontology files
* `--shacl_shacl_validation`: Validate the SHACL files with SHACL
* `--version_directory`: Create a version directory for the documentation
* `--crosslink`: Crosslink between graphs
* `--jekyll_parent_page TEXT`: The parent page for the Jekyll documentation  [default: index]
* `--jekyll_layout TEXT`: The layout for the Jekyll documentation  [default: default]
* `--jekyll_nav_order INTEGER`: The navigation order for the Jekyll documentation  [default: 1]
* `--help`: Show this message and exit.



## Result example
[developer.meemoo.be](https://developer.meemoo.be/)