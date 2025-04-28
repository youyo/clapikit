
import os
import sys
import click
import json
from pathlib import Path
from typing import Dict, Any, Optional
from .parser import OpenAPIParser
from .client import APIClient

class DynamicCLI:
    """Dynamic CLI generator based on OpenAPI specifications."""
    
    def __init__(self):
        """Initialize the dynamic CLI."""
        self.spec = None
        self.client = None
        self.commands = {}
    
    def load_spec(self, spec_file: str, server: Optional[str] = None):
        """Load OpenAPI specification and initialize client."""
        try:
            parser = OpenAPIParser(spec_file)
            self.spec = parser.parse()
            
            if server:
                click.echo(f"Overriding server URL with: {server}")
                self.spec.server_url = server
            
            self.client = APIClient(self.spec)
            click.echo(f"Using server: {self.spec.server_url}")
            
            self.create_commands()
            
        except Exception as e:
            click.echo(f"Error: {str(e)}", err=True)
            sys.exit(1)
    
    def create_commands(self):
        """Create dynamic commands based on the OpenAPI specification."""
        if not self.spec:
            return
            
        for path, methods in self.spec.paths.items():
            for method, details in methods.items():
                operation_id = details.get('operationId', f"{method}_{path.replace('/', '_').strip('_')}")
                summary = details.get('summary', 'No description')
                
                cmd_func = self.create_command_function(path, method, details)
                
                cmd_func.__name__ = operation_id
                cmd_func.__doc__ = f"{summary} [{method.upper()} {path}]"
                
                cli.command(name=operation_id)(cmd_func)
                
                self.commands[operation_id] = {
                    'path': path,
                    'method': method,
                    'summary': summary
                }
    
    def create_command_function(self, path: str, method: str, details: Dict[str, Any]):
        """Create a command function for a specific endpoint."""
        cli_instance = self
        
        @click.option('--data', '-d', help='JSON data to send in the request body')
        @click.option('--params', '-p', help='Query parameters as JSON')
        @click.option('--headers', '-H', help='Headers as JSON')
        @click.option('--output', '-o', type=click.Choice(['json', 'text']), default='json', 
                     help='Output format')
        def command_function(data=None, params=None, headers=None, output='json'):
            """Dynamic command function template."""
            try:
                request_data = json.loads(data) if data else None
                request_params = json.loads(params) if params else None
                request_headers = json.loads(headers) if headers else None
                
                if not cli_instance.client:
                    raise ValueError("API client not initialized. Please provide a valid OpenAPI spec.")
                
                response = cli_instance.client.request(
                    path=path,
                    method=method,
                    json=request_data,
                    params=request_params,
                    headers=request_headers
                )
                
                if output == 'json' and response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        click.echo(json.dumps(response.json(), indent=2))
                    except json.JSONDecodeError:
                        click.echo(response.text)
                else:
                    click.echo(response.text)
                
                click.echo(f"\nStatus: {response.status_code}")
                
            except Exception as e:
                click.echo(f"Error: {str(e)}", err=True)
                sys.exit(1)
        
        return command_function

dynamic_cli = DynamicCLI()

@click.group()
@click.version_option()
@click.option('--spec', '-s', required=True, help='Path or URL to OpenAPI specification')
@click.option('--server', help='Override server URL from the OpenAPI spec')
@click.pass_context
def cli(ctx, spec, server):
    """CLI tool for OpenAPI specifications."""
    if ctx.invoked_subcommand is None and '--help' not in sys.argv and '-h' not in sys.argv:
        dynamic_cli.load_spec(spec, server)
        
        if ctx.invoked_subcommand is None:
            click.echo("\nAvailable commands:")
            for cmd_name, cmd_info in dynamic_cli.commands.items():
                click.echo(f"  {cmd_name} - {cmd_info['summary']} [{cmd_info['method'].upper()} {cmd_info['path']}]")

def main():
    """Entry point for the CLI."""
    cli()

if __name__ == "__main__":
    main()
