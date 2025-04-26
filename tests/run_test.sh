#!/bin/bash

# Kill any existing MCP processes
pkill -f "python -m dynamo_mcp.main" || true

# Run the test with a timeout
timeout 10s python tests/run_single_test.py

# Get the exit code
EXIT_CODE=$?

# Check if the test timed out
if [ $EXIT_CODE -eq 124 ]; then
    echo "Test timed out after 10 seconds"
    # Kill any remaining MCP processes
    pkill -f "python -m dynamo_mcp.main" || true
    exit 1
fi

# Exit with the test's exit code
exit $EXIT_CODE