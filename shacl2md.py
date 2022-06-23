import argparse

from jinja2 import Environment, PackageLoader, select_autoescape
from rdflib.graph import Graph
from rdflib.namespace import Namespace
from rdflib.term import Literal
from util import to_label, to_shortname

from queries import (
    GET_AUTHORS,
    GET_CLASSES,
    GET_DOC_MD,
    GET_PROPERTIES,
    GET_SUBCLASSES,
    GET_SUPERCLASSES,
)

SHACL = Namespace("http://www.w3.org/ns/shacl#")


def get_doc(g, lang):
    for row in g.query(GET_DOC_MD, initBindings={"lang": Literal(lang)}):
        row.authors = list(g.query(GET_AUTHORS))
        return row


def get_superclasses(g, c, lang):
    for parent in g.query(
        GET_SUPERCLASSES, initBindings={"lang": Literal(lang), "child": c}
    ):
        yield {
            "iri": parent.iri,
            "shortname": to_shortname(g, parent.iri),
            "label": to_label(g, parent.iri),
            "description": parent.description,
            "properties": list(get_properties(g, parent.iri, lang)),
        }


def get_subclasses(g, c, lang):
    for child in g.query(
        GET_SUBCLASSES, initBindings={"lang": Literal(lang), "parent": c}
    ):
        yield {
            "iri": child.iri,
            "shortname": to_shortname(g, child.iri),
            "label": to_label(g, child.iri),
            "description": child.description,
        }


def get_classes(g, lang):
    for c in g.query(GET_CLASSES, initBindings={"lang": Literal(lang)}):
        yield {
            "iri": c.iri,
            "shortname": to_shortname(g, c.iri),
            "label": to_label(g, c.iri),
            "description": c.description,
            "properties": list(get_properties(g, c.iri, lang)),
            "superclasses": list(get_superclasses(g, c.iri, lang)),
            "subclasses": list(get_subclasses(g, c.iri, lang)),
        }


def get_properties(g, c, lang):
    qres = g.query(
        GET_PROPERTIES, initBindings={"lang": Literal(lang), "targetClass": c}
    )
    for row in qres:
        result = {
            "iri": row.iri,
            "shortname": to_shortname(g, row.iri),
            "label": to_label(g, row.iri),
            "description": row.description,
            "min": row.min,
            "max": row.max,
        }
        if row.get("datatype"):
            result["datatype"] = {
                "label": to_label(g, row.datatype),
                "iri": row.datatype,
                "shortname": to_shortname(g, row.datatype),
            }
            if bool(row.thesaurus):
                result["thesaurus"] = row.thesaurus

        elif row.get("classtype"):
            result["classtype"] = {
                "label": row.classtype_label,
                "iri": row.classtype,
                "shortname": to_shortname(g, row.classtype),
            }
        yield result


def main(args):
    g = Graph()
    for file in args.files:
        g.parse(file)
    env = Environment(
        loader=PackageLoader("shacl2md"),
        autoescape=select_autoescape(),
        trim_blocks=True,
    )

    lang = args.language
    doc = get_doc(g, lang)
    namespaces = g.namespace_manager.namespaces()
    classes = list(get_classes(g, lang=lang))

    # print puml
    template = env.get_template("template.md.jinja")
    puml_template = env.get_template("diagram.puml.jinja")

    print(
        puml_template.render(
            namespaces=namespaces,
            classes=classes,
        ),
        file=open("output.puml", "w"),
    )

    print(
        template.render(
            doc=doc,
            namespaces=namespaces,
            classes=classes,
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
    parser.add_argument(
        "--language",
        metavar="language",
        type=str,
        default="nl",
        required=False,
        help='language of generated documentation, default is "nl"',
    )
    argsv = parser.parse_args()
    # print(argsv.accumulate(args.files))
    main(argsv)
