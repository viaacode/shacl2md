import os

import requests
from tqdm import tqdm

from shacl2md.generator import ShaclMarkdownGenerator

PLANTUML_JAR_URL="https://github.com/plantuml/plantuml/releases/download/v1.2023.11/plantuml-{}.jar"
PLANTUML_VERSION="1.2023.11"

def get_path():
    """
    Function to return the path to the shacl2md installation folder.
    @return The path String to the shacl2md installation folder.
    """
    path = os.path.realpath(os.path.dirname(__file__))
    return path

def has_jar():
    """
    Checks the jar has been succesfully downloaded in
    the installation folder.
    @return A diagnostic Boolean
    """
    files = os.listdir(get_path())
    for file in files:
        if '.jar' in file:
            return True
    return False

def download_jar(version= PLANTUML_VERSION):
    """
    Downloads the PlantUML jar to the shacl2md
    installation folder.
    @raises ConnectionError and Timeout
    """
    print('Downloading the PlantUML jar, please wait...')
    try:
        path2jar = os.path.join(get_path(), 'plantuml.jar')
        request = requests.get(PLANTUML_JAR_URL.format(version), stream=True, timeout=10.0)
        length = int(request.headers.get('content-length', 0))
        with open(path2jar, 'wb') as jar:
            with tqdm(desc=f'Downloading {PLANTUML_JAR_URL.format(version)}',
                      total=length, unit='iB', unit_scale=True,
                      unit_divisor=1024) as pbar:
                for data in request.iter_content(chunk_size=1024):
                    size = jar.write(data)
                    pbar.update(size)
        print('The Download was successful!')
        print('The system is now ready for use!')
    except requests.ConnectionError as err:
        print('WARNING!!! download_jar() caught '
              + f'a {type(err)} exception and passed it on.')
        raise
    except requests.Timeout as exc:
        print('WARNING!!! download_jar() caught '
              + f'a {type(exc)} exception and passed it on.')
        raise

# Checks if PlantUML is not installed. Installs it if so.
try:
    if not has_jar():  # PlantUML not installed.
        print('No PlantUML jar has been found'
              + ' in the installation folder.')
        download_jar()
except requests.ConnectionError as err:
    print(f' A {type(err)} exception has been raised. \n'
          + 'Installation unsuccessful!!!')
    raise
except requests.Timeout as exc:
    print(f' A {type(exc)} exception has been raised. \n'
          + 'Installation unsuccessful!!!')
    raise