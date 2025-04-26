#!/bin/bash
# Run the database tests

# Set the testing environment variable
export DYNAMO_MCP_TESTING=true

# Run the tests
python -m unittest tests/test_database.py