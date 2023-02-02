import os
from setuptools import setup, find_packages
import versioneer  # https://github.com/warner/python-versioneer

THIS_DIR = os.path.dirname(__file__)


def read_requirements_from_file(filepath):
    '''Read a list of requirements from the given file and split into a
    list of strings. It is assumed that the file is a flat
    list with one requirement per line.
    :param filepath: Path to the file to read
    :return: A list of strings containing the requirements
    '''
    with open(filepath, 'r') as req_file:
        return req_file.readlines()


setup_args = dict(
        install_requires=read_requirements_from_file(
                os.path.join(
                        THIS_DIR,
                        'requirements.txt')),
        # tests_require=read_requirements_from_file(
        #     os.path.join(
        #         THIS_DIR,
        #         'requirements-dev.txt'))
)

setup(name="ibeatles",
      #      version=versioneer.get_version(),
      version="23_02_01_beta",
      description="Bragg Edge Fitting and Strain Calculator",
      author="Jean Bilheux",
      author_email="bilheuxjm@ornl.gov",
      url="http://github.com/ornlneutronimaging/iBeatles",
      long_description="""Should have a longer description""",
      license="The MIT License (MIT)",
      scripts=["scripts/run.py"],
      packages=find_packages(),
      package_data={'': ['*.ui', '*.png', '*.qrc', '*.json']},
      install_requires=setup_args["install_requires"],
      setup_requires=[],
      )
