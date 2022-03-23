from setuptools import setup, find_packages
import versioneer  # https://github.com/warner/python-versioneer

setup(name="iBeatles",
      version=versioneer.get_version(),
      description="Bragg Edge Fitting and Strain Calculator",
      author="Jean Bilheux",
      author_email="bilheuxjm@ornl.gov",
      url="http://github.com/ornlneutronimaging/iBeatles",
      long_description="""Should have a longer description""",
      license="The MIT License (MIT)",
      scripts=["scripts/run.py"],
      packages=find_packages(where='src'),
      package_dir={'': 'src'},
      setup_requires=['numpy',
                      'matplotlib',
                      'pyqtgraph',
                      'lmfit'],
      install_requires=[
          'matplotlib',
          'numpy',
          'lmfit',
          'versioneer',
        ],
      )
