# Rdf

[Shacl2md Index](../../README.md#shacl2md-index) /
[Shacl2md](../index.md#shacl2md) /
[Utilities](./index.md#utilities) /
Rdf

> Auto-generated documentation for [shacl2md.utilities.rdf](../../../shacl2md/utilities/rdf.py) module.

- [Rdf](#rdf)
  - [RDFClass](#rdfclass)
    - [RDFClass().check_crosslink](#rdfclass()check_crosslink)
    - [RDFClass().get_class_info](#rdfclass()get_class_info)
    - [RDFClass().get_properties](#rdfclass()get_properties)
    - [RDFClass().get_subclasses](#rdfclass()get_subclasses)
    - [RDFClass().get_superclasses](#rdfclass()get_superclasses)
    - [RDFClass().to_dict](#rdfclass()to_dict)
  - [RDFDatatype](#rdfdatatype)
    - [RDFDatatype().copy](#rdfdatatype()copy)
    - [RDFDatatype().to_dict](#rdfdatatype()to_dict)
  - [RDFProperty](#rdfproperty)
    - [RDFProperty().get_datatypes](#rdfproperty()get_datatypes)
    - [RDFProperty().get_values](#rdfproperty()get_values)
    - [RDFProperty().to_dict](#rdfproperty()to_dict)
  - [RDFValue](#rdfvalue)
    - [RDFValue().to_dict](#rdfvalue()to_dict)
  - [to_shortname](#to_shortname)

## RDFClass

[Show source in rdf.py:20](../../../shacl2md/utilities/rdf.py#L20)

#### Signature

```python
class RDFClass:
    def __init__(self, lang: str, iri, shortname, label=None, description=None):
        ...
```

### RDFClass().check_crosslink

[Show source in rdf.py:118](../../../shacl2md/utilities/rdf.py#L118)

#### Signature

```python
def check_crosslink(self, g: Graph, g_crosslinks: List[Graph] = []):
    ...
```

### RDFClass().get_class_info

[Show source in rdf.py:108](../../../shacl2md/utilities/rdf.py#L108)

#### Signature

```python
def get_class_info(self, g: Graph):
    ...
```

### RDFClass().get_properties

[Show source in rdf.py:81](../../../shacl2md/utilities/rdf.py#L81)

#### Signature

```python
def get_properties(self, g: Graph, g_crosslinks: List[Graph] = []):
    ...
```

### RDFClass().get_subclasses

[Show source in rdf.py:61](../../../shacl2md/utilities/rdf.py#L61)

#### Signature

```python
def get_subclasses(self, g: Graph):
    ...
```

### RDFClass().get_superclasses

[Show source in rdf.py:40](../../../shacl2md/utilities/rdf.py#L40)

#### Signature

```python
def get_superclasses(self, g: Graph):
    ...
```

### RDFClass().to_dict

[Show source in rdf.py:141](../../../shacl2md/utilities/rdf.py#L141)

#### Signature

```python
def to_dict(self) -> dict:
    ...
```



## RDFDatatype

[Show source in rdf.py:213](../../../shacl2md/utilities/rdf.py#L213)

#### Signature

```python
class RDFDatatype:
    def __init__(self, iri, shortname, label):
        ...
```

### RDFDatatype().copy

[Show source in rdf.py:225](../../../shacl2md/utilities/rdf.py#L225)

#### Signature

```python
def copy(self):
    ...
```

### RDFDatatype().to_dict

[Show source in rdf.py:229](../../../shacl2md/utilities/rdf.py#L229)

#### Signature

```python
def to_dict(self):
    ...
```



## RDFProperty

[Show source in rdf.py:145](../../../shacl2md/utilities/rdf.py#L145)

#### Signature

```python
class RDFProperty:
    def __init__(self, iri, shortname, label, description, min, max, uniqueLang):
        ...
```

### RDFProperty().get_datatypes

[Show source in rdf.py:166](../../../shacl2md/utilities/rdf.py#L166)

#### Signature

```python
def get_datatypes(self, g: Graph, s, lang: str, g_crosslinks: List[Graph] = []):
    ...
```

### RDFProperty().get_values

[Show source in rdf.py:184](../../../shacl2md/utilities/rdf.py#L184)

#### Signature

```python
def get_values(self, g: Graph, s, lang: str):
    ...
```

### RDFProperty().to_dict

[Show source in rdf.py:209](../../../shacl2md/utilities/rdf.py#L209)

#### Signature

```python
def to_dict(self):
    ...
```



## RDFValue

[Show source in rdf.py:233](../../../shacl2md/utilities/rdf.py#L233)

#### Signature

```python
class RDFValue:
    def __init__(self, iri, shortname, label):
        ...
```

### RDFValue().to_dict

[Show source in rdf.py:248](../../../shacl2md/utilities/rdf.py#L248)

#### Signature

```python
def to_dict(self):
    ...
```



## to_shortname

[Show source in rdf.py:16](../../../shacl2md/utilities/rdf.py#L16)

#### Signature

```python
def to_shortname(g: Graph, term):
    ...
```