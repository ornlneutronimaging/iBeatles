# GitHub Copilot Instructions for iBeatles

## Project Overview

iBeatles is a GUI application for automatically fitting Bragg Edges, calculating and displaying strain mapping factors. It's a scientific Python application used for neutron imaging analysis.

## Technology Stack

- **Language**: Python 3.11-3.12
- **GUI Framework**: PyQt5, QtPy, pyqtgraph
- **Scientific Libraries**: numpy, scipy, matplotlib, lmfit, astropy
- **Data Handling**: h5py, Pillow
- **Configuration**: pydantic, tomli
- **Build System**: setuptools with versioningit
- **Package Managers**: pixi (recommended), pip, or conda
- **Testing**: pytest with pytest-cov
- **Linting**: ruff
- **Pre-commit**: Configured for code quality checks

## Code Style and Conventions

### Python Style
- Follow PEP 8 conventions
- Maximum line length: 120 characters (configured in both pylint and ruff)
- Use double quotes for strings (ruff configuration)
- Use 4 spaces for indentation (no tabs)
- Import organization: ruff handles this automatically with isort
- Known first-party package: `ibeatles`

### Code Quality
- All code changes should pass ruff linting and formatting
- Run `ruff check --fix` to auto-fix linting issues
- Run `ruff format` to format code
- Pre-commit hooks enforce these standards automatically

### Testing Conventions
- Tests are located in `tests/` directory
- Test files should start with `test_` prefix
- Use pytest markers for test categorization:
  - `@pytest.mark.unit` - Unit tests
  - `@pytest.mark.integration` - Integration tests
  - `@pytest.mark.slow` - Tests that are slow to run
  - `@pytest.mark.gui` - Tests for GUI components
- Aim for good test coverage (use `--cov-branch` for branch coverage)
- Tests should be deterministic and not rely on external resources when possible

## Project Structure

```
src/ibeatles/          # Main source code
  ├── __main__.py      # Entry point
  ├── ibeatles.py      # Main application
  ├── core/            # Core functionality
  ├── fitting/         # Fitting algorithms
  ├── interfaces/      # Interface definitions
  ├── step1/           # Processing step 1
  ├── step2/           # Processing step 2
  ├── step3/           # Processing step 3
  ├── step6/           # Processing step 6
  ├── ui/              # UI definition files
  ├── utilities/       # Utility functions
  └── widgets/         # Custom widgets
tests/                 # Test files
  ├── data/            # Test data files
  ├── ibeatles/        # Integration and functional tests
  └── unit/            # Unit tests
conda.recipe/          # Conda packaging
designer/              # Qt Designer files
docs/                  # Documentation
notebooks/             # Jupyter notebooks
reference/             # Reference materials
```

## Development Workflow

### Setting Up Environment
Prefer using pixi for development:
```bash
pixi install    # Install all dependencies
pixi run test   # Run tests
pixi run start  # Start GUI application
```

### Running Tests
```bash
pixi run test                                    # Run all tests with coverage
python -m pytest tests                           # Alternative without pixi
python -m pytest tests --cov=src/ibeatles       # With coverage
python -m pytest -m unit                         # Run only unit tests
```

### Building the Project
```bash
pixi run build        # Build PyPI package
pixi run build-conda  # Build conda package
pixi run clean        # Clean all build artifacts
```

### Running the Application
```bash
pixi run start                           # Start GUI application
pixi run cli <CONFIG_FILE>              # Start CLI application
python -m ibeatles                       # GUI via Python module
python -m ibeatles --no-gui <CONFIG>    # CLI via Python module
```

## Guidelines for Code Changes

### When Adding New Features
1. Add tests for new functionality in the appropriate test directory
2. Update docstrings following existing patterns
3. Ensure GUI components follow PyQt5 patterns used in the codebase
4. Update configuration schema if adding new config options
5. Consider backward compatibility

### When Fixing Bugs
1. Add a test that reproduces the bug (if feasible)
2. Fix the issue with minimal changes
3. Ensure the test passes after the fix
4. Check for similar issues in related code

### When Refactoring
1. Ensure all existing tests still pass
2. Do not change public API without good reason
3. Update docstrings and comments as needed
4. Consider impact on GUI functionality

### Working with GUI Components
- UI files are in `src/ibeatles/ui/` directory
- Custom widgets are in `src/ibeatles/widgets/`
- Use QtPy for Qt compatibility abstraction
- Follow the existing patterns for signal/slot connections
- Test GUI changes manually as GUI tests are limited

### Data Handling
- Use h5py for HDF5 file operations
- Use numpy arrays for numerical data
- Use pydantic for configuration validation
- Handle large datasets efficiently (this is a scientific application)

## Dependencies

### Adding New Dependencies
1. Add to `pyproject.toml` under `[project.dependencies]`
2. Add to `[tool.pixi.dependencies]` for conda environment
3. Update `environment.yml` if needed
4. Run dependency security checks
5. Document the reason for the new dependency

### Updating Dependencies
- Be cautious with major version updates
- Test thoroughly after updates, especially for scientific libraries
- Check compatibility with both PyPI and conda distributions

## Domain-Specific Knowledge

### Neutron Imaging
- This application works with neutron imaging data
- Key concepts: Bragg edges, strain mapping, fitting algorithms
- Data often comes from neutron beam experiments
- Precision and scientific accuracy are critical

### File Formats
- Works with various image formats (via Pillow)
- HDF5 files for structured data (h5py)
- Configuration files in TOML format
- Results and metadata handling

## Common Pitfalls

1. **Qt Event Loop**: Be careful with blocking operations in GUI code
2. **Large Data**: Consider memory usage when working with image arrays
3. **Cross-platform**: Code should work on both Linux and macOS (see pyproject.toml platforms)
4. **Dependencies**: Some dependencies come from `neutronimaging` conda channel
5. **Version Management**: Uses versioningit - don't manually edit version strings

## Documentation

- Docstrings should be clear and follow existing patterns
- Complex algorithms should have explanatory comments
- Update README.md for user-facing changes
- Consider adding examples for new features

## Best Practices

1. **Minimal Changes**: Make the smallest possible changes to achieve the goal
2. **Test First**: Write or update tests before or alongside code changes
3. **Incremental Development**: Commit small, logical changes frequently
4. **Code Review**: All changes should be reviewable and understandable
5. **Scientific Rigor**: Maintain accuracy and precision in calculations
6. **User Experience**: Consider the impact on GUI users and CLI users
7. **Performance**: Be mindful of performance with large datasets
8. **Error Handling**: Provide helpful error messages for users

## Additional Notes

- The project uses MIT license
- Maintained by ORNL neutron imaging team
- Published to both PyPI and conda-forge
- Has a DOI for citation purposes
- Used in actual scientific research - correctness is paramount
