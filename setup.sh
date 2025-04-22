#!/bin/bash

# Make the MCP script executable
chmod +x pythonanywhere_mcp.py

# Install dependencies
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please edit it with your PythonAnywhere credentials."
fi

echo "Setup complete!"
echo "Next steps:"
echo "1. Edit the .env file with your PythonAnywhere API token and username"
echo "2. Configure the MCP with: ./pythonanywhere_mcp.py configure"
