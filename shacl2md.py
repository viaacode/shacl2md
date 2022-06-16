import argparse

from jinja2 import Environment, PackageLoader, select_autoescape
from rdflib.graph import Graph
from rdflib.namespace import DCTERMS, FOAF, OWL, RDF, RDFS, SKOS, Namespace
from rdflib.term import BNode, Literal, URIRef
from util import to_local_name, to_label, to_shortname

from queries import (GET_AUTHORS, GET_CLASSES, GET_DOC_MD, GET_PROPERTIES, GET_SUBCLASSES, GET_SUPERCLASSES)

SHACL = Namespace("http://www.w3.org/ns/shacl#")


def get_doc(g, lang):
    for row in g.query(GET_DOC_MD, initBindings={"lang": Literal(lang)}):
        row.authors = list(get_authors(g))
        return row

def extract(g, row):
    return {
        "iri": row.iri,
        "shortname": to_shortname(g, row.iri),
        "label": to_label(g, row.iri),
        "description": row.description
    }

def get_classes(g, lang):
    classes = []
    for row in g.query(GET_CLASSES, initBindings={"lang": Literal(lang)}):
        classes.append(extract(g, row))
        # add properties to class 
        classes[-1]["properties"] = list(get_properties(g, row.iri, lang))

        # parent property that class GET_SUPERCLASS query from g and adds shortname
        classes[-1]["superclasses"] = []
        classes[-1]["subclasses"] = []
        for parent in g.query(GET_SUPERCLASSES, initBindings={"lang": Literal(lang), "child": row.iri}):
            
            classes[-1]["superclasses"].append(extract(g, parent))
            # print(list(get_properties(g, parent.iri)))
            classes[-1]["properties"].extend(list(get_properties(g, parent.iri, lang)))
        for child in g.query(GET_SUBCLASSES, initBindings={"lang": Literal(lang), "parent": row.iri}):
            classes[-1]["subclasses"].append(extract(g, child))
    return classes

def get_properties(g, c, lang):
    properties = []
    qres = g.query(GET_PROPERTIES, initBindings={"lang": Literal(lang), "targetClass": c})
    for row in qres:
        properties.append(extract(g, row))
        if row.get("datatype"):
            properties[-1]["datatype"] = {
                "label": to_label(g,row.datatype),
                "iri": row.datatype,
                "shortname": to_shortname(g,row.datatype),
            }
            if bool(row.thesaurus):
                properties[-1]["datatype"]["thesaurus"] = row.thesaurus
            properties[-1]["min"] = row.min
            properties[-1]["max"] = row.max
        elif row.get("classtype"):
            properties[-1]["classtype"] = {
                "label": row.classtype_label,
                "iri": row.classtype,
                "shortname": row.classtype.n3(g.namespace_manager),
            }
            properties[-1]["min"] = row.min
            properties[-1]["max"] = row.max
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
    lang = args.language
    # print(lang)
    print(
        template.render(
            doc=get_doc(g, lang),
            namespaces=g.namespace_manager.namespaces(),
            classes=get_classes(g, lang=lang),
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
    parser.add_argument(
       "--language",
        metavar="language",
        type=str,
        default="nl",
        required=False,
        help="language of generated documentation, default is \"nl\"",
    )
    args = parser.parse_args()
    # print(args.accumulate(args.files))
    main(args)