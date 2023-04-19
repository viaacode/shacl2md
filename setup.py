from setuptools import find_packages, setup

with open("requirements.txt") as install_requires_file:
    install_requires = install_requires_file.read().strip().split("\n")

with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    name=" shacl2md",
    version="0.1",
    description="Generates datamodel documentation from SHACL and/or RDFS files. ",
    license="MIT License",
    author="Lennert Van de Velde",
    author_email="lennert.vandevelde@meemoo.be",
    keywords=["shacl","rdfs","markdown"],
    url="https://github.com/viaacode/shacl2md",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=install_requires,
)
