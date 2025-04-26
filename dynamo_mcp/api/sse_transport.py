"""
SSE Transport for the dynamo-mcp system.

This module provides an SSE transport for the MCP server.
"""
import json
import asyncio
import logging
from typing import Dict, Any, Optional, Callable, Awaitable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

# Set up logging
logger = logging.getLogger(__name__)


class SSETransport:
    """SSE transport for the MCP server."""
    
    def __init__(self, app: FastAPI):
        """Initialize the SSE transport.
        
        Args:
            app: The FastAPI application to use
        """
        self.app = app
        self.clients = {}
        self.client_id = 0
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add routes
        self.app.post("/mcp/request")(self.handle_request)
        self.app.get("/mcp/events")(self.handle_events)
    
    async def handle_request(self, request: Request) -> Response:
        """Handle an MCP request.
        
        Args:
            request: The HTTP request
        
        Returns:
            The HTTP response
        """
        # Parse request
        data = await request.json()
        
        # Get client ID
        client_id = data.get("client_id")
        if not client_id:
            return Response(
                content=json.dumps({"error": "Missing client_id"}),
                media_type="application/json",
                status_code=400
            )
        
        # Get client
        client = self.clients.get(client_id)
        if not client:
            return Response(
                content=json.dumps({"error": "Client not found"}),
                media_type="application/json",
                status_code=404
            )
        
        # Send request to client
        client["queue"].put_nowait(data)
        
        # Wait for response
        try:
            response = await asyncio.wait_for(client["response"].get(), timeout=60)
            return Response(
                content=json.dumps(response),
                media_type="application/json"
            )
        except asyncio.TimeoutError:
            return Response(
                content=json.dumps({"error": "Request timed out"}),
                media_type="application/json",
                status_code=408
            )
    
    async def handle_events(self, request: Request) -> StreamingResponse:
        """Handle SSE events.
        
        Args:
            request: The HTTP request
        
        Returns:
            The SSE response
        """
        # Create client
        client_id = str(self.client_id)
        self.client_id += 1
        
        # Create queues
        queue = asyncio.Queue()
        response_queue = asyncio.Queue()
        
        # Store client
        self.clients[client_id] = {
            "queue": queue,
            "response": response_queue
        }
        
        # Send client ID
        await queue.put({"type": "connection", "client_id": client_id})
        
        # Create event stream
        async def event_stream():
            try:
                while True:
                    # Get next event
                    event = await queue.get()
                    
                    # Send event
                    yield {
                        "event": event.get("type", "message"),
                        "data": json.dumps(event)
                    }
            except asyncio.CancelledError:
                # Remove client
                self.clients.pop(client_id, None)
                logger.info(f"Client {client_id} disconnected")
        
        # Return event stream
        return EventSourceResponse(event_stream())
    
    def send_response(self, client_id: str, response: Dict[str, Any]):
        """Send a response to a client.
        
        Args:
            client_id: The client ID
            response: The response to send
        """
        # Get client
        client = self.clients.get(client_id)
        if not client:
            logger.warning(f"Client {client_id} not found")
            return
        
        # Send response
        client["response"].put_nowait(response)