# Network Configuration Generator (NCG) - AI Base

Automated network switch configuration generation from ServiceNow Configuration Items using Jinja2 templates with SecretServer integration.

## Features

- **ServiceNow Integration**: Query devices with hardware states "planned" or "in use"
- **Jinja2 Template Engine**: Template inheritance by manufacturer → OS → model
- **Device-Specific Overrides**: Support YAML/JSON override files for per-device customization
- **SecretServer Integration**: Retrieve secrets for device configurations
- **CLI & CI/CD Ready**: Full command-line interface and pipeline automation support
- **Data Merge Pipeline**: Combine ServiceNow data, device overrides, and secrets seamlessly

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/jcarswell/NCG_AI_Base.git
cd NCG_AI_Base

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Basic Usage

```bash
# Show help
ncg --help

# Generate configurations (dry-run)
ncg generate --servicenow-url https://your-instance.service-now.com \
             --servicenow-user admin \
             --servicenow-password password \
             --dry-run

# Generate with device overrides
ncg generate --servicenow-url https://your-instance.service-now.com \
             --servicenow-user admin \
             --servicenow-password password \
             --device-overrides ./overrides/ \
             --output ./configs/

# Use environment variables
export SERVICENOW_URL=https://your-instance.service-now.com
export SERVICENOW_USER=admin
export SERVICENOW_PASSWORD=password
ncg generate --dry-run
```

## Project Structure

```
NCG_AI_Base/
├── src/network_config_gen/
│   ├── __init__.py
│   ├── cli.py                    # CLI interface
│   ├── config.py                 # Configuration management
│   ├── exceptions.py             # Custom exceptions
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── servicenow.py         # ServiceNow API client
│   │   ├── secretserver.py       # SecretServer API client
│   │   └── mock_data.py          # Mock data for testing
│   ├── templates/
│   │   ├── loader.py             # Template loader with inheritance
│   │   └── (template files)
│   ├── generators/
│   │   ├── __init__.py
│   │   └── config_generator.py   # Configuration generation engine
│   └── utils/
│       ├── __init__.py
│       ├── merge.py              # Data merging logic
│       └── validators.py         # Input validation
├── tests/                        # Comprehensive test suite
├── docs/                         # Documentation
├── examples/                     # Example files and CI/CD templates
└── pyproject.toml                # Project configuration
```

## Configuration

### Environment Variables

```bash
# ServiceNow
export SERVICENOW_URL=https://your-instance.service-now.com
export SERVICENOW_USER=admin
export SERVICENOW_PASSWORD=password

# SecretServer
export SECRETSERVER_URL=https://your-secretserver.com
export SECRETSERVER_USER=admin
export SECRETSERVER_PASSWORD=password

# Template paths
export TEMPLATE_DIR=./templates
export DEVICE_OVERRIDE_DIR=./overrides
export OUTPUT_DIR=./output
```

### Device Override File Format

See `examples/device-override.yaml` and `examples/device-override.json` for format examples.

## Template Hierarchy

Templates are resolved in the following order (first match wins):

1. **Model-specific**: `templates/{manufacturer}/{os}/{model}.j2`
2. **OS-specific**: `templates/{manufacturer}/{os}/base.j2`
3. **Manufacturer base**: `templates/{manufacturer}/base.j2`
4. **Global base**: `templates/base.j2`

## Integration Setup

### ServiceNow

1. Create a ServiceNow API user with read access to CMDB
2. Set credentials in environment variables or pass via CLI
3. Ensure hardware state filter is set to "planned" or "in use"

### SecretServer

1. Configure SecretServer API credentials
2. Create secrets for device credentials (username, passwords, etc.)
3. Reference secrets by ID in device override files

## Development

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/network_config_gen

# Run specific test file
pytest tests/test_cli.py
```

### Code Formatting

```bash
# Format with black
black src/ tests/

# Sort imports
isort src/ tests/

# Lint with flake8
flake8 src/ tests/

# Type checking
mypy src/
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

## CI/CD Integration

See `examples/ci-example.yml` for GitHub Actions workflow example.

### GitHub Actions Example

```yaml
name: Generate Switch Configs

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -e .
      
      - name: Generate configurations
        env:
          SERVICENOW_URL: ${{ secrets.SERVICENOW_URL }}
          SERVICENOW_USER: ${{ secrets.SERVICENOW_USER }}
          SERVICENOW_PASSWORD: ${{ secrets.SERVICENOW_PASSWORD }}
        run: ncg generate --output ./configs/
      
      - name: Commit and push
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add configs/
          git commit -m "Update switch configurations" || echo "No changes"
          git push
```

## Documentation

- [CLI Usage Guide](docs/cli-usage.md)
- [Template Configuration](docs/templates.md)
- [Integration Setup](docs/integration-setup.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes and add tests
4. Run `pytest` and linting tools
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or feature requests, please open a GitHub issue.
