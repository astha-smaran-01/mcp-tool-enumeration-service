# MCP Tool Enumeration Testing Script

This script allows you to test multiple MCP server configurations against the tool enumeration API and generate comprehensive reports on the results.

## Features

- ✅ **Batch Testing**: Test multiple server configurations in a single run
- 📊 **Detailed Reporting**: Get comprehensive reports with success rates, tool counts, and error details
- ⏱️ **Configurable Timeouts**: Set custom timeout values for each test
- 💾 **JSON Output**: Save detailed results to JSON files for further analysis
- 🎯 **Health Checks**: Automatic service health verification before testing
- 🌐 **Flexible Service URLs**: Test against different service instances

## Usage

### Basic Usage

```bash
# Test with a configuration file
python scripts/test_enumeration.py --config test_configs.json

# Test with custom timeout
python scripts/test_enumeration.py --config test_configs.json --timeout 15

# Test against different service URL
python scripts/test_enumeration.py --config test_configs.json --service-url http://localhost:8080

# Save detailed results to JSON file
python scripts/test_enumeration.py --config test_configs.json --output results.json
```

### Create Sample Configuration

```bash
# Generate a sample configuration file
python scripts/test_enumeration.py --create-sample
```

## Configuration File Format

The script accepts JSON configuration files with the following structure:

```json
{
  "configurations": [
    {
      "name": "Configuration Name",
      "mcp_json": {
        "mcpServers": {
          "server_name": {
            "command": "npx",
            "args": ["mcp-remote", "https://example.com/mcp"],
            "env": {
              "API_KEY": "your-api-key"
            }
          }
        }
      }
    }
  ]
}
```

### Example Configuration

```json
{
  "configurations": [
    {
      "name": "PayPal Integration Test",
      "mcp_json": {
        "mcpServers": {
          "paypal": {
            "command": "npx",
            "args": [
              "mcp-remote",
              "https://mcp.sandbox.paypal.com/sse",
              "--header",
              "Authorization: Bearer ${PAYPAL_API_KEY}"
            ],
            "env": {
              "PAYPAL_API_KEY": "your-paypal-api-key"
            }
          }
        }
      }
    },
    {
      "name": "Multi-Service Test",
      "mcp_json": {
        "mcpServers": {
          "paypal": {
            "command": "npx",
            "args": [
              "mcp-remote",
              "https://mcp.sandbox.paypal.com/sse",
              "--header",
              "Authorization: Bearer ${PAYPAL_API_KEY}"
            ],
            "env": {
              "PAYPAL_API_KEY": "your-paypal-api-key"
            }
          },
          "linear": {
            "command": "npx",
            "args": [
              "mcp-remote",
              "https://mcp.linear.app/sse",
              "--header",
              "Authorization: Bearer ${LINEAR_API_KEY}"
            ],
            "env": {
              "LINEAR_API_KEY": "your-linear-api-key"
            }
          }
        }
      }
    }
  ]
}
```

## Command Line Options

```bash
usage: test_enumeration.py [-h] [--config CONFIG] [--service-url SERVICE_URL] 
                          [--timeout TIMEOUT] [--output OUTPUT] [--create-sample]

options:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Path to JSON configuration file with test cases
  --service-url SERVICE_URL, -u SERVICE_URL
                        URL of the MCP tool enumeration service 
                        (default: http://localhost:8503)
  --timeout TIMEOUT, -t TIMEOUT
                        Timeout in seconds for each enumeration request 
                        (default: 15)
  --output OUTPUT, -o OUTPUT
                        Save detailed results to JSON file
  --create-sample       Create a sample configuration file and exit
```

## Sample Output

### Console Output
```
🚀 Starting enumeration tests for 6 configurations...
📍 Service URL: http://localhost:8503
⏱️ Timeout: 8 seconds
------------------------------------------------------------
✅ Service health check passed
------------------------------------------------------------
🧪 Testing configuration 1/6: PayPal Sandbox
   ✅ Success: 1/1 servers connected, 31 tools discovered
   ⏱️ Response time: 5.96s

============================================================
📊 ENUMERATION TEST SUMMARY REPORT
============================================================
🕐 Timestamp: 2025-09-25T15:29:28.360834
🌐 Service URL: http://localhost:8503
⏱️ Timeout: 8 seconds

📈 RESULTS OVERVIEW:
   • Total Configurations Tested: 6
   • Total Servers Tested: 8
   • Successful Connections: 2
   • Failed Connections: 6
   • Success Rate: 25.0%
   • Total Tools Discovered: 62
```

### JSON Output Structure
```json
{
  "timestamp": "2025-09-25T15:29:28.360834",
  "service_url": "http://localhost:8503",
  "timeout_seconds": 8,
  "summary": {
    "total_configurations": 6,
    "total_servers_tested": 8,
    "successful_servers": 2,
    "failed_servers": 6,
    "success_rate": 25.0,
    "total_tools_discovered": 62
  },
  "detailed_results": [
    {
      "config_name": "PayPal Sandbox",
      "status": "success",
      "response_time": 5.96,
      "servers": [...],
      "total_tools": 31,
      "error": null
    }
  ]
}
```

## Prerequisites

1. **MCP Tool Enumeration Service**: The service must be running on the specified URL
2. **Python Dependencies**: `requests` library is required
3. **Network Access**: Ability to reach the MCP servers being tested

## Error Handling

The script handles various error scenarios:

- **Service Unavailable**: Checks service health before testing
- **Network Timeouts**: Configurable timeout handling
- **Invalid Configurations**: Validates JSON structure
- **Connection Failures**: Detailed error reporting for each server

## Tips

1. **API Keys**: Replace placeholder API keys with actual values for successful testing
2. **Timeouts**: Adjust timeout values based on expected server response times
3. **Batch Testing**: Use multiple configurations to test different scenarios
4. **Results Analysis**: Use JSON output for automated analysis and reporting

## Example Workflow

1. Create your configuration file:
   ```bash
   python scripts/test_enumeration.py --create-sample
   # Edit the generated sample_test_configs.json with your actual configurations
   ```

2. Start the MCP Tool Enumeration Service:
   ```bash
   uv run python -m src.app.protocols.http.main
   ```

3. Run the tests:
   ```bash
   python scripts/test_enumeration.py --config your_configs.json --output results.json
   ```

4. Analyze the results in the console output or the generated JSON file.
