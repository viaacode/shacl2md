GET_DOC_MD = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX pav: <http://purl.org/pav/>
SELECT DISTINCT ?title ?created ?modified ?description ?version
WHERE { 
    ?doc dct:title ?title; a owl:Ontology.
    FILTER(lang(?title) = ?lang)
    OPTIONAL { ?doc dct:created ?created. }
    OPTIONAL { ?doc dct:modified ?modified. }
    OPTIONAL { ?doc pav:version ?version. }
    OPTIONAL { 
        ?doc dct:description ?description. 
        FILTER(lang(?description) = ?lang)
    }
}
LIMIT 1
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
GET_CLASS = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?label ?description
WHERE {
    ?shape a sh:NodeShape ;
        sh:targetClass ?iri .
    OPTIONAL { 
        ?iri rdfs:label ?label . 
     FILTER(lang(?label) = ?lang)
    }
    OPTIONAL {?iri rdfs:comment ?rdfsdescription
        FILTER(lang(?rdfsdescription) = ?lang) 
    }
    OPTIONAL {?iri skos:definition ?skosdefinition
        FILTER(lang(?skosdefinition) = ?lang) 
    }
    BIND (
        COALESCE(
            IF(bound(?skosdefinition), ?skosdefinition, 1/0),
            IF(bound(?rdfsdescription), ?rdfsdescription, 1/0)
        ) AS ?description
    )
}
"""

GET_CLASSES = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT ?iri ?label ?description
WHERE {
    {?subjectclassNode sh:targetClass ?iri . }
    UNION
    {?property sh:or*/rdf:rest*/rdf:first*/sh:class ?iri .}

    OPTIONAL { 
        ?iri rdfs:label ?label. 
     FILTER(lang(?label) = ?lang)
    }
    OPTIONAL {?iri rdfs:comment ?rdfsdescription
        FILTER(lang(?rdfsdescription) = ?lang) 
    }
    OPTIONAL {?iri skos:definition ?skosdefinition
        FILTER(lang(?skosdefinition) = ?lang) 
    }
    BIND (
        COALESCE(
            IF(bound(?skosdefinition), ?skosdefinition, 1/0),
            IF(bound(?rdfsdescription), ?rdfsdescription, 1/0)
        ) AS ?description
    )
}
ORDER BY ?label
"""

GET_SUBCLASSES = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?iri ?label ?description
WHERE { 
    ?iri   rdfs:subClassOf ?parent ; 
        a rdfs:Class.
    OPTIONAL { 
        ?iri rdfs:label ?label. 
     FILTER(lang(?label) = ?lang)
    }
    OPTIONAL { 
        ?iri rdfs:comment ?description. 
        FILTER(lang(?description) = ?lang)
    }

}
ORDER BY ?label
"""

GET_SUPERCLASSES = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?iri ?label ?description
WHERE { 
    ?child   rdfs:subClassOf ?iri . 
    ?iri a rdfs:Class.
    OPTIONAL { 
        ?iri rdfs:label ?label. 
        FILTER(lang(?label) = ?lang)
    }
    OPTIONAL { 
        ?iri rdfs:comment ?description. 
        FILTER(lang(?description) = ?lang)
    }
}
ORDER BY ?label
"""

GET_PROPERTIES = """
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX schema: <http://schema.org/>
SELECT DISTINCT ?shape ?iri ?label ?description ?min ?max ?kind ?uniqueLang
WHERE {
    ?subjectclassNode sh:targetClass ?targetClass .
    ?subjectclassNode sh:or*/rdf:rest*/rdf:first*/sh:property ?shape .
    ?shape sh:path ?iri.

    # Label
    OPTIONAL {
        ?shape sh:name ?shname
        FILTER(lang(?shname) = ?lang) 
    }
    OPTIONAL {
        ?iri rdfs:label ?rdfslabel
        FILTER(lang(?rdfslabel) = ?lang) 
    }
    BIND (
        COALESCE(
            IF(bound(?shname), ?shname, 1/0),
            IF(bound(?rdfslabel), ?rdfslabel, 1/0)
        ) AS ?label
    )

    # Description  
    OPTIONAL {?shape sh:description ?shacldescription
        FILTER(lang(?shacldescription) = ?lang) 
    }
    OPTIONAL {?iri rdfs:comment ?rdfsdescription
        FILTER(lang(?rdfsdescription) = ?lang) 
    }
    OPTIONAL {?iri skos:definition ?skosdefinition
        FILTER(lang(?skosdefinition) = ?lang) 
    }
    BIND (
        COALESCE(
            IF(bound(?shacldescription), ?shacldescription, 1/0),
            IF(bound(?skosdefinition), ?skosdefinition, 1/0),
            IF(bound(?rdfsdescription), ?rdfsdescription, 1/0)
        ) AS ?description
    )

    # Cardinality
    OPTIONAL {?shape sh:minCount ?min}
    OPTIONAL {?shape sh:maxCount ?max}
    OPTIONAL {?shape sh:uniqueLang ?uniqueLang}

    OPTIONAL {
        ?shape sh:nodeKind ?kind
    }
}
ORDER BY ?label
"""

GET_DATATYPES = """
PREFIX sh: <http://www.w3.org/ns/shacl#>
SELECT DISTINCT ?iri ?label ?type ?kind
WHERE {
    {
        ?shape sh:or*/rdf:rest*/rdf:first*/sh:datatype ?iri .
        OPTIONAL {
            ?iri rdfs:label ?label
            FILTER(lang(?label) = ?lang)
        }
        BIND("datatype" AS ?type)
    } UNION {
        ?shape sh:or*/rdf:rest*/rdf:first*/sh:class ?iri .
        OPTIONAL {
            ?iri rdfs:label ?label
            FILTER(lang(?label) = ?lang)
        }
        BIND("class" AS ?type)
    }
}
"""

GET_VALUES = """
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX schema: <http://schema.org/>
SELECT ?iri ?label
WHERE {
    ?shape sh:in ?n .
    OPTIONAL{
        ?n rdf:rest*/rdf:first ?iri
        
        OPTIONAL {
            ?iri rdfs:label ?label
            FILTER(lang(?label) = ?lang)
        }    
    } 
}
"""

CLASS_EXISTS_CHECK = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sh: <http://www.w3.org/ns/shacl#> 
ASK {
    ?shape a sh:NodeShape ;
        sh:targetClass ?iri .
}
"""
