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
        self.debug = False
    
    def load_spec(self, spec_file: str, server: Optional[str] = None, debug: bool = False):
        """Load OpenAPI specification and initialize client."""
        try:
            self.debug = debug
            parser = OpenAPIParser(spec_file)
            self.spec = parser.parse()
            
            if server:
                if debug:
                    click.echo(f"Overriding server URL with: {server}")
                self.spec.server_url = server
            
            self.client = APIClient(self.spec)
            if debug:
                click.echo(f"Using server: {self.spec.server_url}")
            
            # Create dynamic commands
            self.create_commands()
            
            return True
        except Exception as e:
            click.echo(f"Error: {str(e)}", err=True)
            return False
    
    def create_commands(self):
        """Create dynamic commands based on the OpenAPI specification."""
        if not self.spec:
            return
        
        # Clear existing commands
        self.commands = {}
        
        # Create new commands
        for path, methods in self.spec.paths.items():
            for method, details in methods.items():
                operation_id = details.get('operationId', f"{method}_{path.replace('/', '_').strip('_')}")
                summary = details.get('summary', 'No description')
                
                # Store command info
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
        
        # Parse JSON inputs
        request_data = json.loads(data) if data else None
        request_params = json.loads(params) if params else None
        request_headers = json.loads(headers) if headers else None
        
        # Make the request
        response = self.client.request(
            path=path,
            method=method,
            json=request_data,
            params=request_params,
            headers=request_headers
        )
        
        # Display response
        if output == 'json' and response.headers.get('content-type', '').startswith('application/json'):
            try:
                click.echo(json.dumps(response.json(), indent=2))
            except json.JSONDecodeError:
                click.echo(response.text)
        else:
            click.echo(response.text)
        
        # Show status code
        click.echo(f"\nStatus: {response.status_code}")
        
        return response

# Create a singleton instance
dynamic_cli = DynamicCLI()

# Create a dynamic Click command group
class DynamicGroup(click.Group):
    """Custom Group class that loads commands from OpenAPI spec."""
    
    def list_commands(self, ctx):
        """List available commands."""
        # Get spec from context
        if not dynamic_cli.commands and hasattr(ctx, 'obj') and ctx.obj:
            spec = ctx.obj.get('spec')
            server = ctx.obj.get('server')
            debug = ctx.obj.get('debug', False)
            if spec:
                dynamic_cli.load_spec(spec, server, debug)
        
        # Return command names
        return sorted(dynamic_cli.commands.keys())
    
    def get_command(self, ctx, name):
        """Get a command by name."""
        try:
            # First try to get from context
            if hasattr(ctx, 'obj') and ctx.obj:
                spec = ctx.obj.get('spec')
                server = ctx.obj.get('server')
                debug = ctx.obj.get('debug', False)
                if spec and not dynamic_cli.commands:
                    dynamic_cli.load_spec(spec, server, debug)
            
            if not dynamic_cli.commands:
                args = sys.argv
                debug = '--debug' in args
                for i, arg in enumerate(args):
                    if arg == '--spec' or arg == '-s':
                        if i + 1 < len(args):
                            spec_file = args[i + 1]
                            server = None
                            for j, arg2 in enumerate(args):
                                if arg2 == '--server':
                                    if j + 1 < len(args):
                                        server = args[j + 1]
                                        break
                            # Load spec
                            dynamic_cli.load_spec(spec_file, server, debug)
                            break
        except Exception as e:
            click.echo(f"Error loading spec: {str(e)}", err=True)
        
        # Return command if it exists
        if name in dynamic_cli.commands:
            cmd_info = dynamic_cli.commands[name]
            
            # Create a command for this endpoint
            @click.command(name=name, help=f"{cmd_info['summary']} [{cmd_info['method'].upper()} {cmd_info['path']}]")
            @click.option('--data', '-d', help='JSON data to send in the request body')
            @click.option('--params', '-p', help='Query parameters as JSON')
            @click.option('--headers', '-H', help='Headers as JSON')
            @click.option('--output', '-o', type=click.Choice(['json', 'text']), default='json', help='Output format')
            def command(data=None, params=None, headers=None, output='json'):
                return dynamic_cli.execute_command(name, data, params, headers, output)
            
            return command
        
        return None

# Main CLI group
@click.group(cls=DynamicGroup, invoke_without_command=True)
@click.version_option()
@click.option('--spec', '-s', required=True, help='Path or URL to OpenAPI specification')
@click.option('--server', help='Override server URL from the OpenAPI spec')
@click.option('--debug', is_flag=True, help='Enable debug output')
@click.pass_context
def cli(ctx, spec, server, debug):
    """CLI tool for OpenAPI specifications."""
    # Store parameters in context
    ctx.ensure_object(dict)
    ctx.obj['spec'] = spec
    ctx.obj['server'] = server
    ctx.obj['debug'] = debug
    
    # Load spec if no subcommand is provided
    if ctx.invoked_subcommand is None:
        if not dynamic_cli.load_spec(spec, server, debug):
            return
        
        # Show available commands
        click.echo("\nAvailable commands:")
        for cmd_name, cmd_info in sorted(dynamic_cli.commands.items()):
            click.echo(f"  {cmd_name} - {cmd_info['summary']} [{cmd_info['method'].upper()} {cmd_info['path']}]")

def main():
    """Entry point for the CLI."""
    cli(obj={})

if __name__ == "__main__":
    main()
