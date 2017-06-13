iBeatles
======

GUI to automatically fit Bragg Edges, calculate and display strain mapping factors. 

Building
--------
Install all the dependencies
> pip install -r requirements.txt

Before doing the normal `python setup.py ...` things you must convert the
`designer/*.ui` files to `ibeatles/interfaces/*.py. 
This is done with
> python setup.py pyuic

Because the current version is still under development, it can be a little bit struggle to get it up and running...do not hesitate to contact me to get help on the installation (j35 at ornl.gov)

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](http://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/67521112.svg)](https://zenodo.org/badge/latestdoi/67521112)
[![Build Status](https://travis-ci.org/ornlneutronimaging/iBeatles.svg?branch=master)](https://travis-ci.org/ornlneutronimaging/iBeatles)
