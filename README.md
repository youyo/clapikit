# clapikit

CLI tool for OpenAPI specifications.

## Description

clapikit (CLI + API + Kit) is a command-line tool that parses OpenAPI YAML/JSON files and provides a CLI interface to interact with APIs defined in those specifications. It dynamically generates subcommands based on the endpoints defined in the OpenAPI specification.

## Installation

```bash
# Install with uvx
uvx clapikit

# Or install with pip
pip install clapikit
```

## Usage

```bash
# List available commands from an OpenAPI specification
clapikit --spec https://example.com/openapi.yaml

# Execute an API endpoint
clapikit --spec https://example.com/openapi.yaml getUserInfo

# Override server URL
clapikit --spec https://example.com/openapi.yaml --server http://custom-server:8080 getUserInfo

# Enable debug output
clapikit --spec https://example.com/openapi.yaml --debug getUserInfo

# Send data with a request
clapikit --spec https://example.com/openapi.yaml createUser --data '{"name": "John", "email": "john@example.com"}'

# Specify query parameters
clapikit --spec https://example.com/openapi.yaml searchUsers --params '{"role": "admin", "limit": 10}'

# Set custom headers
clapikit --spec https://example.com/openapi.yaml getUserInfo --headers '{"Authorization": "Bearer token123"}'

# Control output format
clapikit --spec https://example.com/openapi.yaml getUserInfo --output text
```

## Features

- Parse OpenAPI YAML/JSON files from local paths or URLs
- Dynamically generate subcommands based on API endpoints
- Execute API requests directly from the command line
- Override server URL from command line
- Debug mode for detailed logging
- Support for request data, query parameters, and headers
- JSON and text output formats

## Development

```bash
# Clone the repository
git clone https://github.com/youyo/clapikit.git
cd clapikit

# Install development dependencies
uv pip install -e .

# Run tests
python test_cli.py
```

## Mock Server for Testing

You can use Prism to run a mock server for testing:

```bash
npx @stoplight/prism-cli mock https://learn.openapis.org/examples/v3.0/api-with-examples.yaml
```

## License

See the LICENSE file for details.
