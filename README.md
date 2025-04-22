# PythonAnywhere MCP (model context protocol)

This MCP tool allows you to easily push your local Python code to your PythonAnywhere account.

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file based on the `.env.example` template:
   ```
   cp .env.example .env
   ```

3. Edit the `.env` file and add your PythonAnywhere API token and username.
   - You can create an API token at https://www.pythonanywhere.com/user/YOUR_USERNAME/account/#api_token

## Configuration

Before using the MCP, you need to configure it:

```bash
python pythonanywhere_mcp.py configure --local-dir "/path/to/your/local/project" --remote-dir "/home/your_username/path/on/pythonanywhere"
```

Optional configuration arguments:
- `--excluded`: Patterns to exclude (e.g., `--excluded .git __pycache__ *.pyc .env`)
- `--auto-reload`: Whether to automatically reload the web app after pushing changes (`True` or `False`)

## Usage

### Push a Directory

Push a directory and all its contents to PythonAnywhere:

```bash
python pythonanywhere_mcp.py push-dir
```

You can override the configured directories:

```bash
python pythonanywhere_mcp.py push-dir --local-dir "/path/to/your/local/project" --remote-dir "/home/your_username/path/on/pythonanywhere"
```

### Push a Single File

Push a single file to PythonAnywhere:

```bash
python pythonanywhere_mcp.py push-file /path/to/your/local/file.py
```

You can specify a custom remote path:

```bash
python pythonanywhere_mcp.py push-file /path/to/your/local/file.py --remote-file "/home/your_username/path/on/pythonanywhere/file.py"
```

## Example Workflow

1. Configure the MCP:
   ```bash
   python pythonanywhere_mcp.py configure --local-dir "/Users/you/myproject" --remote-dir "/home/your_username/myproject"
   ```

2. Push your entire project:
   ```bash
   python pythonanywhere_mcp.py push-dir
   ```

3. After making changes to a specific file, push just that file:
   ```bash
   python pythonanywhere_mcp.py push-file /Users/you/myproject/app.py
   ```

The MCP will automatically reload your web app after pushing changes (unless disabled in configuration).
