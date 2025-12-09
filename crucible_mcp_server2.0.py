import os
import sys
from fastmcp import FastMCP
from pycrucible import CrucibleClient
from typing import Optional, List, Dict, Any

mcp = FastMCP("crucible")

'''
This is a set of tools for communicating with the Crucible data management platform
'''

# TODO: 
# - comb through descriptions to make sure they are informative
# - where there are kwargs - define possibilities and use cases
# - where there are limits do they make sense
# - test it out!
# - add some benchmarks to see if this does better than 1.0.0-alpha : )

@mcp.tool()
def get_project(client, project_id: str) -> Dict:
        """Get details of a specific project.

        Args:
            project_id (str): Unique project identifier. 
            Generally this is the same as the name of the project. 
            Case sensitive. 

        Returns:
            Dict: Project information including project_id, description, project_lead_email

        """
        return client.get_project(project_id)

@mcp.tool()
def list_projects(client, orcid: str, limit: int = 100) -> List:
    """List all accessible projects.

    Args:
        orcid (str): Filter projects by those associated with a certain user
        limit (int): Maximum number of results to return (default: 100)

    Returns:
        List[Dict]: List of projects and their associated metadata including project_id, description, project_lead_email
    """
    return client.list_projects(orcid, limit)

@mcp.tool()
def get_user(client, orcid: str = None, email: str = None) -> Dict:
     """Get user details by ORCID or email.

        **Requires admin permissions.**

        Args:
            orcid (str): ORCID identifier (format: 0000-0000-0000-000X)
            email (str): Users email address

            If both orcid and email are provided, only orcid will be used. 

        Returns:
            Dict: User profile with orcid, name, email, timestamps
        """
     return client.get_user(orcid, email)

@mcp.tool()
def get_project_users(client, project_id: str, limit: int = 100) -> List[Dict]:
    """Get users associated with a project.

    **Requires admin permissions.**

    Args:
        project_id (str): Unique project identifier
        limit (int): Maximum number of results to return (default: 100)

    Returns:
        List[Dict]: Project team members (excludes project lead)
    """
    return client.get_project_users(project_id, limit)

@mcp.tool()
def get_dataset(client, dsid: str, include_metadata: bool = False) -> Dict:
    """Get dataset details, optionally including scientific metadata.

    Args:
        dsid (str): Dataset unique identifier
        include_metadata (bool): Whether to include scientific metadata

    Returns:
        Dict: Dataset object with optional metadata
    """
    
    return client.get_dataset(dsid, include_metadata)
    
@mcp.tool()
def list_datasets(client, sample_id: Optional[str] = None, limit: int = 100, **kwargs) -> List[Dict]:
    """List datasets with optional filtering.

    Args:
        sample_id (str, optional): If provided, returns datasets for this sample
        limit (int): Maximum number of results to return (default: 100)
        **kwargs: Query parameters for filtering. Fields that are currently supported to filter on include: 
                    keyword, unique_id, public, dataset_name, file_to_upload, owner_orcid,
                    project_id, instrument_name, source_folder, creation_time,
                    size, data_format, measurement, session_name, and sha256_hash_file_to_upload
            Other kwargs will be ignored during filtering. 

        Note:   Filters are applied such that datasets are filtered on the fields
                corresponding to the provided argument names where their attributes
                are equivalent to the value provided.  Values are case sensitive and
                expect exact matches with the exception of keywords.
                Keywords are case insensitive and will match substrings
                (eg. keyword = 'TEM' will return datasets with any of the following keywords: TEM, tem, Stem, etc)

    Returns:
        List[Dict]: Dataset objects matching filter criteria
    """
    return client.list_datasets(sample_id, limit, **kwargs)

@mcp.tool()
def get_request_status(client, dsid: str, reqid: str, request_type: str) -> Dict:
    """Get the status of any type of request.

    Args:
        dsid (str): Dataset ID
        reqid (str): Request ID
        request_type (str): Type of request ('ingest' or 'scicat_update')

    Returns:
        Dict: Request status information
    """
    return client.get_request_status(dsid, reqid, request_type)

@mcp.tool()
def get_thumbnails(client, dsid: str, limit: int = 100) -> List[Dict]:
    """Get thumbnails for a dataset.
    Args:
        dsid (str): Dataset ID
        limit (int): Maximum number of results to return (default: 100)

    Returns:
        List[Dict]: Thumbnail objects with base64-encoded images
    """
    return client.get_thumbnails(dsid, limit)

@mcp.tool()
def get_associated_files(client, dsid: str, limit: int = 100) -> List[Dict]:
    """Get associated files for a dataset.

    Args:
        dsid (str): Dataset ID
        limit (int): Maximum number of results to return (default: 100)

    Returns:
        List[Dict]: File metadata with names, sizes, and hashes
    """
    return client.get_associated_files(dsid, limit)

@mcp.tool()
def get_keywords(client, dsid: str = None, limit: int = 100) -> List[Dict]:
    """List keywords, option to filter on keywords associated with a given dataset.

    Args:
        limit (int): Maximum number of results to return (default: 100)

    Returns:
        List[Dict]: Keyword objects with keyword text and num_datasets counts
    """
    return client.get_keywords(dsid, limit)

@mcp.tool()
def get_google_drive_location(client, dsid: str) -> List[Dict]:
    """Get current Google Drive location information for a dataset.

    Args:
        dsid (str): Dataset ID

    Returns:
        Dict: Google Drive location information
    """
    return client.get_google_drive_location(dsid)

@mcp.tool()
def list_instruments(client, limit: int = 100) -> List[Dict]:
    """List all available instruments.

    Args:
        limit (int): Maximum number of results to return (default: 100)

    Returns:
        List[Dict]: Instrument objects with specifications and metadata
    """
    return client.list_instruments(limit)

@mcp.tool()
def get_instrument(client, instrument_name: str = None, instrument_id: str = None) -> Dict:
    """Get instrument information by name or ID.

    Args:
        instrument_name (str, optional): Name of the instrument
        instrument_id (str, optional): Unique ID of the instrument

    Returns:
        Dict or None: Instrument information if found, None otherwise

    Raises:
        ValueError: If neither parameter is provided
    """
    return client.get_instrument(instrument_name, instrument_id)

@mcp.tool()
def get_sample(client, sample_id: str) -> Dict:
    """Get sample information by ID.

    Args:
        sample_id (str): Sample unique identifier

    Returns:
        Dict: Sample information with associated datasets
    """
    return client.get_sample(sample_id)

@mcp.tool()
def list_samples(client, dataset_id: str = None, parent_id: str = None, limit: int = 100, **kwargs) -> List[Dict]:
    """List samples with optional filtering.

    Args:
        dataset_id (str, optional): Get samples from specific dataset
        parent_id (str, optional): Get child samples from parent
        limit (int): Maximum number of results to return (default: 100)
        **kwargs: Query parameters for filtering samples

    Returns:
        List[Dict]: Sample information
    """
    return client.list_samples(dataset_id, parent_id, limit, **kwargs)
    


if __name__ == "__main__":
    # initialize the client connection
    api_url = os.getenv("CRUCIBLE_API_URL")
    api_key = os.getenv("CRUCIBLE_API_KEY")

    if not api_url or not api_key:
        print("Error: CRUCIBLE_API_URL and CRUCIBLE_API_KEY environment variables must be set", file=sys.stderr)
        sys.exit(1)

    client = CrucibleClient(api_url, api_key)
    mcp.run(transport = "stdio")