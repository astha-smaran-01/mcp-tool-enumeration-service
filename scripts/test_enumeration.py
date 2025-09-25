#!/usr/bin/env python3
"""
MCP Tool Enumeration Testing Script

This script tests multiple MCP server configurations against the tool enumeration API
and generates a comprehensive report of the results.

Usage:
    python scripts/test_enumeration.py [--config CONFIG_FILE] [--service-url URL] [--timeout SECONDS]

Example:
    python scripts/test_enumeration.py --config test_configs.json --timeout 15
"""

import argparse
import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import requests
import sys
from datetime import datetime


class EnumerationTester:
    """Test MCP tool enumeration API with multiple server configurations."""
    
    def __init__(self, service_url: str = "http://localhost:8503", timeout: int = 15):
        self.service_url = service_url.rstrip('/')
        self.api_endpoint = f"{self.service_url}/api/v1/tools/enumerate"
        self.health_endpoint = f"{self.service_url}/health"
        self.timeout = timeout
        
    def check_service_health(self) -> bool:
        """Check if the enumeration service is running and healthy."""
        try:
            response = requests.get(self.health_endpoint, timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                return health_data.get("success", False)
            return False
        except requests.exceptions.RequestException:
            return False
    
    def test_single_configuration(self, config: Dict[str, Any], config_name: str = "") -> Dict[str, Any]:
        """Test a single MCP configuration and return results."""
        request_body = {
            "mcp_json": config,
            "timeout_seconds": self.timeout
        }
        
        start_time = time.time()
        try:
            response = requests.post(
                self.api_endpoint,
                json=request_body,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout + 10  # Add buffer to request timeout
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result_data = response.json()
                return {
                    "config_name": config_name,
                    "status": "success",
                    "response_time": round(end_time - start_time, 2),
                    "data": result_data.get("data", {}),
                    "servers": result_data.get("data", {}).get("servers", []),
                    "total_tools": len(result_data.get("data", {}).get("tools", [])),
                    "error": None
                }
            else:
                return {
                    "config_name": config_name,
                    "status": "error",
                    "response_time": round(end_time - start_time, 2),
                    "data": {},
                    "servers": [],
                    "total_tools": 0,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "config_name": config_name,
                "status": "timeout",
                "response_time": self.timeout + 10,
                "data": {},
                "servers": [],
                "total_tools": 0,
                "error": f"Request timeout after {self.timeout + 10} seconds"
            }
        except requests.exceptions.RequestException as e:
            return {
                "config_name": config_name,
                "status": "error",
                "response_time": round(time.time() - start_time, 2),
                "data": {},
                "servers": [],
                "total_tools": 0,
                "error": f"Request error: {str(e)}"
            }
    
    def test_multiple_configurations(self, configurations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test multiple configurations and generate a comprehensive report."""
        print(f"🚀 Starting enumeration tests for {len(configurations)} configurations...")
        print(f"📍 Service URL: {self.service_url}")
        print(f"⏱️ Timeout: {self.timeout} seconds")
        print("-" * 60)
        
        # Check service health first
        if not self.check_service_health():
            print("❌ Service health check failed. Is the MCP tool enumeration service running?")
            return {"error": "Service not available"}
        
        print("✅ Service health check passed")
        print("-" * 60)
        
        results = []
        total_servers_tested = 0
        successful_servers = 0
        failed_servers = 0
        total_tools_discovered = 0
        
        for i, config in enumerate(configurations, 1):
            mcp_json = config.get("mcp_json", config)
            config_name = list(mcp_json.get('mcpServers', {f"config_{i}": {}}).keys())[0]
            
            print(f"🧪 Testing configuration {i}/{len(configurations)}: {config_name}")
            
            # Count servers in this configuration
            servers_in_config = len(mcp_json.get("mcpServers", {}))
            total_servers_tested += servers_in_config
            
            result = self.test_single_configuration(mcp_json, config_name)
            results.append(result)
            
            # Update counters
            if result["status"] == "success":
                for server in result["servers"]:
                    if server.get("status") == "connected":
                        successful_servers += 1
                    else:
                        failed_servers += 1
                total_tools_discovered += result["total_tools"]
            else:
                failed_servers += servers_in_config
            
            # Print immediate result
            if result["status"] == "success":
                success_count = len([s for s in result["servers"] if s.get("status") == "connected"])
                print(f"   ✅ Success: {success_count}/{servers_in_config} servers connected, {result['total_tools']} tools discovered")
            else:
                print(f"   ❌ Failed: {result['error']}")
            
            print(f"   ⏱️ Response time: {result['response_time']}s")
            print()
        
        # Generate summary report
        report = {
            "timestamp": datetime.now().isoformat(),
            "service_url": self.service_url,
            "timeout_seconds": self.timeout,
            "summary": {
                "total_configurations": len(configurations),
                "total_servers_tested": total_servers_tested,
                "successful_servers": successful_servers,
                "failed_servers": failed_servers,
                "success_rate": round((successful_servers / total_servers_tested * 100), 2) if total_servers_tested > 0 else 0,
                "total_tools_discovered": total_tools_discovered
            },
            "detailed_results": results
        }
        
        return report
    
    def print_summary_report(self, report: Dict[str, Any]):
        """Print a formatted summary report."""
        if "error" in report:
            print(f"❌ Test failed: {report['error']}")
            return
            
        summary = report["summary"]
        
        print("=" * 60)
        print("📊 ENUMERATION TEST SUMMARY REPORT")
        print("=" * 60)
        print(f"🕐 Timestamp: {report['timestamp']}")
        print(f"🌐 Service URL: {report['service_url']}")
        print(f"⏱️ Timeout: {report['timeout_seconds']} seconds")
        print()
        print(f"📈 RESULTS OVERVIEW:")
        print(f"   • Total Configurations Tested: {summary['total_configurations']}")
        print(f"   • Total Servers Tested: {summary['total_servers_tested']}")
        print(f"   • Successful Connections: {summary['successful_servers']}")
        print(f"   • Failed Connections: {summary['failed_servers']}")
        print(f"   • Success Rate: {summary['success_rate']}%")
        print(f"   • Total Tools Discovered: {summary['total_tools_discovered']}")
        print()
        
        print("🔍 DETAILED RESULTS:")
        for result in report["detailed_results"]:
            status_icon = "✅" if result["status"] == "success" else "❌"
            print(f"   {status_icon} {result['config_name']}")
            
            if result["status"] == "success":
                connected_servers = [s for s in result["servers"] if s.get("status") == "connected"]
                failed_servers = [s for s in result["servers"] if s.get("status") != "connected"]
                
                print(f"      • Connected: {len(connected_servers)} servers")
                if connected_servers:
                    for server in connected_servers:
                        print(f"        - {server.get('name', 'Unknown')}: {server.get('tool_count', 0)} tools")
                
                if failed_servers:
                    print(f"      • Failed: {len(failed_servers)} servers")
                    for server in failed_servers:
                        error_msg = server.get('error', 'Unknown error')[:50]
                        print(f"        - {server.get('name', 'Unknown')}: {error_msg}")
            else:
                print(f"      • Error: {result['error']}")
            
            print(f"      • Response time: {result['response_time']}s")
            print()
        
        print("=" * 60)


def load_configurations_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Load test configurations from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        # Handle different file formats
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            if "configurations" in data:
                return data["configurations"]
            else:
                return [data]
        else:
            raise ValueError("Invalid configuration file format")
            
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading configuration file: {e}")
        sys.exit(1)


def create_sample_config():
    """Create a sample configuration file for reference."""
    sample_config = {
        "configurations": [
            {
                "name": "PayPal Sandbox",
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
                                "PAYPAL_API_KEY": "<Your PayPal API Key here>"
                            }
                        }
                    }
                }
            },
            {
                "name": "Multiple Services",
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
                                "PAYPAL_API_KEY": "<Your PayPal API Key here>"
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
                                "LINEAR_API_KEY": "<Your Linear API Key here>"
                            }
                        }
                    }
                }
            }
        ]
    }
    
    with open("sample_test_configs.json", "w") as f:
        json.dump(sample_config, f, indent=2)
    
    print("📝 Sample configuration created: sample_test_configs.json")


def main():
    parser = argparse.ArgumentParser(
        description="Test MCP tool enumeration API with multiple configurations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Test with configuration file
    python scripts/test_enumeration.py --config test_configs.json
    
    # Test with custom service URL and timeout
    python scripts/test_enumeration.py --config test_configs.json --service-url http://localhost:8080 --timeout 20
    
    # Create sample configuration file
    python scripts/test_enumeration.py --create-sample
    
    # Save results to file
    python scripts/test_enumeration.py --config test_configs.json --output results.json
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to JSON configuration file with test cases"
    )
    
    parser.add_argument(
        "--service-url", "-u",
        type=str,
        default="http://localhost:8503",
        help="URL of the MCP tool enumeration service (default: http://localhost:8503)"
    )
    
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=15,
        help="Timeout in seconds for each enumeration request (default: 15)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Save detailed results to JSON file"
    )
    
    parser.add_argument(
        "--create-sample",
        action="store_true",
        help="Create a sample configuration file and exit"
    )
    
    args = parser.parse_args()
    
    if args.create_sample:
        create_sample_config()
        return
    
    if not args.config:
        print("❌ Configuration file is required. Use --config to specify the file.")
        print("💡 Use --create-sample to generate a sample configuration file.")
        sys.exit(1)
    
    # Load configurations
    configurations = load_configurations_from_file(args.config)
    
    if not configurations:
        print("❌ No configurations found in the file.")
        sys.exit(1)
    
    # Run tests
    tester = EnumerationTester(service_url=args.service_url, timeout=args.timeout)
    report = tester.test_multiple_configurations(configurations)
    
    # Print summary
    tester.print_summary_report(report)
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"💾 Detailed results saved to: {args.output}")


if __name__ == "__main__":
    main()
