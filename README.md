# shacl2md
Generates datamodel documentation from SHACL and/or RDFS files.


```
usage: shacl2md.py [-h] [--language language] [--out out] [--name name] [--crosslinks crosslinks] inputFile [inputFile ...]

positional arguments:
  inputFile            SHACL OR RDFS files to construct Markdown documentation of.

optional arguments:
  -h, --help           show this help message and exit
  --language language  language of generated documentation, default is "nl"
  --out out            output directory for files, default is "./"
  --name name          filename for the output file, default is "output"
  --crosslinks         crosslink graphs to find classes in: format is "name;file1;file2;..."
```