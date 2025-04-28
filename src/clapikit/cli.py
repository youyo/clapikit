
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
            
            return True
        except Exception as e:
            click.echo(f"Error: {str(e)}", err=True)
            return False
    
    def create_commands(self):
        """Create dynamic commands based on the OpenAPI specification."""
        if not self.spec:
            return
        
        self.commands = {}
        
        for path, methods in self.spec.paths.items():
            for method, details in methods.items():
                operation_id = details.get('operationId', f"{method}_{path.replace('/', '_').strip('_')}")
                summary = details.get('summary', 'No description')
                
                self.commands[operation_id] = {
                    'path': path,
                    'method': method,
                    'summary': summary,
                    'details': details
                }
    
    def execute_command(self, command_name: str, data=None, params=None, headers=None, output='json'):
        """Execute a command by name."""
        if not self.client:
            raise ValueError("API client not initialized. Please provide a valid OpenAPI spec.")
        
        if command_name not in self.commands:
            raise ValueError(f"Command '{command_name}' not found.")
        
        cmd_info = self.commands[command_name]
        path = cmd_info['path']
        method = cmd_info['method']
        
        request_data = json.loads(data) if data else None
        request_params = json.loads(params) if params else None
        request_headers = json.loads(headers) if headers else None
        
        response = self.client.request(
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
        
        return response

dynamic_cli = DynamicCLI()

@click.group(invoke_without_command=True)
@click.version_option()
@click.option('--spec', '-s', required=True, help='Path or URL to OpenAPI specification')
@click.option('--server', help='Override server URL from the OpenAPI spec')
@click.pass_context
def cli(ctx, spec, server):
    """CLI tool for OpenAPI specifications."""
    ctx.ensure_object(dict)
    ctx.obj['spec'] = spec
    ctx.obj['server'] = server
    
    if not dynamic_cli.load_spec(spec, server):
        return
    
    if ctx.invoked_subcommand is None:
        click.echo("\nAvailable commands:")
        for cmd_name, cmd_info in sorted(dynamic_cli.commands.items()):
            click.echo(f"  {cmd_name} - {cmd_info['summary']} [{cmd_info['method'].upper()} {cmd_info['path']}]")

def add_dynamic_commands():
    """Add dynamic commands to the CLI based on the OpenAPI spec."""
    for cmd_name, cmd_info in dynamic_cli.commands.items():
        def make_callback(name):
            def callback(data=None, params=None, headers=None, output='json'):
                return dynamic_cli.execute_command(name, data, params, headers, output)
            return callback
        
        @click.command(name=cmd_name, help=f"{cmd_info['summary']} [{cmd_info['method'].upper()} {cmd_info['path']}]")
        @click.option('--data', '-d', help='JSON data to send in the request body')
        @click.option('--params', '-p', help='Query parameters as JSON')
        @click.option('--headers', '-H', help='Headers as JSON')
        @click.option('--output', '-o', type=click.Choice(['json', 'text']), default='json', help='Output format')
        def command_func(data=None, params=None, headers=None, output='json'):
            return dynamic_cli.execute_command(cmd_name, data, params, headers, output)
        
        command_func.__name__ = f"command_{cmd_name}"
        
        cmd = command_func
        
        cli.add_command(cmd)

def main():
    """Entry point for the CLI."""
    spec_file = None
    server = None
    
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == '--spec' or arg == '-s':
            if i < len(sys.argv):
                spec_file = sys.argv[i]
        elif arg == '--server':
            if i < len(sys.argv):
                server = sys.argv[i]
    
    if spec_file:
        dynamic_cli.load_spec(spec_file, server)
        add_dynamic_commands()
    
    cli(obj={})

if __name__ == "__main__":
    main()
