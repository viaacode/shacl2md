GET_DOC_MD = """
PREFIX dct: <http://purl.org/dc/terms/>

SELECT DISTINCT ?title ?created ?modified ?description
WHERE { 
    ?doc dct:title ?title.
    FILTER(lang(?title) = ?lang)
    OPTIONAL { ?doc dct:created ?created. }
    OPTIONAL { ?doc dct:modified ?modified. }
    OPTIONAL { 
        ?doc dct:description ?description. 
        FILTER(lang(?description) = ?lang)
    }
}
"""


GET_AUTHORS = """
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX schema: <https://schema.org/>

SELECT DISTINCT ?label ?email
WHERE {
    ?doc dct:author ?a.

    ?a schema:name ?label.
    OPTIONAL { ?a schema:email ?email. } 
}
"""

GET_CLASSES = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?iri ?label ?description
WHERE {
    ?iri a rdfs:Class;
        rdfs:label ?label.
    FILTER(lang(?label) = ?lang)
    OPTIONAL { 
        ?iri rdfs:comment ?description. 
        FILTER(lang(?description) = ?lang)
    }
}
"""

GET_SUBCLASSES = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?iri ?label ?description
WHERE { 
    ?iri   rdfs:subClassOf ?parent . 

    ?iri a rdfs:Class;
        rdfs:label ?label;
        rdfs:comment ?description.
        FILTER(lang(?label) = ?lang)
        FILTER(lang(?description) = ?lang)

}
"""

GET_SUPERCLASSES = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?iri ?label ?description
WHERE { 
    ?child   rdfs:subClassOf ?iri . 

    ?iri a rdfs:Class;
        rdfs:label ?label;
        rdfs:comment ?description.
        FILTER(lang(?label) = ?lang)
        FILTER(lang(?description) = ?lang)

}
"""

GET_PROPERTIES = """
PREFIX sh: <http://www.w3.org/ns/shacl#>
SELECT DISTINCT ?iri ?label ?description ?min ?max ?class ?datatype ?datatype_label
WHERE {
    ?class sh:property ?property.

    ?property sh:path ?iri;
            sh:name ?label;
            sh:description ?description.

    OPTIONAL {?property sh:minCount ?min}
    OPTIONAL {?property sh:maxCount ?max}
    OPTIONAL {?property sh:class ?class}
    OPTIONAL {?property sh:datatype ?datatype}

    OPTIONAL {?datatype rdfs:label ?datatype_label}
}
"""