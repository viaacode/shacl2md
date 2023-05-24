# shacl2md

## Synopsis
Generates datamodel documentation from SHACL and/or RDFS files.


## Documentation

For more information about the internals of this library: see the automatically generated [documentation](/docs/README.md)
## Usage:

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

## Result example
[developer.meemoo.be](https://developer.meemoo.be/)