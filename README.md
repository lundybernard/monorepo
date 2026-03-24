# mono - Python CLI Template

[![PyPI](https://img.shields.io/pypi/v/mono)](https://pypi.org/project/mono/)
[![Python](https://img.shields.io/pypi/pyversions/mono)](https://pypi.org/project/mono/)
[![License](https://img.shields.io/github/license/guenp/mono)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/guenp/mono/pytest.yml?label=tests)](https://github.com/guenp/mono/actions/workflows/pytest.yml)

<img src="logo.svg" align="right" width="150" />

A minimal, production-ready template for Python CLI tools. Get started building your CLI in minutes with modern tooling, comprehensive testing, and CI/CD out of the box.

**Features**

This template provides:

- **Modern Python packaging** with [hatchling](https://hatch.pypa.io/) and [hatch-vcs](https://github.com/ofek/hatch-vcs) for automatic versioning
- **CLI framework** using [Typer](https://typer.tiangolo.com/) with type hints and autocomplete support
- **Configuration management** with [batconf](https://github.com/lundybernard/batconf) — layered config from CLI args, environment variables, INI files, and dataclass defaults
- **Code quality** with [Ruff](https://docs.astral.sh/ruff/) for linting/formatting and [mypy](https://mypy-lang.org/) for type checking
- **Testing** with [pytest](https://pytest.org/) and coverage reporting
- **Pre-commit hooks** configured and ready to use
- **CI/CD** with GitHub Actions (testing on multiple platforms/Python versions)
- **Documentation** infrastructure with [Zensical](https://github.com/zensical/zensical)
- **Automatic releases** to PyPI when you tag versions

## Using This Template

### 1. Create Your Repository

Click "Use this template" on GitHub or:

```bash
git clone https://github.com/guenp/mono.git my-cli-tool
cd my-cli-tool
rm -rf .git && git init
```

### 2. Customize the Package

**Choose your structure:**

**Option A: Simple single package** (recommended for most projects)

Remove the example subpackages:
```bash
rm -rf mono-core mono-one mono-two
```

Then update `pyproject.toml` to remove the subpackage dependencies:
```toml
dependencies = [
    "typer>=0.15",
    # Remove: mono-core, mono-one, mono-two
]
# Remove the [tool.uv.sources] section
```

**Option B: Keep the monorepo structure**

Keep the subpackages and customize them for your needs.

**Then, for either option:**

Replace all occurrences of `mono` with your package name:

```bash
# macOS
find . -type f -not -path './.git/*' -exec sed -i '' 's/mono/yourpackage/g' {} +

# Linux
find . -type f -not -path './.git/*' -exec sed -i 's/mono/yourpackage/g' {} +
```

Rename the package directory:

```bash
mv src/mono src/yourpackage
# If keeping subpackages, rename those too:
# mv mono-core yourpackage-core
# mv mono-one yourpackage-one
# etc.
```

Update `pyproject.toml`:
- Change `name`, `description`, and `authors`
- Update repository URLs
- Adjust dependencies as needed

### 3. Install Development Environment

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync --group dev --group docs

# Install pre-commit hooks
uv run pre-commit install
```

### 4. Start Building

Replace the example `hello` command in `src/yourpackage/cli.py` with your own commands:

```python
@app.command()
def yourcommand(
    arg: str = typer.Argument(..., help="Description"),
    flag: bool = typer.Option(False, "--flag", help="Enable feature"),
) -> None:
    """Your command description."""
    # Your implementation here
    typer.echo(f"Running with {arg}")
```

## Quick Start (Using This Template As-Is)

Install the example CLI:

```bash
uv tool install mono
# or: uvx mono hello World
```

Try it out:

```bash
mono hello
# Output: Hello, World!

mono hi Alice
# Output: Hi, Alice!

mono bye Bob
# Output: Goodbye, Bob!

mono --help
# See available options
```

This example demonstrates the monorepo structure with three subpackages (`mono-core`, `mono-one`, `mono-two`). The CLI imports from these subpackages to show how they work together.

## Configuration Management

This template uses [batconf](https://github.com/lundybernard/batconf) for layered configuration. Values are resolved in priority order:

1. **CLI arguments** (highest priority)
2. **Environment variables**
3. **INI configuration file**
4. **Dataclass defaults** (lowest priority)

### Defining Your Config Schema

Configuration is defined as dataclasses in `src/yourpackage/conf.py`. Each field maps to a config key. Required fields have no default; optional fields have one:

```python
# src/yourpackage/conf.py
from dataclasses import dataclass


@dataclass
class YourPackageConfig:
    api_key: str  # required — must be set via CLI, env var, or config file
    name: str = "World"  # optional — falls back to default
```

Subpackages define their own schemas and expose them to the top-level config:

```python
# yourpackage-myfeature/src/yourpackage_myfeature/conf.py
@dataclass
class MyFeatureConfig:
    host: str = "localhost"
    port: int = 8080
```

```python
# src/yourpackage/conf.py
from yourpackage_myfeature.conf import MyFeatureConfig


@dataclass
class YourPackageConfig:
    api_key: str
    name: str = "World"
    myfeature: MyFeatureConfig
```

### INI Configuration File

Create a `config.ini` in your working directory. Use sections to define environments:

```ini
[batconf]
default_env = dev

[dev]
[dev.yourpackage]
name = Alice

[dev.yourpackage.myfeature]
host = dev.example.com
port = 9090

[prod]
[prod.yourpackage.myfeature]
host = prod.example.com
```

Select an environment at runtime with the `--env` flag or the `BATCONF_ENV` environment variable:

```bash
mono --env test config
# or
BATCONF_ENV=test mono config
```

### Environment Variables

Config keys map to environment variables by uppercasing the dotted path. For example, `yourpackage.myfeature.host` maps to `YOURPACKAGE_MYFEATURE_HOST`:

```bash
export YOURPACKAGE_API_KEY=secret
export YOURPACKAGE_MYFEATURE_HOST=staging.example.com
yourpackage mycommand
```

### Using Config in Commands

Load configuration inside a command via `get_config()`, passing any CLI overrides through the Typer context:

```python
# src/yourpackage/cli.py
from .conf import get_config


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    env: str | None = typer.Option(
        None,
        "--env",
        "-e",
        help="Config environment"
    ),
    name: str | None = typer.Option(None, "--name", "-n"),
) -> None:
    ctx.ensure_object(dict)
    ctx.obj = {"batconf.env": env, "yourpackage.name": name}


@app.command()
def greet(ctx: typer.Context) -> None:
    """Greet someone using config."""
    from argparse import Namespace
    cfg = get_config(
        cli_args=Namespace(**ctx.obj),
        config_env=ctx.obj["batconf.env"]
    )
    typer.echo(f"Hello, {cfg.name}!")
```

### Changing the Config File Location

By default, `get_config()` looks for `config.ini` in the current working directory. To use a user-level config file instead, update `CONFIG_FILE_NAME` in `conf.py`:

```python
# src/yourpackage/conf.py
from pathlib import Path


CONFIG_FILE_NAME = str(Path.home() / '.config' / 'yourpackage' / 'config.ini')
```

This is a good default for tools installed system-wide, as it keeps configuration in a standard, user-writable location. Users can still override individual values via environment variables or CLI flags without touching the file.

### Inspecting Config

The `config` command (defined in `cli.py`) prints the resolved configuration and its sources:

```bash
yourpackage config
```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=yourpackage

# Run specific test
uv run pytest tests/test_yourpackage.py::test_hello_default
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type check
uv run mypy src tests

# Run all pre-commit hooks
uv run pre-commit run --all-files
```

### Building and Publishing

The template includes automatic PyPI publishing via GitHub Actions when you push a tag:

```bash
# Create a new version tag
git tag v0.1.0
git push origin v0.1.0
```

Or build locally:

```bash
# Build wheel and sdist
uv build

# Install your local build
uv pip install dist/yourpackage-*.whl
```

### Documentation

Documentation is built with Zensical:

```bash
# Build docs
uv run zensical build

# Serve docs locally
uv run zensical serve
```

Update the docs in the `docs/` directory and customize `zensical.toml`.

## Project Structure

This template supports two project structures:

### Simple Single Package (Recommended for Most Projects)

```
.
├── .github/
│   └── workflows/        # CI/CD workflows (tests, release, docs)
├── docs/                 # Documentation source files
│   ├── index.md
│   ├── getting-started.md
│   └── usage.md
├── src/
│   └── yourpackage/
│       ├── __init__.py   # Package initialization
│       ├── cli.py        # CLI commands (Typer app)
│       └── _version.py   # Auto-generated version file
├── tests/
│   ├── conftest.py       # Pytest configuration
│   └── test_yourpackage.py
├── pyproject.toml        # Package metadata and tool configuration
├── zensical.toml         # Documentation configuration
└── CLAUDE.md             # Development notes for AI assistants
```

### Monorepo with Multiple Subpackages (Optional)

If you need to split your project into multiple independently installable packages:

```
.
├── .github/
├── docs/
├── yourpackage-core/          # Separate subpackage
│   ├── pyproject.toml
│   ├── README.md
│   └── src/
│       └── yourpackage_core/
│           ├── __init__.py
│           └── core.py
├── yourpackage-one/           # Another subpackage
│   ├── pyproject.toml
│   ├── README.md
│   └── src/
│       └── yourpackage_one/
│           ├── __init__.py
│           └── feature.py
├── src/
│   └── yourpackage/           # Main CLI package
│       ├── __init__.py
│       └── cli.py
├── tests/
├── pyproject.toml             # Main project config
└── zensical.toml
```

**When to use the monorepo structure:**
- You need to publish multiple packages separately to PyPI
- Different parts of your project have different dependencies
- You want to version subpackages independently
- You're building a plugin ecosystem or modular toolkit

**For the monorepo structure:**
1. Each subpackage has its own `pyproject.toml` with independent configuration
2. Package names use underscores for imports (e.g., `yourpackage_core`)
3. The main `pyproject.toml` references subpackages using `[tool.uv.sources]`
4. Each subpackage can be installed and published independently

See the example structure in this repository (`mono-core`, `mono-one`, `mono-two`) for reference.

## What's Included

### Dependencies

**Core:**
- `typer>=0.15` - CLI framework with rich features
- `batconf` - Layered configuration management

**Development:**
- `pytest>=8` - Testing framework
- `pytest-cov>=4` - Coverage reporting
- `mypy>=1.14` - Static type checker
- `ruff>=0.9` - Fast linter and formatter
- `pre-commit>=4` - Git hook framework

**Documentation:**
- `zensical` - Documentation builder
- `markdown-gfm-admonition` - Enhanced markdown support

### CI/CD Workflows

1. **pytest.yml** - Runs tests on Python 3.12+ across Linux, macOS, and Windows
2. **release.yml** - Publishes to PyPI when you tag a version
3. **docs.yml** - Builds and deploys documentation to GitHub Pages

### Configuration Files

- **pyproject.toml** - All tool configuration in one place
- **zensical.toml** - Documentation site settings
- **.pre-commit-config.yaml** - Pre-commit hook configuration
- **CLAUDE.md** - Project context for AI coding assistants

## Customization Examples

### Adding a New Command

```python
# src/yourpackage/cli.py

@app.command()
def process(
    input_file: Path = typer.Argument(..., help="Input file to process"),
    output: Path | None = typer.Option(None, "--output", "-o"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Process a file and optionally save results."""
    if verbose:
        typer.echo(f"Processing {input_file}")

    # Your logic here
    result = do_processing(input_file)

    if output:
        output.write_text(result)
        typer.echo(f"Saved to {output}")
    else:
        typer.echo(result)
```

### Adding Dependencies

```bash
# Add a runtime dependency
uv add requests

# Add a dev dependency
uv add --group dev ipython

# Update lockfile
uv lock
```

### Adding Tests

```python
# tests/test_yourpackage.py

def test_process_command() -> None:
    """Test the process command."""
    result = runner.invoke(app, ["process", "input.txt"])
    assert result.exit_code == 0
    assert "Processing" in result.stdout
```

## Why This Template?

This template embodies Python packaging best practices as of 2025:

- **`pyproject.toml`** - Single source of truth for all configuration
- **`src/` layout** - Prevents accidental imports of uninstalled code
- **Type hints** - Full type coverage with mypy
- **Modern tools** - Ruff (fast) instead of multiple slower tools
- **Comprehensive CI** - Test across platforms and Python versions
- **Automatic versioning** - Git tags become package versions
- **Developer experience** - Pre-commit hooks catch issues before CI

## Contributing

Contributions are welcome! This template is designed to be:

- **Minimal** - Only essential features, easy to understand
- **Modern** - Uses current best practices and tools
- **Practical** - Everything works out of the box

Please open an issue or PR if you have suggestions.

## License

MIT - feel free to use this template for any project.

## Acknowledgments

Built with modern Python tooling:
- [Typer](https://typer.tiangolo.com/) for the CLI framework
- [Hatch](https://hatch.pypa.io/) for packaging
- [Ruff](https://docs.astral.sh/ruff/) for linting and formatting
- [uv](https://github.com/astral-sh/uv) for fast dependency management

This template is inspired by https://github.com/basnijholt/trueloc.
