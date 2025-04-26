"""
Main entry point for the dynamo-mcp system.

This module provides the main entry point for the dynamo-mcp system.
"""
import os
import sys
import signal
import argparse
import logging
from typing import Optional

from dynamo_mcp.api.mcp_server import MCPServer
from dynamo_mcp.utils.config import HOST, PORT, TRANSPORT
from dynamo_mcp.utils.database import ensure_db_exists
from dynamo_mcp.utils.init_template_db import initialize_database

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments.
    
    Returns:
        The parsed arguments
    """
    parser = argparse.ArgumentParser(description="Dynamo MCP Server")
    
    # Transport
    parser.add_argument(
        "--transport",
        type=str,
        default=TRANSPORT,
        choices=["sse", "stdio"],
        help="Transport type (sse or stdio)"
    )
    
    # Host and port (only used for SSE transport)
    parser.add_argument(
        "--host",
        type=str,
        default=HOST,
        help="Host to bind to (only used for SSE transport)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=PORT,
        help="Port to bind to (only used for SSE transport)"
    )
    
    # Testing mode
    parser.add_argument(
        "--testing",
        action="store_true",
        help="Enable testing mode"
    )
    
    # Verbose mode
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    # Database initialization
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialize the template database with default templates"
    )
    
    parser.add_argument(
        "--reset-db",
        action="store_true",
        help="Reset the template database before initialization"
    )
    
    return parser.parse_args()


def setup_testing_mode():
    """Set up testing mode."""
    os.environ["DYNAMO_MCP_TESTING"] = "true"


def setup_environment():
    """Set up the environment."""
    # Add current directory to path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def initialize_template_database(force_reset: bool = False):
    """Initialize the template database with default templates.
    
    Args:
        force_reset: Whether to force reset the database
    """
    logger.info("Initializing template database...")
    
    # Ensure database exists
    ensure_db_exists()
    
    # Initialize database with default templates if it's empty
    try:
        count, names = initialize_database(reset=force_reset)
        if count > 0:
            logger.info(f"Added {count} templates to the database")
        else:
            logger.info("No new templates added to the database")
    except Exception as e:
        logger.error(f"Error initializing template database: {e}", exc_info=True)


def setup_signal_handlers():
    """Set up signal handlers for graceful shutdown."""
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down...")
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Run the MCP server."""
    try:
        # Parse arguments
        args = parse_args()
        
        # Set up logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Set up environment
        setup_environment()
        
        # Set up signal handlers
        setup_signal_handlers()
        
        # Set up testing mode if enabled
        if args.testing:
            setup_testing_mode()
            logger.info("Running in testing mode")
        
        # Initialize database if requested
        if args.init_db or args.reset_db:
            initialize_template_database(force_reset=args.reset_db)
        
        # Log startup information
        logger.info(f"Starting Dynamo MCP Server with {args.transport} transport")
        if args.transport == "sse":
            logger.info(f"Binding to {args.host}:{args.port}")
        
        # Create and run server
        server = MCPServer()
        server.run(transport=args.transport, host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()