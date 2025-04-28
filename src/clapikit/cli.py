
import os
import sys
import click
from pathlib import Path
from .parser import OpenAPIParser
from .client import APIClient

@click.group()
@click.version_option()
def cli():
    """CLI tool for OpenAPI specifications."""
    pass

@cli.command()
@click.argument('spec_file', type=click.Path(exists=True))
@click.option('--server', help='Override server URL from the OpenAPI spec')
def run(spec_file, server):
    """Run commands based on OpenAPI specification."""
    try:
        parser = OpenAPIParser(spec_file)
        spec = parser.parse()
        
        if server:
            click.echo(f"Overriding server URL with: {server}")
            spec.server_url = server
        
        client = APIClient(spec)
        click.echo(f"Using server: {spec.server_url}")
        
        click.echo("\nAvailable endpoints:")
        for path, methods in spec.paths.items():
            for method, details in methods.items():
                operation_id = details.get('operationId', f"{method} {path}")
                summary = details.get('summary', 'No description')
                click.echo(f"  {method.upper()} {path} - {operation_id}: {summary}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

def main():
    """Entry point for the CLI."""
    cli()

if __name__ == "__main__":
    main()
