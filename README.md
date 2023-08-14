# iBeatles
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](http://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/67521112.svg)](https://zenodo.org/badge/latestdoi/67521112)
[![Build Status](https://travis-ci.org/ornlneutronimaging/iBeatles.svg?branch=master)](https://travis-ci.org/ornlneutronimaging/iBeatles)

GUI to automatically fit Bragg Edges, calculate and display strain mapping factors.

## Runtime Environment Setup

It is recommended to use a virtual environment to install the dependencies for iBeatles.
The following instructions are for setting up a virtual environment using conda.

### Install Miniconda

Download and install Miniconda from https://docs.conda.io/en/latest/miniconda.html

### Create a virtual environment

Create a virtual environment named `iBeatles` with given environment file.

```bash
conda env create -f environment.yml
```

### Install iBeatles [Optional]

Activate the virtual environment:

```bash
conda activate iBeatles
```

Install iBeatles in editable mode:

```bash
pip install -e .
```

Alternatively, if you do not want to install iBeatles, you need to modify your `PYTHONPATH` to include the path to the `iBeatles` directory.

```bash
export PYTHONPATH=/path/to/iBeatles:$PYTHONPATH
```

## Run iBeatles

Activate the virtual environment:

```bash
conda activate iBeatles
```

Run iBeatles:

```bash
python -m ibeatles
```

or use the script directly

```bash
cd /path/to/iBeatles
python scripts/iBeatles
```

After that, all the normal
[setuptools](https://pythonhosted.org/setuptools/setuptools.html) magic applies.

Because the current version is still under development, it can be a little bit struggle to get it up and running...do not hesitate to contact me to get help on the installation (j35 at ornl.gov)

## Development Environment Setup

The development environment is similar to the runtime environment, except that it is required to perform the installation in editable mode.

Here is a quick recap of the steps:

```bash
conda env create -f environment.yml
conda activate iBeatles
pip install -e .
```
