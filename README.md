# iBeatles
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](http://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/67521112.svg)](https://zenodo.org/badge/latestdoi/67521112)

GUI to automatically fit Bragg Edges, calculate and display strain mapping factors.

## Installation

### From PyPI (recommended)

To install the latest release from PyPI, use the following command:

```bash
pip install ibeatles
```

This should install the latest release of iBeatles and all its dependencies.
To start the application, use the following command:

```bash
python -m ibeatles
```

which will start the GUI application.
For command-line interface (CLI) application, use the following command:

```bash
python -m ibeatles --no-gui <CONFIG_FILE>
```

### From Conda

To install the latest release from Conda, use the following command:

```bash
micromamba install -c conda-forge -c ornlneutronimaging ibeatles
```

This should install the latest release of iBeatles and all its dependencies.
To start the application, use the following command:

```bash
python -m ibeatles
```

which will start the GUI application.
For command-line interface (CLI) application, use the following command:

```bash
python -m ibeatles --no-gui <CONFIG_FILE>
```

### From Source

Check the instructions in the [Development Environment Setup](#development-environment-setup) section to setup the development environment for iBeatles.

## Development Environment Setup

It is recommended to use a virtual environment to setup the development environment for iBeatles.
The following instructions are for setting up a virtual development environment using `pixi`.
For detailed instructions on how to install `pixi`, please refer to the [pixi documentation](https://pixi.readthedocs.io/en/latest/).

- Install `pixi`:

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

- Clone the iBeatles repository:

```bash
git clone git@github.com:ornlneutronimaging/iBeatles.git
```

- Install the dependencies:

```bash
cd iBeatles
pixi install
```

Note that `pixi install` will install all dependencies, including the editable version of iBeatles.

> By default, `pixi` is configured to use `detached-environments` so that you can build the conda packages directly in the repo. This settings can be changed by `pixi config set detached-environments false` if needed.

## Run iBeatles

There are several ways to start the application:

- Use the entry script to start the GUI application.

```bash
pixi run ibeatles
```

- Use `pixi` tasks `run` to start the GUI application.

```bash
# to start GUI application
pixi run start
# to start CLI application
pixi run cli  <CONFIG_FILE>
```

- Use Python interpreter to start the GUI application.

```bash
# start GUI application
pixi run python -m ibeatles
# start CLI application
pixi run python -m ibeatles --no-gui <CONFIG_FILE>
```

## Run Tests

To run the tests, use the following command:

```bash
pixi run test
```

Alternatively, you can always invoke the Python interpreter directly:

```bash
python -m pytest
```

> Note: we recommend using `pixi` to run the tests as it will ensure that the correct environment is used.

## Build Documentation

More to come...

## Packaging

### PyPI Package

To build the PyPI package, use the following command:

```bash
pixi run build
```

This will create a `dist` directory containing the PyPI package.

### Conda Package

To build the Conda package, use the following command:

```bash
pixi run build-conda
```

This will build the Conda packages in the `conda.recipe` directory.

To clean up all the builds, use

```bash
pixi run clean
```

If you prefer to clean all the environments (not builds), use

```bash
pixi clean
```

which will remove all the environments created by `pixi`.
