import argparse

from jinja2 import Environment, PackageLoader, select_autoescape
from rdflib.graph import Graph
from rdflib.namespace import DCTERMS, FOAF, OWL, RDF, RDFS, SKOS, Namespace
from rdflib.term import BNode, Literal, URIRef

from queries import (GET_AUTHORS, GET_CLASSES, GET_DOC_MD, GET_PROPERTIES,
                     GET_SUBCLASSES, GET_SUPERCLASSES)

SHACL = Namespace("http://www.w3.org/ns/shacl#")


def get_doc(g):
    for row in g.query(GET_DOC_MD, initBindings={"lang": Literal("nl")}):
        row.authors = list(get_authors(g))
        return row


def get_classes(g):
    classes = []
    for row in g.query(GET_CLASSES, initBindings={"lang": Literal("nl")}):
        classes.append(
            {
                "iri": row.iri,
                "shortname": row.iri.n3(g.namespace_manager),
                "label": row.label,
                "description": row.description,
                "parent": list(
                    g.query(GET_SUPERCLASSES, initBindings={"child": row.iri, "lang": Literal("nl")})
                ),
                "child": list(
                    g.query(GET_SUBCLASSES, initBindings={"parent": row.iri, "lang": Literal("nl")})
                ),
                "properties": list(get_properties(g, row.iri)),
            }
        )

    return classes


def get_properties(g, c=None):
    properties = []
    if c is not None:
        qres = g.query(GET_PROPERTIES, initBindings={"lang": Literal("nl"), "targetClass": c})
    else:
        qres = g.query(GET_PROPERTIES, initBindings={"lang": Literal("nl")})
    for row in qres:
        # print(row)

        properties.append(
            {
                "iri": row.iri,
                "shortname": row.iri.n3(g.namespace_manager),
                "label": row.label,
                "description": row.description,
                
            }
        )
        if row.datatype:
            properties[-1]["datatype"] = {
                "label": row.datatype_label,
                "iri": row.datatype,
                "shortname": row.datatype.n3(g.namespace_manager),
            }
        elif row.classtype:
            properties[-1]["classtype"] = {
                "label": row.classtype_label,
                "iri": row.classtype,
                "shortname": row.classtype.n3(g.namespace_manager),
            }
    # print(properties)
    return properties


def get_authors(g):
    return g.query(GET_AUTHORS)


def main(args):

    g = Graph()
    for file in args.files:
        g.parse(file)
    env = Environment(
        loader=PackageLoader("shacl2md"),
        autoescape=select_autoescape(),
        trim_blocks=True,
    )

    template = env.get_template("template.md.jinja")

    print(
        template.render(
            doc=get_doc(g),
            namespaces=g.namespace_manager.namespaces(),
            properties=get_properties(g),
            classes=get_classes(g),
            authors=get_authors(g),
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "files",
        metavar="inputFile",
        nargs="+",
        help="SHACL OR RDFS files to construct Markdown documentation of.",
    )
    args = parser.parse_args()
    # print(args.accumulate(args.files))
    main(args)
