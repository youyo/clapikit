# clapikit

CLI tool for OpenAPI specifications.

## Description

clapikit (CLI + API + Kit) is a command-line tool that parses OpenAPI YAML/JSON files and provides a CLI interface to interact with APIs defined in those specifications.

## Installation

```bash
# Install with uvx
uvx clapikit

# Or install with pip
pip install clapikit
```

## Usage

```bash
# Basic usage
clapikit run path/to/openapi.yaml

# Override server URL
clapikit run path/to/openapi.yaml --server http://custom-server:8080
```

## Features

- Parse OpenAPI YAML/JSON files
- Override server URL from command line
- Display available endpoints and operations

## Development

```bash
# Clone the repository
git clone https://github.com/youyo/clapikit.git
cd clapikit

# Install development dependencies
uv pip install -e .
```

## License

See the LICENSE file for details.
