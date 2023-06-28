import sys

from setuptools import find_packages, setup

version = None
if "--new-version" in sys.argv:
    version_index = sys.argv.index("--new-version")
    version = sys.argv[version_index + 1]
    del sys.argv[version_index : version_index + 2]


with open("requirements.txt") as install_requires_file:
    install_requires = install_requires_file.read().strip().split("\n")

with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    name="shacl2md",
    version=version,
    description="Shacl to Markdown documentation generator",
    license="MIT License",
    keywords="documentation",
    url="https://github.com/viaacode/shacl2md",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("tests", "docs")),
    python_requires=">=3.7",
    install_requires=install_requires,
    include_package_data=True,
    entry_points={
        "console_scripts": ["shacl2md=shacl2md.cli:app"],
    },
)

