iBeatles
======

GUI to automatically fit Bragg Edges, calculate and display strain mapping factors. 

Building
--------
Install all the dependencies
> pip install -r requirements.txt

add iBeatles to python path (as well as BraggEdge as right now the library do not seem to work correctly!)
> export PYTHONPATH=/Users/j35/git/iBeatles;/Users/j35/git/BraggEdge/
> python scripts/ibeatles.py

After that, all the normal
[setuptools](https://pythonhosted.org/setuptools/setuptools.html) magic applies.

Because the current version is still under development, it can be a little bit struggle to get it up and running...do not hesitate to contact me to get help on the installation (j35 at ornl.gov)

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](http://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/67521112.svg)](https://zenodo.org/badge/latestdoi/67521112)
[![Build Status](https://travis-ci.org/ornlneutronimaging/iBeatles.svg?branch=master)](https://travis-ci.org/ornlneutronimaging/iBeatles)

Developers
----------

To install iBeatles

$ conda create -n iBeatles python=3.7
$ conda activate iBeatles
$ git clone https://github.com/pyqtgraph/pyqtgraph.git
$ cd pyqtgraph
$ pip install -e .
$ cd ~/git/iBeatles
$ python -m iBeatles
$ conda install qtpy
$ conda install pandas
$ conda install -y -c anaconda PyQt
$ conda install astrapy
$ conda install pillow
$ conda install matplotlib
$ pip install neutronbraggedge
$ conda install -c Conda-forge qt=5.12.9
$ conda install scipy
$ conda install lmfit
$ pip install NeuNorm
$ python -m iBeatles