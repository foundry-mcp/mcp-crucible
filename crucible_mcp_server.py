#!/usr/bin/env python3
"""
Crucible MCP Server

An MCP (Model Context Protocol) server that exposes the Crucible API functionality
as tools that can be used by AI assistants and other MCP clients.

This server wraps the pycrucible.CrucibleClient and exposes its key methods
as MCP tools for managing datasets, projects, users, instruments, and samples.
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional

# Add the pycrucible package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pycrucible'))

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types
from mcp.server.stdio import stdio_server

from pycrucible import CrucibleClient


# Global client instance
client: Optional[CrucibleClient] = None

server = Server("crucible-api")


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available Crucible API tools."""
    return [
        Tool(
            name="list_projects",
            description="List all accessible projects in Crucible. This function first checks if the API key is associated with a user or admin account. Then uses that information to either list all projects (admin) or all projects associated with the current user's ORCID",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="get_project",
            description="Get details of a specific project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "The project ID to retrieve"
                    }
                },
                "required": ["project_id"]
            },
        ),
        Tool(
            name="list_datasets",
            description="List datasets with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "sample_id": {
                        "type": "string",
                        "description": "If provided, returns datasets associated with this sample ID"
                    },
                    "public": {
                        "type": "boolean",
                        "description": "If provided, filters datasets by public visibility"
                    },
                    "instrument_id": {
                        "type": "integer",
                        "description": "If provided, returns only datasets associated with this instrument ID"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "If provided, returns only datasets associated with this project ID"
                    },
                    "owner_orcid": {
                        "type": "string",
                        "description": "If provided, returns only datasets owned by this ORCID"
                    },
                    "dataset_name": {
                        "type": "string",
                        "description": "If provided, filters datasets by name"
                    },
                    "source_folder": {
                        "type": "string",
                        "description": "If provided, filters datasets by source folder"
                    },
                    "data_format": {
                        "type": "string",
                        "description": "If provided, filters datasets by data format"
                    },
                    "measurement": {
                        "type": "string",
                        "description": "If provided, filters datasets by measurement type"
                    },
                    "session_name": {
                        "type": "string",
                        "description": "If provided, filters datasets by session name"
                    },
                    "keyword": {
                        "type": "string",
                        "description": "If provided, filters datasets by keyword"
                    }
                },
                "required": [],
                "additionalProperties": True
            },
        ),
        Tool(
            name="get_dataset",
            description="Get dataset details, optionally including scientific metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "dsid": {
                        "type": "string",
                        "description": "Dataset ID"
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "description": "Whether to include scientific metadata",
                        "default": False
                    }
                },
                "required": ["dsid"]
            },
        ),
        Tool(
            name="download_dataset",
            description="Download a dataset file",
            inputSchema={
                "type": "object",
                "properties": {
                    "dsid": {
                        "type": "string",
                        "description": "Dataset ID"
                    },
                    "file_name": {
                        "type": "string",
                        "description": "Name of file to download (optional - uses dataset's file_to_upload field if not provided)"
                    },
                    "output_path": {
                        "type": "string", 
                        "description": "Local path to save file (optional - uses crucible-downloads/<filename> if not provided)"
                    }
                },
                "required": ["dsid"]
            },
        ),
        Tool(
            name="upload_dataset",
            description="Upload a file to a dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "dsid": {
                        "type": "string",
                        "description": "Dataset ID"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to upload"
                    }
                },
                "required": ["dsid", "file_path"]
            },
        ),
        Tool(
            name="create_dataset",
            description="Create a new dataset with metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_name": {
                        "type": "string",
                        "description": "Name of the dataset"
                    },
                    "unique_id": {
                        "type": "string",
                        "description": "Unique identifier for the dataset"
                    },
                    "public": {
                        "type": "boolean",
                        "description": "Whether the dataset is public",
                        "default": False
                    },
                    "owner_orcid": {
                        "type": "string",
                        "description": "ORCID of the dataset owner"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project this dataset belongs to"
                    },
                    "instrument_name": {
                        "type": "string",
                        "description": "Name of the instrument used"
                    },
                    "measurement": {
                        "type": "string",
                        "description": "Type of measurement"
                    },
                    "session_name": {
                        "type": "string",
                        "description": "Name of the measurement session"
                    },
                    "data_format": {
                        "type": "string",
                        "description": "Format of the dataset"
                    },
                    "scientific_metadata": {
                        "type": "object",
                        "description": "Additional scientific metadata"
                    },
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of keywords to associate with the dataset"
                    }
                },
                "required": []
            },
        ),
        Tool(
            name="request_ingestion",
            description="Request dataset ingestion",
            inputSchema={
                "type": "object",
                "properties": {
                    "dsid": {
                        "type": "string",
                        "description": "Dataset ID"
                    },
                    "file_to_upload": {
                        "type": "string",
                        "description": "Path to the file to ingest"
                    },
                    "ingestor": {
                        "type": "string",
                        "description": "Ingestion class to use"
                    }
                },
                "required": ["dsid"]
            },
        ),
        Tool(
            name="get_request_status",
            description="Get the status of a request (ingestion, scicat, etc)",
            inputSchema={
                "type": "object",
                "properties": {
                    "dsid": {
                        "type": "string",
                        "description": "Dataset ID"
                    },
                    "reqid": {
                        "type": "string",
                        "description": "Request ID"
                    },
                    "request_type": {
                        "type": "string",
                        "description": "Type of request",
                        "enum": ["ingest", "scicat_update"]
                    }
                },
                "required": ["dsid", "reqid", "request_type"]
            },
        ),
        Tool(
            name="get_scientific_metadata",
            description="Get scientific metadata for a dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "dsid": {
                        "type": "string",
                        "description": "Dataset ID"
                    }
                },
                "required": ["dsid"]
            },
        ),
        Tool(
            name="update_scientific_metadata",
            description="Update scientific metadata for a dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "dsid": {
                        "type": "string",
                        "description": "Dataset ID"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Scientific metadata to update"
                    }
                },
                "required": ["dsid", "metadata"]
            },
        ),
        Tool(
            name="add_dataset_keyword",
            description="Add a keyword to a dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "dsid": {
                        "type": "string",
                        "description": "Dataset ID"
                    },
                    "keyword": {
                        "type": "string",
                        "description": "Keyword to add"
                    }
                },
                "required": ["dsid", "keyword"]
            },
        ),
        Tool(
            name="get_dataset_keywords",
            description="Get keywords associated with a dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "dsid": {
                        "type": "string",
                        "description": "Dataset ID"
                    }
                },
                "required": ["dsid"]
            },
        ),
        Tool(
            name="send_to_scicat",
            description="Request SciCat update for a dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "dsid": {
                        "type": "string",
                        "description": "Dataset ID"
                    },
                    "wait_for_response": {
                        "type": "boolean",
                        "description": "Whether to wait for the SciCat response",
                        "default": False
                    }
                },
                "required": ["dsid"]
            },
        ),
        Tool(
            name="list_instruments",
            description="List all available instruments",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="get_instrument",
            description="Get instrument information by name or ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "instrument_name": {
                        "type": "string",
                        "description": "Name of the instrument"
                    },
                    "instrument_id": {
                        "type": "integer",
                        "description": "ID of the instrument"
                    }
                },
                "required": []
            },
        ),
        Tool(
            name="get_or_add_instrument",
            description="Get an existing instrument or create a new one if it doesn't exist",
            inputSchema={
                "type": "object",
                "properties": {
                    "instrument_name": {
                        "type": "string",
                        "description": "Name of the instrument"
                    },
                    "creation_location": {
                        "type": "string",
                        "description": "Location where instrument was created"
                    },
                    "instrument_owner": {
                        "type": "string",
                        "description": "Owner of the instrument"
                    }
                },
                "required": ["instrument_name"]
            },
        ),
        Tool(
            name="list_samples",
            description="List samples with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "Dataset ID to get samples from"
                    },
                    "parent_id": {
                        "type": "string",
                        "description": "Parent sample ID to get children from"
                    },
                    "unique_id": {
                        "type": "string",
                        "description": "If provided, filters samples by unique ID"
                    },
                    "sample_name": {
                        "type": "string",
                        "description": "If provided, filters samples by name"
                    },
                    "owner_orcid": {
                        "type": "string",
                        "description": "If provided, filters samples by owner ORCID"
                    },
                    "date_created": {
                        "type": "string",
                        "description": "If provided, filters samples by creation date"
                    },
                    "description": {
                        "type": "string",
                        "description": "If provided, filters samples by description"
                    }
                },
                "required": []
            },
        ),
        Tool(
            name="get_sample",
            description="Get sample information by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "sample_id": {
                        "type": "string",
                        "description": "Sample ID"
                    }
                },
                "required": ["sample_id"]
            },
        ),
        Tool(
            name="add_sample",
            description="Add a new sample to the system",
            inputSchema={
                "type": "object",
                "properties": {
                    "unique_id": {
                        "type": "string",
                        "description": "Unique ID for the sample"
                    },
                    "sample_name": {
                        "type": "string",
                        "description": "Name of the sample"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the sample"
                    },
                    "creation_date": {
                        "type": "string",
                        "description": "Creation date in ISO format"
                    },
                    "owner_orcid": {
                        "type": "string",
                        "description": "ORCID of the sample owner"
                    }
                },
                "required": []
            },
        ),
        Tool(
            name="add_sample_to_dataset",
            description="Link a sample to a dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "Dataset ID"
                    },
                    "sample_id": {
                        "type": "string",
                        "description": "Sample ID"
                    }
                },
                "required": ["dataset_id", "sample_id"]
            },
        ),
        Tool(
            name="get_user_by_email",
            description="Get user details by email",
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "Email address of the user"
                    }
                },
                "required": ["email"]
            },
        ),
        Tool(
            name="get_project_users",
            description="Get users associated with a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    }
                },
                "required": ["project_id"]
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls to the Crucible API."""
    if client is None:
        return [types.TextContent(
            type="text",
            text="Error: Crucible client not initialized. Please set CRUCIBLE_API_URL and CRUCIBLE_API_KEY environment variables."
        )]

    try:
        result = None
        
        if name == "list_projects":
            result = client.list_projects()
        
        elif name == "get_account":
            result = client.get_user_account_info()

        elif name == "get_project":
            result = client._get_project(arguments["project_id"])
        
        # get_user
        # get_user_by_email
        # get_project_users

        elif name == "list_datasets":
            #sample_id = arguments.get("sample_id")
            result = client.list_datasets(**arguments)
            
        elif name == "get_dataset":
            dsid = arguments["dsid"]
            include_metadata = arguments.get("include_metadata", False)
            result = client._get_dataset(dsid, include_metadata=include_metadata)
            
        elif name == "download_dataset":
            dsid = arguments["dsid"]
            file_name = arguments.get("file_name")
            output_path = arguments.get("output_path")
            result = client.download_dataset(dsid, file_name=file_name, output_path=output_path)
        
        elif name == "upload_dataset":
            dsid = arguments["dsid"]
            file_path = arguments["file_path"]
            result = client.upload_dataset(dsid, file_path)
            
        elif name == "create_dataset":
            result = client.create_dataset(**arguments)
            
        elif name == "request_ingestion":
            dsid = arguments["dsid"]
            file_to_upload = arguments.get("file_to_upload")
            ingestor = arguments.get("ingestor")
            result = client.request_ingestion(dsid, file_to_upload=file_to_upload, ingestor=ingestor)
            
        elif name == "get_request_status":
            dsid = arguments["dsid"]
            reqid = arguments["reqid"]
            request_type = arguments["request_type"]
            result = client.get_request_status(dsid, reqid, request_type)
            
        elif name == "get_scientific_metadata":
            dsid = arguments["dsid"]
            result = client.get_scientific_metadata(dsid)
            
        elif name == "update_scientific_metadata":
            dsid = arguments["dsid"]
            metadata = arguments["metadata"]
            result = client.update_scientific_metadata(dsid, metadata)
            
        elif name == "add_dataset_keyword":
            dsid = arguments["dsid"]
            keyword = arguments["keyword"]
            result = client.add_dataset_keyword(dsid, keyword)
            
        elif name == "get_dataset_keywords":
            dsid = arguments["dsid"]
            result = client.get_dataset_keywords(dsid)
            
        elif name == "send_to_scicat":
            dsid = arguments["dsid"]
            wait_for_response = arguments.get("wait_for_response", False)
            result = client.send_to_scicat(dsid, wait_for_scicat_response=wait_for_response)
            
        elif name == "list_instruments":
            result = client.list_instruments()
            
        elif name == "get_instrument":
            instrument_name = arguments.get("instrument_name")
            instrument_id = arguments.get("instrument_id")
            result = client._get_instrument(instrument_name=instrument_name, instrument_id=instrument_id)
            
        elif name == "get_or_add_instrument":
            instrument_name = arguments["instrument_name"]
            creation_location = arguments.get("creation_location")
            instrument_owner = arguments.get("instrument_owner")
            result = client.get_or_add_instrument(instrument_name, creation_location=creation_location, instrument_owner=instrument_owner)
            
        elif name == "list_samples":
            #dataset_id = arguments.get("dataset_id")
            #parent_id = arguments.get("parent_id")
            result = client.list_samples(**arguments)
            
        elif name == "get_sample":
            sample_id = arguments["sample_id"]
            result = client.get_sample(sample_id)
            
        elif name == "add_sample":
            result = client.add_sample(**arguments)
            
        elif name == "add_sample_to_dataset":
            dataset_id = arguments["dataset_id"]
            sample_id = arguments["sample_id"]
            result = client.add_sample_to_dataset(dataset_id, sample_id)
            
        elif name == "get_user_by_email":
            email = arguments["email"]
            result = client.get_user_by_email(email)
            
        elif name == "get_project_users":
            project_id = arguments["project_id"]
            result = client.get_project_users(project_id)
            
        else:
            return [types.TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]

        # Format the result as JSON
        if result is None:
            result_text = "Operation completed successfully (no return value)"
        else:
            result_text = json.dumps(result, indent=2, default=str)

        return [types.TextContent(
            type="text",
            text=result_text
        )]

        # TODO: Can return images as image content

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def main():
    """Main function to run the MCP server."""
    global client
    
    # TODO: this should happen on mcp client side
    # Initialize the Crucible client
    api_url = os.getenv("CRUCIBLE_API_URL")
    api_key = os.getenv("CRUCIBLE_API_KEY")
    
    if not api_url or not api_key:
        print("Error: CRUCIBLE_API_URL and CRUCIBLE_API_KEY environment variables must be set", file=sys.stderr)
        sys.exit(1)
    
    client = CrucibleClient(api_url, api_key)
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
           await server.run(read_stream,
                            write_stream,
                            InitializationOptions(
                                server_name="crucible_mcp_server",
                                server_version="0.0.1",
                                capabilities=server.get_capabilities(
                                    notification_options=NotificationOptions(),
                                    experimental_capabilities={},
                                )))

if __name__ == "__main__":
   asyncio.run(main())
