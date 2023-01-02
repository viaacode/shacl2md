# shacl2md
Generates datamodel documentation from SHACL and/or RDFS files.

# Usage:

```bash
usage: shacl2md.py [-h] [--language [language [language ...]]] [--out out] [--parent parent] [--layout layout]
               [--nav_order nav_order] [--name name] [--crosslinks [crosslinks [crosslinks ...]]] [--vdir]
               [--validate] [--nodocs]
               inputFile [inputFile ...]

```
# Positional Arguments

|Option|Default|Description|
| :--- | :--- | :--- |
|`files`|`None`|SHACL OR RDFS files to construct Markdown documentation of.|

# Optional Arguments

|Option|Default|Description|
| :--- | :--- | :--- |
|`-h`, `--help`||show this help message and exit|
|`--language`|`['nl']`|languages of generated documentation, default is "nl"|
|`--out`|`./`|output directory for files, default is "./"|
|`--parent`|`index`|Jekyll parent page, default is "index"|
|`--layout`|`default`|Jekyll layout, default is "default"|
|`--nav_order`|`1`|Jekyll nav order, default is 1|
|`--name`|`output`|filename for the output file, default is "output"|
|`--crosslinks`|`None`|crosslink graphs to find classes in: format is "name;file1;file2;..."|
|`--vdir`||if present, outputs files to a directory based on the SHACL version|
|`--validate`||if present, the shacl file is validated against the SHACL-SHACL.|
|`--nodocs`||if present, only a diagram is produced.|
