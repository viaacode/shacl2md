import argparse
from plantuml import PlantUML

from jinja2 import Environment, PackageLoader, select_autoescape
from rdflib.graph import Graph
from rdflib.namespace import Namespace
from rdflib.term import Literal

from queries import (
    GET_AUTHORS,
    GET_CLASSES,
    GET_DOC_MD,
    GET_PROPERTIES,
    GET_SUBCLASSES,
    GET_SUPERCLASSES,
    GET_DATATYPES,
    GET_VALUES,
)

SHACL = Namespace("http://www.w3.org/ns/shacl#")


def to_shortname(g, term):
    return term.n3(g.namespace_manager)


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
            "label": parent.label,
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
            "label": child.label,
            "description": child.description,
        }


def get_classes(g, lang):
    for c in g.query(GET_CLASSES, initBindings={"lang": Literal(lang)}):
        yield {
            "iri": c.iri,
            "shortname": to_shortname(g, c.iri),
            "label": c.label,
            "description": c.description,
            "properties": list(get_properties(g, c.iri, lang)),
            "superclasses": list(get_superclasses(g, c.iri, lang)),
            "subclasses": list(get_subclasses(g, c.iri, lang)),
        }


def get_datatypes(g, s, lang):
    for dt in g.query(
        GET_DATATYPES, initBindings={"lang": Literal(lang), "shape": s}
    ):
        yield {
            "iri": dt.iri,
            "label": dt.label,
            "shortname": to_shortname(g, dt.iri),
            "type": dt.type.toPython(),
        }

def get_values(g, s, lang):
    for dt in g.query(GET_VALUES, initBindings={"lang": Literal(lang), "shape": s}):
        yield {
            "iri": dt.iri,
            "label": dt.label,
            "shortname": to_shortname(g, dt.iri),
        }


def get_properties(g, c, lang):
    qres = g.query(
        GET_PROPERTIES, initBindings={"lang": Literal(lang), "targetClass": c}
    )
    for row in qres:
        result = {
            "iri": row.iri,
            "shortname": to_shortname(g, row.iri),
            "label": row.label,
            "description": row.description,
            "min": row.min,
            "max": row.max,
            "datatypes": list(get_datatypes(g, row.shape, lang)),
            # "values": list(get_values(g, row.shape, lang))
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

    output_dir = args.out
    puml_filename = f"{args.name}-diagram.puml"
    svg_filename = f"{args.name}-diagram.svg"

    print(
        puml_template.render(
            namespaces=namespaces,
            classes=classes,
        ),
        file=open(f"{output_dir}/{puml_filename}", "w"),
    )

    pl = PlantUML("http://www.plantuml.com/plantuml/svg/")
    pl.processes_file(
        f"{output_dir}/{puml_filename}", directory=output_dir, outfile=svg_filename
    )

    print(
        template.render(
            doc=doc,
            namespaces=namespaces,
            classes=classes,
            diagram=f"{output_dir}/{svg_filename}",
        ),
        file=open(f"{output_dir}/{args.name}.md", "w"),
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
    parser.add_argument(
        "--out",
        metavar="out",
        type=str,
        default="./",
        required=False,
        help='output directory for files, default is "./"',
    )
    parser.add_argument(
        "--name",
        metavar="name",
        type=str,
        default="output",
        required=False,
        help='filename for the output file, default is "output"',
    )
    argsv = parser.parse_args()
    # print(argsv.accumulate(args.files))
    main(argsv)
