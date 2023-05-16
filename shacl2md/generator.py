import argparse
import os
from itertools import groupby
from typing import List

from jinja2 import Environment, PackageLoader, select_autoescape
from lxml import etree
from plantuml import PlantUML
from pyshacl import validate
from rdflib.graph import Graph, URIRef
from rdflib.namespace import Namespace
from rdflib.term import Literal

from shacl2md.utilities.lang_labels import get_lang_labels
from shacl2md.utilities.queries import (CLASS_EXISTS_CHECK, GET_AUTHORS,
                                        GET_CLASS, GET_CLASSES, GET_DATATYPES,
                                        GET_DOC_MD, GET_PROPERTIES,
                                        GET_SUBCLASSES, GET_SUPERCLASSES,
                                        GET_VALUES)
from shacl2md.utilities.rdf import RDFClass, to_shortname

SHACL = Namespace("http://www.w3.org/ns/shacl#")

env = Environment(
    loader=PackageLoader("shacl2md"),
    autoescape=select_autoescape(),
    trim_blocks=True,
)

template = env.get_template("template.md.jinja")
puml_template = env.get_template("diagram.puml.jinja")





class ShaclMarkdownGenerator: 

    def __init__(
        self,
        languages : List[str], 
        output_dir : str= "./", 
        shacl_shacl_validation : bool = False,
        version_directory : bool = False, 
        crosslink_between_graphs : bool = False,
        jekyll_parent_page : str = "index",
        jekyll_layout : str = "default",
        jekyll_nav_order : int = 1,
        ontology_graphs : List[str] = [],
        ):
        """
        A shacl markdown generator object.

        Args:
            languages (List[str]): List of languages to generate documentation for.
            output_dir (str, optional): Output directory. Defaults to "./".
            shacl_shacl_validation (bool, optional): Validate the SHACL files against the SHACL specification. Defaults to False.
            version_directory (bool, optional): Create a version directory. Defaults to False.
            crosslink_between_graphs (bool, optional): Crosslink between graphs. Defaults to True.
            jekyll_parent_page (str, optional): Jekyll parent page. Defaults to "index".
            jekyll_layout (str, optional): Jekyll layout. Defaults to "default".
            jekyll_nav_order (int, optional): Jekyll nav order. Defaults to 1.
            ontology_graphs (List[str], optional): List of ontology files to include with the SHACL shapes, e.g., class definitions or reasoning. Defaults to [].
        """

        self.languages : List[str] = languages
        self.output_dir : str = output_dir
        self.shacl_shacl_validation : bool = shacl_shacl_validation
        self.version_directory : bool = version_directory
        self.crosslink_between_graphs : bool = crosslink_between_graphs
        self.jekyll_parent_page : str = jekyll_parent_page
        self.jekyll_layout : str = jekyll_layout
        self.jekyll_nav_order : int = jekyll_nav_order            

        self.graphs :  dict = {}
        self.ontology_graph : Graph = Graph(identifier="ontology_graph", bind_namespaces="none")
        for ontology_graph in ontology_graphs:
            self.ontology_graph.parse(ontology_graph)

    def get_graph(self, name: str):
        """
        Get a graph by name.

        Args:
            name (str): Name of the graph to get.
        """
        return self.graphs[name]

    def get_other_languages(self, lang: str):
        """
        Get all other languages.

        Args:
            lang (str): language to filter
        """
        return list(filter(lambda l: l != lang, self.languages))

    def get_other_graphs(self, name: str):
        """
        Get all other graphs.

        Args:
            name (str): Name of the graph to filter.
        """
        return [g for n, g in self.graphs.items() if n != name]

    def generate(
        self, 
        **shacls) -> None:
        """
        Generate markdown documentation from SHACL files.

        Args:
            **shacls: Dictionary of SHACL files to generate documentation for. The key is the name of the SHACL graph, the value is the filename of the SHACL file.

        Raises:
            ValidationFailure (pyshacl.errors.ValidationFailure): Raised when the SHACL files do not validate against the SHACL specification.
        """

        # check if shacl-shacl validation is required

        shacl_graphs : List[ShaclGraph] = []
        # parse shacl files to graphs
        for shacl, shacl_filename in shacls.items():
            g = Graph(identifier=shacl, bind_namespaces="none")
            g.parse(shacl_filename)
            self.graphs[shacl] = g

            for lang in self.languages:
                shacl_graph = ShaclGraph(
                    shacl,
                    lang,
                    self
                )
                shacl_graphs.append(shacl_graph)
                if self.shacl_shacl_validation:
                    shacl_graph.validate()
        
        for shacl_graph in shacl_graphs:
            shacl_graph.generate_md()

                
class ShaclGraph:

    def __init__(
        self,
        name: str,
        lang : str,
        generator : ShaclMarkdownGenerator,
    ):
        """
        A shacl graph object.

        Args:
            graph (Graph): The SHACL graph.
            name (str): The name of the SHACL graph.
            lang (str): The language of the SHACL graph.
            base_output_dir (str): The base output directory.
            version_directory (bool): Create a version directory.
            crosslink_graphs (List[Graph], optional): List of graphs to crosslink to. Defaults to [].
        """
        self.name = name
        self.lang = lang
        self.generator = generator
        self.graph : Graph = generator.get_graph(name)
        self.graph += generator.ontology_graph
        self.doc = self._get_doc()
        self.output_dir, self.output_dir_length = self._generate_output_dir()
        self.namespaces = self.graph.namespace_manager.namespaces()
        self.classes = list(self._get_classes())

    def generate_puml(self):
        """
        Generate a PlantUML diagram from the SHACL graph.
        """
        puml_filename = f"{self.name}-diagram.puml"
        svg_filename = f"{self.name}-diagram.svg"

        # Generate PUML diagram
        print(
            puml_template.render(
                namespaces=self.namespaces,
                classes=self.classes,
                output_dir_length=self.output_dir_length,
            ),
            file=open(f"{self.output_dir}/{puml_filename}", "w"),
        )
        print(f"* File '{self.output_dir}/{puml_filename}' created")

        # Render PUML diagram
        pl = PlantUML("http://www.plantuml.com/plantuml/svg/")
        try:
            pl.processes_file(
                f"{self.output_dir}/{puml_filename}", directory=self.output_dir, outfile=svg_filename
            )
            print(f"* File '{self.output_dir}/{svg_filename}' created")
        except:
            print(f"* File '{self.output_dir}/{svg_filename}' not created due to PlantUML error")

        # Extract PUML SVG string
        parser = etree.XMLParser(ns_clean=True, remove_comments=True)
        tree = etree.parse(f"{self.output_dir}/{svg_filename}", parser)
        tree.getroot().attrib.pop("width")
        tree.getroot().attrib.pop("height")
        tree.getroot().attrib.pop("style")
        svg_text = etree.tostring(tree.getroot(), encoding="unicode", xml_declaration=False)
        return svg_text

    def generate_md(self):
        """
        Generate markdown documentation from the SHACL graph.
        """
        svg_text = self.generate_puml()
        # Dump RDF serialization to file
        rdf_filename = f"{self.name}.shacl.ttl"
        self.graph.serialize(f"{self.output_dir}/{rdf_filename}")
        print(f"* File '{self.output_dir}/{rdf_filename}' created")

        other_languages = self.generator.get_other_languages(self.lang)

        # Get markdown labels
        labels = get_lang_labels(self.lang)

        print(
            template.render(
                frontmatter={
                    "layout": self.generator.jekyll_layout,
                    "title": self.doc.title,
                    "parent": self.generator.jekyll_parent_page,
                    "nav_order": self.generator.jekyll_nav_order,
                    "nav_exclude": self.generator.languages[0] != self.lang,
                },
                rdf_filename=rdf_filename,
                doc=self.doc,
                namespaces=self.namespaces,
                classes=self.classes,
                diagramText=svg_text,
                languages=other_languages,
                output_dir_length=self.output_dir_length,
                labels=labels,
            ),
            file=open(f"{self.output_dir}/index.md", "w"),
        )
        print(f"* File '{self.output_dir}/index.md' created")

    def _get_classes(self):
        crosslink_graphs = []
        if self.generator.crosslink_between_graphs:
            crosslink_graphs = self.generator.get_other_graphs(self.name)
        for c in self.graph.query(GET_CLASSES, initBindings={"lang": Literal(self.lang)}):
            c = RDFClass(self.lang, c.iri, to_shortname(self.graph, c.iri), c.label, c.description)
            c.check_crosslink(self.graph, crosslink_graphs)
            c.get_properties(self.graph, crosslink_graphs)
            c.get_subclasses(self.graph)
            c.get_superclasses(self.graph)
            yield c.to_dict()

    def _generate_output_dir(self):
        base_output_dir = self.generator.output_dir
        version_directory = self.generator.version_directory
        output_dir_length = 1
        if version_directory:
            if self.doc is None or self.doc.version is None:
                print("* Version info not found; outputting in main directory.")
                output_dir = base_output_dir
            else:
                output_dir = f"{base_output_dir}/{self.doc.version}"

            if not os.path.exists(base_output_dir):
                os.mkdir(base_output_dir)
            print(f"* Directory '{base_output_dir}' created")
            output_dir_length += 1

        output_dir = f"{output_dir}/{self.graph.identifier}/{self.lang}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        print(f"* Directory '{output_dir}' created")
        return output_dir, output_dir_length

    def _get_doc(self):
        for row in self.graph.query(GET_DOC_MD, initBindings={"lang": Literal(self.lang)}):
            row.authors = list(self.graph.query(GET_AUTHORS))
            return row

    def validate(self):
        """
        Validate the SHACL graph against the SHACL specification.
        """
        r = validate(
                self.graph,
                shacl_graph="http://www.w3.org/ns/shacl-shacl",
                abort_on_first=True,
                allow_infos=True,
                allow_warnings=True,
            )
        conforms, results_graph, results_text = r
        print(f"* {results_text}")
