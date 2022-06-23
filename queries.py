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
    ?iri   rdfs:subClassOf ?parent ; 
        a rdfs:Class;
        rdfs:label ?label.
    FILTER(lang(?label) = ?lang)
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
    ?iri a rdfs:Class;
        rdfs:label ?label.
    FILTER(lang(?label) = ?lang)
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
SELECT ?targetClass ?subjectclassNode ?iri ?label ?datatype ?datatype_label ?classtype ?classtype_label ?min ?max ?description (GROUP_CONCAT(?thesaurusitem;separator=", ") AS ?thesaurus)
WHERE {
    ?subjectclassNode sh:targetClass ?targetClass .
    ?subjectclassNode sh:property ?property.
    ?property sh:path ?iri;
            sh:name ?label .
    FILTER(lang(?label) = ?lang)
    OPTIONAL {?iri rdfs:comment ?rdfsdescription
        FILTER(lang(?rdfsdescription) = ?lang) 
    }
    OPTIONAL {?property sh:description ?shacldescription
        FILTER(lang(?shacldescription) = ?lang) 
    }
    BIND (
        COALESCE(
            IF(bound(?shacldescription), ?shacldescription, 1/0),
            IF(bound(?rdfsdescription), ?rdfsdescription, 1/0)
        ) AS ?description
    )
    OPTIONAL {?property sh:minCount ?min}
    OPTIONAL {?property sh:maxCount ?max}
    OPTIONAL {?property sh:datatype ?datatype .
       OPTIONAL{?datatype rdfs:label ?datatype_label} }
    OPTIONAL {?property sh:or*/rdf:rest*/rdf:first*/sh:class ?classtype .
       OPTIONAL{?classtype rdfs:label ?classtype_label .
       FILTER(lang(?classtype_label) = ?lang)} }
    OPTIONAL {?property sh:in ?thesaurusnode .
       OPTIONAL{?thesaurusnode rdf:rest*/rdf:first ?thesaurusitem} }
}
GROUP BY ?targetClass ?subjectclassNode ?iri ?label ?datatype ?datatype_label ?classtype ?classtype_label ?min ?max ?description
ORDER BY ?label
"""


GET_ATTRIBUTES = """
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX schema: <http://schema.org/>
SELECT DISTINCT ?targetClass ?subjectclassNode ?iri ?label ?datatype ?datatype_label ?min ?max ?description
WHERE {
    ?subjectclassNode sh:targetClass ?targetClass;
                      sh:property ?property.
    ?property sh:path ?iri;
              sh:datatype ?datatype .

    OPTIONAL{ ?datatype rdfs:label ?datatype_label}

    OPTIONAL {?property sh:name ?shname
        FILTER(lang(?shname) = ?lang) 
    }
    OPTIONAL {?property rdfs:label ?rdfslabel
        FILTER(lang(?rdfslabel) = ?lang) 
    }
    BIND (
        COALESCE(
            IF(bound(?shname), ?shname, 1/0),
            IF(bound(?rdfslabel), ?rdfslabel, 1/0)
        ) AS ?label
    )

    OPTIONAL {?iri rdfs:comment ?rdfsdescription
        FILTER(lang(?rdfsdescription) = ?lang) 
    }
    OPTIONAL {?property sh:description ?shacldescription
        FILTER(lang(?shacldescription) = ?lang) 
    }
    BIND (
        COALESCE(
            IF(bound(?shacldescription), ?shacldescription, 1/0),
            IF(bound(?rdfsdescription), ?rdfsdescription, 1/0)
        ) AS ?description
    )
    OPTIONAL {?property sh:minCount ?min}
    OPTIONAL {?property sh:maxCount ?max} 
    }
}
"""