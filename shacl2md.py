import argparse
import os
from itertools import groupby
from typing import List

from jinja2 import Environment, PackageLoader, select_autoescape
from lxml import etree
from plantuml import PlantUML
from rdflib.graph import Graph
from rdflib.namespace import Namespace
from rdflib.term import Literal

from queries import (
    CLASS_EXISTS_CHECK,
    GET_AUTHORS,
    GET_CLASS,
    GET_CLASSES,
    GET_DATATYPES,
    GET_DOC_MD,
    GET_PROPERTIES,
    GET_SUBCLASSES,
    GET_SUPERCLASSES,
    GET_VALUES,
)
from lang_labels import get_lang_labels
SHACL = Namespace("http://www.w3.org/ns/shacl#")

env = Environment(
    loader=PackageLoader("shacl2md"),
    autoescape=select_autoescape(),
    trim_blocks=True,
)

template = env.get_template("template.md.jinja")
puml_template = env.get_template("diagram.puml.jinja")


class RDFClass:
    def __init__(
        self,
        lang: str,
        iri,
        shortname,
        label=None,
        description=None,
    ):
        self.lang: str = lang
        self.iri: str = iri
        self.shortname = shortname
        self.label = label
        self.description = description
        self.properties = []
        self.subclasses = []
        self.superclasses = []
        self.type = "class"
        self.crosslink = None

    def get_superclasses(
        self,
        g: Graph,
    ):
        def get_superclasses_generator():
            for parent in g.query(
                GET_SUPERCLASSES,
                initBindings={"lang": Literal(self.lang), "child": self.iri},
            ):
                super_class = RDFClass(
                    self.lang,
                    parent.iri,
                    to_shortname(g, parent.iri),
                    parent.label,
                    parent.description,
                )
                super_class.get_properties(g)
                yield super_class

        self.superclasses = list(get_superclasses_generator())

    def get_subclasses(
        self,
        g: Graph,
    ):
        def get_subclasses_generator():
            for child in g.query(
                GET_SUBCLASSES,
                initBindings={"lang": Literal(self.lang), "parent": self.iri},
            ):
                sub_class = RDFClass(
                    self.lang,
                    child.iri,
                    to_shortname(g, child.iri),
                    child.label,
                    child.description,
                )
                yield sub_class

        self.subclasses = list(get_subclasses_generator())

    def get_properties(self, g: Graph, g_crosslinks: List[Graph] = []):
        def get_properties_generator():
            for prop in g.query(
                GET_PROPERTIES,
                initBindings={"lang": Literal(self.lang), "targetClass": self.iri},
            ):
                property = RDFProperty(
                    prop.iri,
                    to_shortname(g, prop.iri),
                    prop.label,
                    prop.description,
                    prop.min,
                    prop.max,
                )
                property.get_datatypes(g, prop.shape, self.lang, g_crosslinks)
                if not property.datatypes and prop.kind == SHACL.IRI:
                    property.datatypes = [
                        RDFDatatype(
                            "https://www.rfc-editor.org/rfc/rfc3987.txt", "IRI", "IRI"
                        )
                    ]
                property.get_values(g, prop.shape, self.lang)
                yield property

        self.properties = list(get_properties_generator())

    def get_class_info(
        self,
        g: Graph,
    ):
        for row in g.query(
            GET_CLASS, initBindings={"lang": Literal(self.lang), "iri": self.iri}
        ):
            self.label = row.label
            self.description = row.description

    def check_crosslink(self, g: Graph, g_crosslinks: List[Graph] = []):
        class_exists = g.query(
            CLASS_EXISTS_CHECK, initBindings={"iri": self.iri}
        ).askAnswer
        if g_crosslinks and (not class_exists or not self.label):
            for graph in g_crosslinks:
                if graph.query(
                    CLASS_EXISTS_CHECK, initBindings={"iri": self.iri}
                ).askAnswer:
                    if not class_exists:
                        self.crosslink = graph.identifier
                    self.get_class_info(graph)

    # deep copy method
    def copy(self):
        copy_class = RDFClass(
            self.lang, self.iri, self.shortname, self.label, self.description
        )
        copy_class.properties = [prop.copy() for prop in self.properties]
        copy_class.subclasses = [sub.copy() for sub in self.subclasses]
        copy_class.superclasses = [sup.copy() for sup in self.superclasses]
        return copy_class

    def to_dict(self):
        return {
            "lang": self.lang,
            "iri": self.iri,
            "shortname": self.shortname,
            "label": self.label,
            "description": self.description,
            "properties": [prop.to_dict() for prop in self.properties],
            "subclasses": [sub.to_dict() for sub in self.subclasses],
            "superclasses": [sup.to_dict() for sup in self.superclasses],
            "type": self.type,
            "crosslink": self.crosslink,
        }


class RDFProperty:
    def __init__(
        self,
        iri,
        shortname,
        label,
        description,
        min,
        max,
    ):
        self.iri = iri
        self.shortname = shortname
        self.label = label
        self.description = description
        self.min = min
        self.max = max
        self.datatypes = []
        self.value_list = []

    def get_datatypes(self, g: Graph, s, lang: str, g_crosslinks: List[Graph] = []):
        def get_datatypes_generator():
            for dt in g.query(
                GET_DATATYPES, initBindings={"lang": Literal(lang), "shape": s}
            ):
                if dt.type.toPython() == "datatype":
                    yield RDFDatatype(
                        dt.iri,
                        to_shortname(g, dt.iri),
                        dt.label,
                    )
                elif dt.type.toPython() == "class":
                    dt_class = RDFClass(lang, dt.iri, to_shortname(g, dt.iri), dt.label)
                    dt_class.check_crosslink(g, g_crosslinks)
                    yield dt_class

        self.datatypes = list(get_datatypes_generator())

    def get_values(self, g: Graph, s, lang: str):
        def get_values_generator():
            for value in g.query(
                GET_VALUES, initBindings={"lang": Literal(lang), "shape": s}
            ):
                yield RDFValue(
                    value.iri,
                    to_shortname(g, value.iri),
                    value.label,
                )

        self.value_list = list(get_values_generator())

    def copy(self):
        copy_prop = RDFProperty(
            self.iri,
            self.shortname,
            self.label,
            self.description,
            self.min,
            self.max,
        )
        copy_prop.datatypes = [dt.copy() for dt in self.datatypes]
        copy_prop.value_list = [value.copy() for value in self.value_list]

    def to_dict(self):
        return {
            "iri": self.iri,
            "shortname": self.shortname,
            "label": self.label,
            "description": self.description,
            "min": self.min,
            "max": self.max,
            "datatypes": [dt.to_dict() for dt in self.datatypes],
            "value_list": [value.to_dict() for value in self.value_list],
        }


class RDFDatatype:
    def __init__(
        self,
        iri,
        shortname,
        label,
    ):
        self.iri = iri
        self.shortname = shortname
        self.label = label
        self.type = "datatype"

    def copy(self):
        copy_dt = RDFDatatype(self.iri, self.shortname, self.label)
        return copy_dt

    def to_dict(self):
        return {
            "iri": self.iri,
            "shortname": self.shortname,
            "label": self.label,
            "type": self.type,
        }


class RDFValue:
    def __init__(
        self,
        iri,
        shortname,
        label,
    ):
        self.iri = iri
        self.shortname = shortname
        self.label = label

    def copy(self):
        copy_value = RDFValue(self.iri, self.shortname, self.label)
        return copy_value

    def to_dict(self):
        return {
            "iri": self.iri,
            "shortname": self.shortname,
            "label": self.label,
        }


def to_shortname(g: Graph, term):
    return term.n3(g.namespace_manager) if term is not None else ""


def get_doc(g: Graph, lang: str):
    for row in g.query(GET_DOC_MD, initBindings={"lang": Literal(lang)}):
        row.authors = list(g.query(GET_AUTHORS))
        return row


def get_classes(g: Graph, lang: str, g_crosslinks: List[Graph]):
    for c in g.query(GET_CLASSES, initBindings={"lang": Literal(lang)}):
        c = RDFClass(lang, c.iri, to_shortname(g, c.iri), c.label, c.description)
        c.check_crosslink(g, g_crosslinks)
        c.get_properties(g, g_crosslinks)
        c.get_subclasses(g)
        c.get_superclasses(g)
        yield c.to_dict()


def get_crosslink_graphs(crosslinks):
    for crosslink in crosslinks:
        crosslink_name, *crosslink_files = crosslink.split("=")
        g_crosslink = Graph(identifier=crosslink_name)
        for crosslink_file in crosslink_files[0].split(","):
            g_crosslink.parse(crosslink_file)
        yield g_crosslink


def get_output_dir(args, lang: str, doc):
    output_dir = args.out
    output_dir_length = 1
    if args.vdir:
        output_dir = f"{args.out}/{doc.version}"
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        print(f"* Directory '{output_dir}' created")
        output_dir_length += 1

    output_dir = f"{output_dir}/{args.name}/{lang}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print(f"* Directory '{output_dir}' created")
    return output_dir, output_dir_length


def generate_puml(args, output_dir, output_dir_length, namespaces, classes):
    puml_filename = f"{args.name}-diagram.puml"
    svg_filename = f"{args.name}-diagram.svg"

    # Generate PUML diagram
    print(
        puml_template.render(
            namespaces=namespaces,
            classes=classes,
            output_dir_length=output_dir_length,
        ),
        file=open(f"{output_dir}/{puml_filename}", "w"),
    )
    print(f"* File '{output_dir}/{puml_filename}' created")

    # Render PUML diagram
    pl = PlantUML("http://www.plantuml.com/plantuml/svg/")
    try:
        pl.processes_file(
            f"{output_dir}/{puml_filename}", directory=output_dir, outfile=svg_filename
        )
        print(f"* File '{output_dir}/{svg_filename}' created")
    except:
        print(f"* File '{output_dir}/{svg_filename}' not created due to PlantUML error")

    if args.nodocs:
        return None

    # Extract PUML SVG string
    parser = etree.XMLParser(ns_clean=True, remove_comments=True)
    tree = etree.parse(f"{output_dir}/{svg_filename}", parser)
    tree.getroot().attrib.pop("width")
    tree.getroot().attrib.pop("height")
    tree.getroot().attrib.pop("style")
    svg_text = etree.tostring(tree.getroot(), encoding="unicode", xml_declaration=False)
    return svg_text


def generate_md(
    args, g, output_dir, output_dir_length, lang, doc, namespaces, classes, svg_text
):
    # Dump RDF serialization to file
    rdf_filename = f"{args.name}.shacl.ttl"
    g.serialize(f"{output_dir}/{rdf_filename}")
    print(f"* File '{output_dir}/{rdf_filename}' created")

    other_languages = list(args.language)
    other_languages.remove(lang)

    # Get markdown labels
    labels = get_lang_labels(lang)

    print(
        template.render(
            frontmatter={
                "layout": args.layout,
                "title": doc.title,
                "parent": args.parent,
                "nav_order": args.nav_order,
                "nav_exclude": args.language[0] != lang,
            },
            rdf_filename=rdf_filename,
            doc=doc,
            namespaces=namespaces,
            classes=classes,
            diagramText=svg_text,
            languages=other_languages,
            output_dir_length=output_dir_length,
            labels=labels,
        ),
        file=open(f"{output_dir}/index.md", "w"),
    )
    print(f"* File '{output_dir}/index.md' created")


def generate(g: Graph, g_crosslinks: List[Graph], args, lang: str):
    doc = get_doc(g, lang)

    # decide on output dir
    output_dir, output_dir_length = get_output_dir(args, lang, doc)

    namespaces = g.namespace_manager.namespaces()

    classes = list(get_classes(g, lang, g_crosslinks))

    svg_text = generate_puml(args, output_dir, output_dir_length, namespaces, classes)
    if svg_text:
        generate_md(
            args,
            g,
            output_dir,
            output_dir_length,
            lang,
            doc,
            namespaces,
            classes,
            svg_text,
        )


def main(args):
    # TODO: from rdflib 6.1.2, use bind_namespaces="none"
    g = Graph(bind_namespaces="none")
    for file in args.files:
        g.parse(file)

    print(f"Creating {args.name}")
    print("-----------------------------------------------")

    if args.crosslinks:
        g_crosslinks = list(get_crosslink_graphs(args.crosslinks))
    else:
        g_crosslinks = []

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
        generate(g, g_crosslinks, args, lang)


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
        default=["nl"],
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
        "--crosslinks",
        metavar="crosslinks",
        type=str,
        nargs="*",
        required=False,
        help='crosslink graphs to find classes in: format is "name1=file1,file2,...  name2=file1,file2,..."',
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
