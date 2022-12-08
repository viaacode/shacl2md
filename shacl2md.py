import argparse
import os
from itertools import groupby

from jinja2 import Environment, PackageLoader, select_autoescape
from lxml import etree
from plantuml import PlantUML
from rdflib.graph import Graph
from rdflib.namespace import Namespace
from rdflib.term import Literal

from queries import (GET_AUTHORS, GET_CLASSES, GET_DATATYPES, GET_DOC_MD,
                     GET_PROPERTIES, GET_SUBCLASSES, GET_SUPERCLASSES,
                     GET_VALUES)

SHACL = Namespace("http://www.w3.org/ns/shacl#")

env = Environment(
    loader=PackageLoader("shacl2md"),
    autoescape=select_autoescape(),
    trim_blocks=True,
)

template = env.get_template("template.md.jinja")
puml_template = env.get_template("diagram.puml.jinja")


def to_shortname(g, term):
    return term.n3(g.namespace_manager) if term is not None else ""


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
            # "superclasses": list(get_superclasses(g, parent.iri, lang)),
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
    def iri_func(p):
        return p['iri']
    for c in g.query(GET_CLASSES, initBindings={"lang": Literal(lang)}):
        ungrouped_properties = list(get_properties(g, c.iri, lang))
        properties = []
        for prop_iri, prop_shapes in groupby(ungrouped_properties, key=iri_func):
            prop_shapes = list(prop_shapes)
            property = prop_shapes[0]
            for prop in prop_shapes:
                for key in prop:
                    if prop[key] != property[key] and prop[key] and property[key]:
                        print(prop_iri, key, prop[key], property[key])
                        properties.append(prop)
                    elif not property[key] and prop[key]:
                        property[key] = prop[key]
            properties.append(property)
        yield {
            "iri": c.iri,
            "shortname": to_shortname(g, c.iri),
            "label": c.label,
            "description": c.description,
            "properties": properties,
            "superclasses": list(get_superclasses(g, c.iri, lang)),
            "subclasses": list(get_subclasses(g, c.iri, lang)),
        }


def get_datatypes(g, s, lang):
    for dt in g.query(GET_DATATYPES, initBindings={"lang": Literal(lang), "shape": s}):
        yield {
            "iri": dt.iri,
            "label": dt.label,
            "shortname": to_shortname(g, dt.iri),
            "type": dt.type.toPython(),
        }


def get_values(g, s, lang):
    for v in g.query(GET_VALUES, initBindings={"lang": Literal(lang), "shape": s}):
        yield {
            "iri": v.iri,
            "label": v.label,
            "shortname": to_shortname(g, v.iri),
        }


def get_properties(g, c, lang):
    qres = g.query(
        GET_PROPERTIES, initBindings={"lang": Literal(lang), "targetClass": c}
    )
    for row in qres:
        datatypes = list(get_datatypes(g, row.shape, lang))
        values = list(get_values(g, row.shape, lang))
        if (not len(datatypes) > 0) and row.kind == SHACL.IRI:
            datatypes = [
                {
                    "iri": "https://www.rfc-editor.org/rfc/rfc3987.txt",
                    "shortname": "IRI",
                }
            ]
        result = {
            "iri": row.iri,
            "shortname": to_shortname(g, row.iri),
            "label": row.label,
            "description": row.description,
            "min": row.min,
            "max": row.max,
            "datatypes": datatypes,
            "value_list": values,
        }
        yield result


def main(args):
    # TODO: from rdflib 6.1.2, use bind_namespaces="none"
    g = Graph(bind_namespaces="none")
    for file in args.files:
        g.parse(file)

    print(f"Creating {args.name}")
    print("-----------------------------------------------")

    if args.validate:
        from pyshacl import validate

        r = validate(
            g,
            shacl_graph="http://www.w3.org/ns/shacl-shacl",
            abort_on_first=False,
            allow_infos=True,
            allow_warnings=True,
        )
        conforms, results_graph, results_text = r

        print(f"* {results_text}")

        if not conforms:
            quit()

    for lang in args.language:
        generate(g, args, lang)


def generate(g, args, lang):
    doc = get_doc(g, lang)

    # decide on output dir
    output_dir = args.out
    if args.vdir:
        output_dir = f"{args.out}/{doc.version}"
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        print(f"* Directory '{output_dir}' created")

    output_dir = f"{output_dir}/{args.name}/{lang}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print(f"* Directory '{output_dir}' created")

    namespaces = g.namespace_manager.namespaces()
    classes = list(get_classes(g, lang=lang))

    puml_filename = f"{args.name}-diagram.puml"
    svg_filename = f"{args.name}-diagram.svg"

    # Generate PUML diagram
    print(
        puml_template.render(
            namespaces=namespaces,
            classes=classes,
        ),
        file=open(f"{output_dir}/{puml_filename}", "w"),
    )
    print(f"* File '{output_dir}/{puml_filename}' created")

    # Render PUML diagram
    pl = PlantUML("http://www.plantuml.com/plantuml/svg/")
    pl.processes_file(
        f"{output_dir}/{puml_filename}", directory=output_dir, outfile=svg_filename
    )
    print(f"* File '{output_dir}/{svg_filename}' created")

    if args.nodocs:
        return

    # Extract PUML SVG string
    parser = etree.XMLParser(ns_clean=True, remove_comments=True)
    tree = etree.parse(f"{output_dir}/{svg_filename}", parser)
    tree.getroot().attrib.pop("width")
    tree.getroot().attrib.pop("height")
    tree.getroot().attrib.pop("style")
    svg_text = etree.tostring(tree.getroot(), encoding="unicode", xml_declaration=False)

    # Dump RDF serialization to file
    rdf_filename = f"{args.name}.shacl.ttl"
    g.serialize(f"{output_dir}/{rdf_filename}")
    print(f"* File '{output_dir}/{rdf_filename}' created")

    other_languages = list(args.language)
    other_languages.remove(lang)

    print(
        template.render(
            frontmatter={
                "layout": args.layout,
                "title": doc.title,
                "parent": args.parent,
                "nav_order": args.nav_order,
                "nav_exclude": args.language[0] != lang
            },
            rdf_filename=rdf_filename,
            doc=doc,
            namespaces=namespaces,
            classes=classes,
            diagramText=svg_text,
            languages=other_languages,
        ),
        file=open(f"{output_dir}/index.md", "w"),
    )
    print(f"* File '{output_dir}/index.md' created")


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
        nargs="*",
        required=False,
        help='languages of generated documentation, default is "nl"',
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
        "--parent",
        metavar="parent",
        type=str,
        required=False,
        default="index",
        help='Jekyll parent page, default is "index"',
    )
    parser.add_argument(
        "--layout",
        metavar="layout",
        type=str,
        required=False,
        default="default",
        help='Jekyll layout, default is "default"',
    )
    parser.add_argument(
        "--nav_order",
        metavar="nav_order",
        type=int,
        required=False,
        default=1,
        help="Jekyll nav order, default is 1",
    )
    parser.add_argument(
        "--name",
        metavar="name",
        type=str,
        default="output",
        required=False,
        help='filename for the output file, default is "output"',
    )
    parser.add_argument(
        "--vdir",
        action="store_true",
        help="if present, outputs files to a directory based on the SHACL version",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="if present, the shacl file is validated against the SHACL-SHACL.",
    )
    parser.add_argument(
        "--nodocs",
        action="store_true",
        help="if present, only a diagram is produced.",
    )
    argsv = parser.parse_args()
    main(argsv)
