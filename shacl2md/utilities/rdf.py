import json
from typing import List

from rdflib.graph import Graph
from rdflib.namespace import Namespace
from rdflib.term import Literal

from shacl2md.utilities.queries import (
    CLASS_EXISTS_CHECK,
    GET_CLASS,
    GET_DATATYPES,
    GET_PROPERTIES,
    GET_SUBCLASSES,
    GET_SUPERCLASSES,
    GET_VALUES,
)

SHACL = Namespace("http://www.w3.org/ns/shacl#")


def to_shortname(g: Graph, term):
    return term.n3(g.namespace_manager) if term is not None else ""


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
        self.label = label if label is not None else shortname.split(":", 1)[1]
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
                    prop.uniqueLang,
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

    # # deep copy method
    # def copy(self):
    #     copy_class = RDFClass(
    #         self.lang, self.iri, self.shortname, self.label, self.description
    #     )
    #     copy_class.properties = [prop.copy() for prop in self.properties]
    #     copy_class.subclasses = [sub.copy() for sub in self.subclasses]
    #     copy_class.superclasses = [sup.copy() for sup in self.superclasses]
    #     return copy_class

    def to_dict(self) -> dict:
        return json.loads(json.dumps(self, default=lambda o: o.__dict__))


class RDFProperty:
    def __init__(
        self,
        iri,
        shortname,
        label,
        description,
        min,
        max,
        uniqueLang,
    ):
        self.iri = iri
        self.shortname = shortname
        self.label = label
        self.description = description
        self.min = min
        self.max = max
        self.uniqueLang = uniqueLang
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

    # def copy(self):
    #     copy_prop = RDFProperty(
    #         self.iri,
    #         self.shortname,
    #         self.label,
    #         self.description,
    #         self.min,
    #         self.max,
    #     )
    #     copy_prop.datatypes = [dt.copy() for dt in self.datatypes]
    #     copy_prop.value_list = [value.copy() for value in self.value_list]

    def to_dict(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__))


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
        return json.loads(json.dumps(self, default=lambda o: o.__dict__))


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

    # def copy(self):
    #     copy_value = RDFValue(self.iri, self.shortname, self.label)
    #     return copy_value

    def to_dict(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__))
