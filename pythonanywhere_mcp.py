#!/usr/bin/env python3
"""
PythonAnywhere MCP (Model-Controller-Provider)
This script provides functionality to push local changes to PythonAnywhere.
"""

import os
import sys
import json
import argparse
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class PythonAnywhereClient:
    """Client for interacting with PythonAnywhere API"""
    
    def __init__(self, api_token=None):
        """Initialize the PythonAnywhere client with API token"""
        self.api_token = api_token or os.getenv('PYTHONANYWHERE_API_TOKEN')
        if not self.api_token:
            raise ValueError("API token not provided and not found in environment variables")
        
        self.username = os.getenv('PYTHONANYWHERE_USERNAME')
        if not self.username:
            raise ValueError("PythonAnywhere username not found in environment variables")
        
        self.api_base_url = f"https://www.pythonanywhere.com/api/v0/user/{self.username}"
        self.headers = {"Authorization": f"Token {self.api_token}"}
    
    def list_files(self, path):
        """List files in a directory on PythonAnywhere"""
        endpoint = f"{self.api_base_url}/files/path{path}"
        response = requests.get(endpoint, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error listing files: {response.status_code} - {response.text}")
            return None
    
    def upload_file(self, local_path, remote_path):
        """Upload a file to PythonAnywhere"""
        if not os.path.exists(local_path):
            print(f"Error: Local file {local_path} does not exist")
            return False
        
        with open(local_path, 'rb') as file:
            content = file.read()
        
        endpoint = f"{self.api_base_url}/files/path{remote_path}"
        response = requests.post(
            endpoint, 
            headers=self.headers,
            files={"content": content}
        )
        
        if response.status_code in (200, 201):
            print(f"Successfully uploaded {local_path} to {remote_path}")
            return True
        else:
            print(f"Error uploading file: {response.status_code} - {response.text}")
            return False
    
    def create_directory(self, path):
        """Create a directory on PythonAnywhere"""
        endpoint = f"{self.api_base_url}/files/path{path}"
        response = requests.post(
            endpoint,
            headers=self.headers,
            json={"operation": "mkdir"}
        )
        
        if response.status_code in (200, 201):
            print(f"Successfully created directory {path}")
            return True
        else:
            print(f"Error creating directory: {response.status_code} - {response.text}")
            return False
    
    def reload_web_app(self):
        """Reload the web app on PythonAnywhere"""
        endpoint = f"{self.api_base_url}/webapps/{self.username}.pythonanywhere.com/reload/"
        response = requests.post(endpoint, headers=self.headers)
        
        if response.status_code == 200:
            print("Successfully reloaded web app")
            return True
        else:
            print(f"Error reloading web app: {response.status_code} - {response.text}")
            return False


class PythonAnywhereMCP:
    """Model-Controller-Provider for PythonAnywhere"""
    
    def __init__(self):
        """Initialize the MCP"""
        self.client = PythonAnywhereClient()
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_config.json")
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from JSON file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            # Default config
            default_config = {
                "local_root_dir": "",
                "remote_root_dir": "",
                "excluded_paths": [".git", "__pycache__", "*.pyc", ".env"],
                "auto_reload": True
            }
            return default_config
    
    def _save_config(self):
        """Save configuration to JSON file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def configure(self, local_root_dir=None, remote_root_dir=None, excluded_paths=None, auto_reload=None):
        """Configure the MCP"""
        if local_root_dir:
            self.config["local_root_dir"] = os.path.abspath(local_root_dir)
        
        if remote_root_dir:
            self.config["remote_root_dir"] = remote_root_dir
        
        if excluded_paths is not None:
            self.config["excluded_paths"] = excluded_paths
        
        if auto_reload is not None:
            self.config["auto_reload"] = auto_reload
        
        self._save_config()
        print("Configuration saved successfully")
    
    def _should_ignore(self, path):
        """Check if a path should be ignored based on excluded_paths"""
        for pattern in self.config["excluded_paths"]:
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                if os.path.basename(path).startswith(prefix):
                    return True
            elif pattern in path:
                return True
        return False
    
    def push_directory(self, local_dir=None, remote_dir=None, create_dirs=True):
        """Push a directory and its contents to PythonAnywhere"""
        local_dir = local_dir or self.config["local_root_dir"]
        remote_dir = remote_dir or self.config["remote_root_dir"]
        
        if not local_dir or not remote_dir:
            print("Error: Local and remote directories must be specified")
            return False
        
        print(f"Pushing directory {local_dir} to {remote_dir}")
        
        for root, dirs, files in os.walk(local_dir):
            # Create relative path from local_dir
            rel_path = os.path.relpath(root, local_dir)
            if rel_path == ".":
                rel_path = ""
            
            # Skip ignored directories
            if self._should_ignore(rel_path):
                continue
            
            # Create remote directory if it doesn't exist and create_dirs is True
            if create_dirs and rel_path:
                remote_path = os.path.join(remote_dir, rel_path).replace("\\", "/")
                self.client.create_directory(remote_path)
            
            # Upload files
            for file in files:
                if self._should_ignore(file):
                    continue
                
                local_file_path = os.path.join(root, file)
                
                # Calculate remote file path
                if rel_path:
                    remote_file_path = os.path.join(remote_dir, rel_path, file).replace("\\", "/")
                else:
                    remote_file_path = os.path.join(remote_dir, file).replace("\\", "/")
                
                # Upload the file
                self.client.upload_file(local_file_path, remote_file_path)
        
        # Reload web app if auto_reload is enabled
        if self.config["auto_reload"]:
            self.client.reload_web_app()
        
        return True
    
    def push_file(self, local_file, remote_file=None):
        """Push a single file to PythonAnywhere"""
        if not os.path.exists(local_file):
            print(f"Error: Local file {local_file} does not exist")
            return False
        
        if not remote_file:
            # Use the same path relative to local_root_dir
            if not self.config["local_root_dir"] or not self.config["remote_root_dir"]:
                print("Error: local_root_dir and remote_root_dir must be configured")
                return False
            
            rel_path = os.path.relpath(local_file, self.config["local_root_dir"])
            remote_file = os.path.join(self.config["remote_root_dir"], rel_path).replace("\\", "/")
        
        # Make sure the remote directory exists
        remote_dir = os.path.dirname(remote_file)
        if remote_dir:
            self.client.create_directory(remote_dir)
        
        # Upload the file
        result = self.client.upload_file(local_file, remote_file)
        
        # Reload web app if auto_reload is enabled and file was uploaded successfully
        if result and self.config["auto_reload"]:
            self.client.reload_web_app()
        
        return result


def main():
    """Main function to run the MCP from command line"""
    parser = argparse.ArgumentParser(description="PythonAnywhere MCP - Push changes to PythonAnywhere")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Configure command
    config_parser = subparsers.add_parser("configure", help="Configure the MCP")
    config_parser.add_argument("--local-dir", help="Local root directory")
    config_parser.add_argument("--remote-dir", help="Remote root directory on PythonAnywhere")
    config_parser.add_argument("--excluded", nargs="*", help="Patterns to exclude")
    config_parser.add_argument("--auto-reload", type=bool, help="Automatically reload web app after pushing changes")
    
    # Push directory command
    push_dir_parser = subparsers.add_parser("push-dir", help="Push a directory to PythonAnywhere")
    push_dir_parser.add_argument("--local-dir", help="Local directory to push (default: configured local_root_dir)")
    push_dir_parser.add_argument("--remote-dir", help="Remote directory on PythonAnywhere (default: configured remote_root_dir)")
    push_dir_parser.add_argument("--no-create-dirs", action="store_false", dest="create_dirs", help="Don't create directories on PythonAnywhere")
    
    # Push file command
    push_file_parser = subparsers.add_parser("push-file", help="Push a file to PythonAnywhere")
    push_file_parser.add_argument("local_file", help="Local file to push")
    push_file_parser.add_argument("--remote-file", help="Remote file path on PythonAnywhere (default: same relative path as local file)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create MCP instance
    mcp = PythonAnywhereMCP()
    
    # Execute command
    if args.command == "configure":
        mcp.configure(
            local_root_dir=args.local_dir,
            remote_root_dir=args.remote_dir,
            excluded_paths=args.excluded,
            auto_reload=args.auto_reload
        )
    elif args.command == "push-dir":
        mcp.push_directory(
            local_dir=args.local_dir,
            remote_dir=args.remote_dir,
            create_dirs=args.create_dirs
        )
    elif args.command == "push-file":
        mcp.push_file(
            local_file=args.local_file,
            remote_file=args.remote_file
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
