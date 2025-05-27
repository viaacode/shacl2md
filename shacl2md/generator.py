import subprocess
import json
import os
from os.path import abspath
from logging import Logger, getLogger, StreamHandler, INFO
from typing import List, Union
import sys

from jinja2 import Environment, PackageLoader, select_autoescape
from lxml import etree
from pyshacl import validate
from rdflib.graph import Graph
from rdflib.namespace import Namespace
from rdflib.term import Literal

from shacl2md.utilities.lang_labels import get_lang_labels
from shacl2md.utilities.queries import GET_AUTHORS, GET_CLASSES, GET_DOC_MD
from shacl2md.utilities.rdf import RDFClass, to_shortname

SHACL = Namespace("http://www.w3.org/ns/shacl#")


class Generator:
    def __init__(
        self,
        languages: List[str],
        output_dir: str = "./",
        shacl_shacl_validation: bool = False,
        ontology_graphs: List[Union[str, Graph]] = None,
        logger: Logger = None,
    ):
        self.output_dir: str = output_dir
        self.shacl_shacl_validation: bool = shacl_shacl_validation
        self.graphs: dict = {}
        self.ontology_graph: Graph = Graph(
            identifier="ontology_graph", bind_namespaces="none"
        )
        if ontology_graphs is None:
            ontology_graphs = []
        for ontology_graph in ontology_graphs:
            self.add_ontology_graph(ontology_graph)
        self.languages: List[str] = languages
        if logger is None:
            self.logger: Logger = getLogger(__name__) 
            # also log to stdout using StreamHandler
            self.logger.setLevel(INFO)
            self.logger.addHandler(StreamHandler(sys.stdout))
        else:
            self.logger: Logger = logger
            

    def add_ontology_graph(self, ontology_graph: Union[str, Graph]):
        """
        Add an ontology graph.

        Args:
            ontology_graph (str | Graph): Ontology graph to add.
        """
        if isinstance(ontology_graph, str):
            self.ontology_graph.parse(ontology_graph)
        elif isinstance(ontology_graph, Graph):
            self.ontology_graph += ontology_graph
            for name, uri in ontology_graph.namespaces():
                self.ontology_graph.bind(name, uri)

    def get_graph(self, graph_name: str):
        """
        Get a graph by name.

        Args:
            graph_name (str): Name of the graph to get.
        """
        return self.graphs[graph_name]

    def add_shacl_graphs(self, **shacls):
        """
        Add SHACL graphs.

        Args:
            **shacls: Dictionary of SHACL files or Graphs to generate documentation for. The key is the name of the SHACL graph, the value is the filename of the SHACL file.
        """
        shacl_graphs: List[ShaclGraph] = []
        # parse shacl files to graphs
        for shacl, shacl_filename_or_graphs in shacls.items():
            g = Graph(identifier=shacl, bind_namespaces="none")
            
            if not isinstance(shacl_filename_or_graphs, list):
                shacl_filename_or_graphs = [shacl_filename_or_graphs]

            for shacl_filename_or_graph in shacl_filename_or_graphs:
                if isinstance(shacl_filename_or_graph, str):
                    g.parse(shacl_filename_or_graph)
                elif isinstance(shacl_filename_or_graph, Graph):
                    g += shacl_filename_or_graph
                    for name, uri in shacl_filename_or_graph.namespaces():
                        g.bind(name, uri)
            self.graphs[shacl] = g

        for shacl in self.graphs.keys():
            for lang in self.languages:
                shacl_graph = ShaclGraph(shacl, lang, self)
                shacl_graphs.append(shacl_graph)
            if self.shacl_shacl_validation:
                shacl_graph.validate()

        return shacl_graphs


class ShaclMarkdownGenerator(Generator):
    def __init__(
        self,
        languages: List[str],
        output_dir: str = "./",
        shacl_shacl_validation: bool = False,
        version_directory: bool = False,
        crosslink_between_graphs: bool = False,
        jekyll_parent_page: str = "index",
        jekyll_layout: str = "default",
        jekyll_nav_order: int = 1,
        ontology_graphs: List[Union[str, Graph]] = None,
        logger: Logger = None,
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
            ontology_graphs (List[str | Graph], optional): List of ontology files or Graphs, to include with the SHACL shapes, e.g., class definitions or reasoning. Defaults to [].
            logger (Logger, optional): logging.Logger. Defaults to None.
        """
        super().__init__(
            languages, output_dir, shacl_shacl_validation, ontology_graphs, logger
        )
        self.version_directory: bool = version_directory
        self.crosslink_between_graphs: bool = crosslink_between_graphs
        self.jekyll_parent_page: str = jekyll_parent_page
        self.jekyll_layout: str = jekyll_layout
        self.jekyll_nav_order: int = jekyll_nav_order

        self.env = Environment(
            loader=PackageLoader("shacl2md"),
            autoescape=select_autoescape(),
            trim_blocks=True,
        )
        self.template = self.env.get_template("template.md.jinja")
        self.puml_template = self.env.get_template("diagram.puml.jinja")

    def filter_language(self, lang: str):
        """
        Get all other languages.

        Args:
            lang (str): language to filter
        """
        return list(filter(lambda l: l != lang, self.languages))

    def filter_graph(self, graph_name: str):
        """
        Get all other graphs.

        Args:
            graph_name (str): Name of the graph to filter.
        """
        return [g for n, g in self.graphs.items() if n != graph_name]

    def generate(self, exclude: list = None, **shacls) -> None:
        """
        Generate markdown documentation from SHACL files.

        Args:
            exclude: list of graph names for which docs should not be generated
            **shacls: Dictionary of SHACL files or Graphs to generate documentation for. The key is the name of the SHACL graph, the value is the filename of the SHACL file.

        Raises:
            ValidationFailure (pyshacl.errors.ValidationFailure): Raised when the SHACL files do not validate against the SHACL specification.

        Examples:
            >>> from shacl2md import ShaclMarkdownGenerator
            >>> sh_md = ShaclMarkdownGenerator(
            ...     ["nl", "en", "fr"],
            ...     "./output",
            ...     shacl_shacl_validation=True,
            ...     version_directory=True,
            ...     crosslink_between_graphs=True,
            ...     ontology_graphs=[
            ...         "/path_to_ontology/rdfs.ttl",
            ...     ]
            ... )
            >>> sh_md.generate(
            ...     organizations="/path_to_shacl/organizations.shacl.ttl",
            ...     description="/path_to_shacl/description.shacl.ttl",
            ... )
        """
        if not exclude:
            exclude = []
        shacl_graphs: List[ShaclGraph] = self.add_shacl_graphs(**shacls)

        for shacl_graph in shacl_graphs:
            if shacl_graph.name in exclude or shacl_graph.name == "exclude":
                continue
            shacl_graph.generate_md()


class ShaclSnippetGenerator(Generator):
    def __init__(
        self,
        languages: List[str] = ["en"],
        output_dir: str = "./",
        shacl_shacl_validation: bool = False,
        ontology_graphs: List[Union[str, Graph]] = None,
        logger: Logger = None,
    ):
        """
        A shacl snippet generator object.

        Args:
            languages (List[str], optional): List of languages to generate snippets for. Defaults to ["en"].
            output_dir (str, optional): Output directory. Defaults to "./".
            shacl_shacl_validation (bool, optional): Validate the SHACL files against the SHACL specification. Defaults to False.
            ontology_graphs (List[str | Graph], optional): List of ontology files or Graphs, to include with the SHACL shapes, e.g., class definitions or reasoning. Defaults to [].
            logger (Logger, optional): logging.Logger. Defaults to None.
        """
        super().__init__(
            languages, output_dir, shacl_shacl_validation, ontology_graphs, logger
        )

    def generate(self, **shacls):
        """
        Generate snippets from SHACL files. Place the snippets in the `.vscode` directory.

        Args:
            **shacls: Dictionary of SHACL files or Graphs to generate snippets for. The key is the name of the SHACL graph, the value is the filename of the SHACL file.

        Raises:
            ValidationFailure (pyshacl.errors.ValidationFailure): Raised when the SHACL files do not validate against the SHACL specification.

        Examples:
            >>> from shacl2md import ShaclSnippetGenerator
            >>> sh_snippet = ShaclSnippetGenerator()
            >>> sh_snippet.generate(
            ...     organizations="/path_to_shacl/organizations.shacl.ttl",
            ...     description="/path_to_shacl/description.shacl.ttl",
            ... )
        """
        shacl_graphs: List[ShaclGraph] = self.add_shacl_graphs(**shacls)
        for shacl_graph in shacl_graphs:
            shacl_graph.generate_vscode_snippet()


class ShaclGraph:
    def __init__(
        self,
        name: str,
        lang: str,
        generator: Union[ShaclMarkdownGenerator, ShaclSnippetGenerator],
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
        self.graph: Graph = generator.get_graph(name)
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
        code = self.generator.puml_template.render(
            namespaces=self.namespaces,
            classes=[c.to_dict() for c in self.classes],
            output_dir_length=self.output_dir_length,
        )
        print(
            code,
            file=open(f"{self.output_dir}/{puml_filename}", "w"),
        )
        self.generator.logger.info(
            f"* File '{self.output_dir}/{puml_filename}' created"
        )

        # Render PUML diagram
        try:
            jar_path = os.path.join(
                os.path.realpath(os.path.dirname(__file__)), "plantuml.jar"
            )
            retcode = subprocess.call(
                [
                    "java",
                    "-jar",
                    jar_path,
                    f"{self.output_dir}/{puml_filename}",
                    "-svg",
                    "-o",
                    abspath(self.output_dir),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            if retcode > 0:
                raise

            # Extract PUML SVG string
            parser = etree.XMLParser(ns_clean=True, remove_comments=True)
            tree = etree.parse(f"{self.output_dir}/{svg_filename}", parser)
            tree.getroot().attrib.pop("width")
            tree.getroot().attrib.pop("height")
            tree.getroot().attrib.pop("style")
            svg_text = etree.tostring(
                tree.getroot(), encoding="unicode", xml_declaration=False
            )
            return svg_text
        except Exception as e:
            self.generator.logger.error(
                f"* File '{self.output_dir}/{svg_filename}' not created due to PlantUML error: {e}"
            )
            # raise e

    def generate_md(self):
        """
        Generate markdown documentation from the SHACL graph.
        """
        svg_text = self.generate_puml()
        # Dump RDF serialization to file
        rdf_filename = f"{self.name}.shacl.ttl"
        self.graph.serialize(f"{self.output_dir}/{rdf_filename}")
        self.generator.logger.info(f"* File '{self.output_dir}/{rdf_filename}' created")

        other_languages = self.generator.filter_language(self.lang)

        # Get markdown labels
        labels = get_lang_labels(self.lang)

        print(
            self.generator.template.render(
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
                classes=[c.to_dict() for c in self.classes],
                diagramText=svg_text,
                languages=other_languages,
                output_dir_length=self.output_dir_length,
                labels=labels,
            ),
            file=open(f"{self.output_dir}/index.md", "w"),
        )
        self.generator.logger.info(f"* File '{self.output_dir}/index.md' created")

    def generate_vscode_snippet(self):
        """
        Generate Snippets for triples in VSCODE
        """
        snippet_json = {}
        for rdf_class in self.classes:
            if not rdf_class.properties:
                continue
            snippet_json[f"({self.name}){rdf_class.shortname}"] = {
                "prefix": rdf_class.shortname,
                "body": [],
                "description": rdf_class.label,
            }
            snippet_json[f"({self.name}){rdf_class.shortname}"]["body"].append(
                f"${{1:URI}} a {rdf_class.shortname} ;"
            )
            i = 2
            for prop in rdf_class.properties:
                if prop.description:
                    snippet_prop = f"\t{prop.shortname} ${{{i}:{prop.description} ({', '.join([p_dt.shortname for p_dt in prop.datatypes])})}} ;"
                elif prop.label:
                    snippet_prop = f"\t{prop.shortname} ${{{i}:{prop.label} ({', '.join([p_dt.shortname for p_dt in prop.datatypes])})}} ;"
                else:
                    snippet_prop = f"\t{prop.shortname} ${{{i}:({', '.join([p_dt.shortname for p_dt in prop.datatypes])})}} ;"
                snippet_json[f"({self.name}){rdf_class.shortname}"]["body"].append(
                    snippet_prop
                )
                i += 1
            if snippet_json[f"({self.name}){rdf_class.shortname}"]["body"]:
                snippet_json[f"({self.name}){rdf_class.shortname}"]["body"][-1] = (
                    snippet_json[f"({self.name}){rdf_class.shortname}"]["body"][-1][:-1]
                    + "."
                )
        with open(
            f"{self.output_dir}{self.name}.code-snippets", "w", encoding="utf8"
        ) as json_file:
            json.dump(snippet_json, json_file)
            self.generator.logger.info(f"Generated snippet for {self.name}")

    def _get_classes(self):
        crosslink_graphs = []
        try:
            if self.generator.crosslink_between_graphs:
                crosslink_graphs = self.generator.filter_graph(self.name)
        except AttributeError:
            pass
        for c in self.graph.query(
            GET_CLASSES, initBindings={"lang": Literal(self.lang)}
        ):
            c = RDFClass(
                self.lang,
                c.iri,
                to_shortname(self.graph, c.iri),
                c.label,
                c.description,
            )
            c.check_crosslink(self.graph, crosslink_graphs)
            c.get_properties(self.graph, crosslink_graphs)
            c.get_subclasses(self.graph)
            c.get_superclasses(self.graph)
            yield c

    def _generate_output_dir(self):
        base_output_dir = self.generator.output_dir
        output_dir_length = 1
        try:
            version_directory = self.generator.version_directory
            if version_directory:
                if self.doc is None or self.doc.version is None:
                    self.generator.logger.warning(
                        "* Version info not found; outputting in main directory."
                    )
                    output_dir = base_output_dir
                else:
                    output_dir = f"{base_output_dir}/{self.doc.version}"

                if not os.path.exists(base_output_dir):
                    os.mkdir(base_output_dir)
                self.generator.logger.info(f"* Directory '{base_output_dir}' created")
                output_dir_length += 1
            else:
                output_dir = base_output_dir
            output_dir = f"{output_dir}/{self.graph.identifier}/{self.lang}"

        except AttributeError:
            output_dir = base_output_dir

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.generator.logger.info(f"* Directory '{output_dir}' created")
        return output_dir, output_dir_length

    def _get_doc(self):
        for row in self.graph.query(
            GET_DOC_MD, initBindings={"lang": Literal(self.lang)}
        ):
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
        self.generator.logger.info(f"* {results_text}")
