LANG_LABELS= {
    "nl" : {
        "Version" : "Versie",
        "Prior version" : "Vorige versie",
        "Created" : "Aangemaakt op",
        "Last modified" : "Laatst gewijzigd op",
        "SHACL file" : "SHACL-bestand",
        "Other languages" : "Andere talen",
        "Authors" : "Auteurs",
        "Namespaces" : "Naamruimten",
        "Classes & Properties" : "Klassen & Eigenschappen",
        "Classes" : "Klassen",
        "Subclass of" : "Subklasse van",
        "Subclasses" : "Subklassen",
        "Property" : "Eigenschap",
        "Description" : "Beschrijving",
        "Cardinality" : "Kardinaliteit",
        "Datatype" : "Datatype",
        "Properties from" : "Eigenschappen van"
    },
    "en" : {
        "Version" : "Version",
        "Prior version" : "Previous version",
        "Created" : "Created",
        "Last modified" : "Last modified",
        "SHACL file" : "SHACL file",
        "Other languages" : "Other languages",
        "Authors" : "Authors",
        "Namespaces" : "Namespaces",
        "Classes & Properties" : "Classes & Properties",
        "Classes" : "Classes",
        "Subclass of" : "Subclass of",
        "Subclasses" : "Subclasses",
        "Property" : "Property",
        "Description" : "Description",
        "Cardinality" : "Cardinality",
        "Datatype" : "Datatype",
        "Properties from" : "Properties from"
    },
    "fr" : {
        "Version" : "Version",
        "Prior version" : "Version précédente",
        "Created" : "Créé",
        "Last modified" : "Dernière mise à jour",
        "SHACL file" : "Fichier SHACL",
        "Other languages" : "Autres langues",
        "Authors" : "Auteurs",
        "Namespaces" : "Espaces de noms",
        "Classes & Properties" : "Classes & Propriétés",
        "Classes" : "Classes",
        "Subclass of" : "Sous-classe de",
        "Subclasses" : "Sous-classes",
        "Property" : "Propriété",
        "Description" : "Description",
        "Cardinality" : "Cardinalité",
        "Datatype" : "Type de données",
        "Properties from" : "Propriétés de"
    }
}

def get_lang_labels(lang):
    if lang in LANG_LABELS:
        return LANG_LABELS[lang]
    else:
        return LANG_LABELS["en"]