#!/usr/bin/env python3
"""
Test script for PayPal MCP server debugging.

This script helps debug issues with PayPal MCP server execution in Docker.
"""

import asyncio
import subprocess
import json
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_paypal_mcp():
    """Test PayPal MCP server execution."""
    
    # Test 1: Check if npx is available
    logger.info("=== Test 1: Checking npx availability ===")
    try:
        result = subprocess.run(["which", "npx"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ npx found at: {result.stdout.strip()}")
        else:
            logger.error("❌ npx not found")
            return
    except Exception as e:
        logger.error(f"❌ Error checking npx: {e}")
        return
    
    # Test 2: Check npx version
    logger.info("=== Test 2: Checking npx version ===")
    try:
        result = subprocess.run(["npx", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ npx version: {result.stdout.strip()}")
        else:
            logger.error(f"❌ npx version check failed: {result.stderr}")
    except Exception as e:
        logger.error(f"❌ Error checking npx version: {e}")
    
    # Test 3: Try to run PayPal MCP with proper arguments
    logger.info("=== Test 3: Testing PayPal MCP with proper arguments ===")
    
    # Set up environment
    env = os.environ.copy()
    env.update({
        "PAYPAL_ACCESS_TOKEN": "YOUR_PAYPAL_ACCESS_TOKEN",
        "PAYPAL_ENVIRONMENT": "SANDBOX"
    })
    
    # Try different argument combinations
    test_configs = [
        {
            "name": "Basic npx with access-token",
            "args": ["npx", "-y", "@paypal/mcp", "--access-token", "test_token"]
        },
        {
            "name": "npx with tools=all",
            "args": ["npx", "-y", "@paypal/mcp", "--tools=all"]
        },
        {
            "name": "npx with environment",
            "args": ["npx", "-y", "@paypal/mcp", "--paypal-environment", "SANDBOX"]
        }
    ]
    
    for config in test_configs:
        logger.info(f"Testing: {config['name']}")
        try:
            # Start process
            process = subprocess.Popen(
                config["args"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True
            )
            
            # Give it a moment to start
            await asyncio.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                logger.info(f"✅ Process is running for {config['name']}")
                
                # Try to send MCP initialization
                mcp_init = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-06-18",
                        "capabilities": {"tools": {}},
                        "clientInfo": {"name": "test-client", "version": "1.0.0"}
                    }
                }
                
                try:
                    process.stdin.write(json.dumps(mcp_init) + "\n")
                    process.stdin.flush()
                    logger.info("✅ Sent MCP initialization")
                    
                    # Try to read response
                    try:
                        response = await asyncio.wait_for(
                            asyncio.to_thread(process.stdout.readline),
                            timeout=5
                        )
                        if response:
                            logger.info(f"✅ Received response: {response.strip()}")
                        else:
                            logger.warning("⚠️ No response received")
                    except asyncio.TimeoutError:
                        logger.warning("⚠️ Timeout waiting for response")
                        
                except Exception as e:
                    logger.error(f"❌ Error sending MCP init: {e}")
                
                # Clean up
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    
            else:
                logger.error(f"❌ Process terminated early for {config['name']}")
                stdout, stderr = process.communicate()
                if stderr:
                    logger.error(f"stderr: {stderr}")
                if stdout:
                    logger.info(f"stdout: {stdout}")
                    
        except Exception as e:
            logger.error(f"❌ Error testing {config['name']}: {e}")
    
    # Test 4: Check if package exists
    logger.info("=== Test 4: Checking if @paypal/mcp package exists ===")
    try:
        result = subprocess.run(
            ["npm", "view", "@paypal/mcp", "version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            logger.info(f"✅ @paypal/mcp package exists, version: {result.stdout.strip()}")
        else:
            logger.error(f"❌ @paypal/mcp package not found: {result.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("❌ Timeout checking package")
    except Exception as e:
        logger.error(f"❌ Error checking package: {e}")

if __name__ == "__main__":
    asyncio.run(test_paypal_mcp())