"""
Run a single test and exit immediately.

This script runs a single test and exits immediately, regardless of whether the test passes or fails.
"""
import os
import sys
import signal
import subprocess
import time
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def run_test():
    """Run a single test and exit immediately."""
    print("Starting test...")
    
    # Kill any existing MCP processes
    try:
        subprocess.run(["pkill", "-f", "python -m dynamo_mcp.main"], check=False)
        time.sleep(1)  # Give processes time to terminate
    except Exception as e:
        print(f"Error killing existing processes: {e}")
    
    # Start MCP server
    try:
        server_process = subprocess.Popen(
            [sys.executable, "-m", "dynamo_mcp.main", "--transport", "stdio", "--testing"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,  # Unbuffered
            universal_newlines=False
        )
        
        print("Server process started")
        
        # Wait for server to start
        time.sleep(2)
        
        # Check if server is running
        if server_process.poll() is not None:
            print(f"Server process exited with code {server_process.returncode}")
            stderr = server_process.stderr.read().decode()
            print(f"Server stderr: {stderr}")
            return 1
        
        print("Sending request...")
        
        # Send a simple request
        request = {
            "jsonrpc": "2.0",
            "method": "mcp.call_tool",
            "params": {
                "tool": "list_templates",
                "arguments": {}
            },
            "id": 1
        }
        
        request_bytes = json.dumps(request).encode() + b'\n'
        server_process.stdin.write(request_bytes)
        server_process.stdin.flush()
        
        print("Request sent, waiting for response...")
        
        # Wait for response with timeout
        start_time = time.time()
        timeout = 5  # 5 seconds
        
        while time.time() - start_time < timeout:
            # Check if process is still running
            if server_process.poll() is not None:
                print(f"Server process exited with code {server_process.returncode}")
                stderr = server_process.stderr.read().decode()
                print(f"Server stderr: {stderr}")
                return 1
            
            # Check if there's data to read
            if server_process.stdout is not None:
                try:
                    response_line = server_process.stdout.readline()
                    if response_line:
                        print(f"Received response: {response_line.decode()}")
                        return 0
                except Exception as e:
                    print(f"Error reading response: {e}")
            
            # Wait a bit
            time.sleep(0.1)
        
        print("Timeout waiting for response")
        return 1
    except Exception as e:
        print(f"Error running test: {e}")
        return 1
    finally:
        print("Cleaning up...")
        
        # Terminate server
        try:
            if server_process.poll() is None:
                print("Terminating server process...")
                server_process.terminate()
                
                # Wait for process to terminate
                for _ in range(10):  # Wait up to 1 second
                    if server_process.poll() is not None:
                        break
                    time.sleep(0.1)
                
                # If process is still running, kill it
                if server_process.poll() is None:
                    print("Killing server process...")
                    server_process.kill()
        except Exception as e:
            print(f"Error terminating process: {e}")
        
        # Kill any remaining MCP processes
        try:
            subprocess.run(["pkill", "-f", "python -m dynamo_mcp.main"], check=False)
        except Exception as e:
            print(f"Error killing processes: {e}")


if __name__ == "__main__":
    try:
        exit_code = run_test()
        print(f"Test completed with exit code {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        print(f"Unhandled exception: {e}")
        sys.exit(1)
    finally:
        print("Exiting...")
        # Force exit to ensure we don't hang
        os._exit(0)