# Shacl2md

[Shacl2md Index](../README.md#shacl2md-index) /
Shacl2md

> Auto-generated documentation for [shacl2md](../../shacl2md/__init__.py) module.

- [Shacl2md](#shacl2md)
  - [download_jar](#download_jar)
  - [get_path](#get_path)
  - [has_jar](#has_jar)
  - [Modules](#modules)

## download_jar

[Show source in __init__.py:31](../../shacl2md/__init__.py#L31)

Downloads the PlantUML jar to the shacl2md
installation folder.
@raises ConnectionError and Timeout

#### Signature

```python
def download_jar(version=PLANTUML_VERSION):
    ...
```

#### See also

- [PLANTUML_VERSION](#plantuml_version)



## get_path

[Show source in __init__.py:11](../../shacl2md/__init__.py#L11)

Function to return the path to the shacl2md installation folder.
@return The path String to the shacl2md installation folder.

#### Signature

```python
def get_path():
    ...
```



## has_jar

[Show source in __init__.py:19](../../shacl2md/__init__.py#L19)

Checks the jar has been succesfully downloaded in
the installation folder.
@return A diagnostic Boolean

#### Signature

```python
def has_jar():
    ...
```



## Modules

- [Cli](cli/index.md)
- [Generator](./generator.md)
- [Templates](templates/index.md)
- [Utilities](utilities/index.md)