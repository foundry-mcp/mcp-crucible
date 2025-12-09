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
# - where there are limits do they make sense
# - test it out!
# - add some benchmarks to see if this does better than 1.0.0-alpha : )

@mcp.tool
def get_project(project_id: str) -> Dict:
        """Get details of a specific project.

        Args:
            project_id (str): Unique project identifier. 
            Generally this is the same as the name of the project. 
            Case sensitive. 

        Returns:
            Dict: Project information including project_id, description, project_lead_email

        """
        return client.get_project(project_id)

@mcp.tool
def list_projects(orcid: str, limit: int = 100) -> List:
    """List all accessible projects.

    Args:
        orcid (str): Filter projects by those associated with a certain user
        limit (int): Maximum number of results to return (default: 100)

    Returns:
        List[Dict]: List of projects and their associated metadata including project_id, description, project_lead_email
    """
    return client.list_projects(orcid, limit)

@mcp.tool
def get_user(orcid: str = None, email: str = None) -> Dict:
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

@mcp.tool
def get_project_users(project_id: str, limit: int = 100) -> List[Dict]:
    """Get users associated with a project.

    **Requires admin permissions.**

    Args:
        project_id (str): Unique project identifier
        limit (int): Maximum number of results to return (default: 100)

    Returns:
        List[Dict]: Project team members (excludes project lead)
    """
    return client.get_project_users(project_id, limit)

@mcp.tool
def get_dataset(dsid: str, include_metadata: bool = False) -> Dict:
    """Get dataset details, optionally including scientific metadata.

    Args:
        dsid (str): Dataset unique identifier
        include_metadata (bool): Whether to include scientific metadata

    Returns:
        Dict: Dataset object with optional metadata
    """
    
    return client.get_dataset(dsid, include_metadata)
    
@mcp.tool
def list_datasets(sample_id: Optional[str] = None,
                  unique_id: Optional[str] = None,
                  public: Optional[bool] = None,
                  dataset_name: Optional[str] = None,
                  file_to_upload: Optional[str] = None,
                  owner_orcid: Optional[str] = None, 
                  project_id: Optional[str] = None,
                  instrument_name: Optional[str] = None,
                  source_folder: Optional[str] = None, 
                  creation_time: Optional[str] = None, 
                  data_format: Optional[str] = None, 
                  measurement: Optional[str] = None, 
                  session_name: Optional[str] = None, 
                  sha256_hash_file_to_upload: Optional[str] = None, 
                  keyword: Optional[str] = None,
                  limit: int = 100
                  ) -> List[Dict]:
    
    """List datasets with optional filtering.

    Args:
        sample_id (str, optional): If provided, returns datasets for this sample
        limit (int): Maximum number of results to return (default: 100)
        
        # Arguments for filtering dataset results 
        file_to_upload (str, optional): name of the file that was uploaded for the dataset
        owner_orcid (str, optional): orcid ID for the user who owns the dataset
        project_id (str, optional): project ID associated with the dataset, this is the descriptive ID not the internal database ID
        instrument_name (str, optional): name of the instrument on which the dataset was generated
        source_folder (str, optional): the folder where the dataset was ingested from
        creation_time (str, optional): the time when the dataset was generated in isoformat
        data_format (str, optional): the file extension of the dataset
        measurement (str, optional): the measurement used to generate the data
        session_name (str, optional): a metadata field provided by the user to group datasets taken within the same session
        sha256_hash_file_to_upload (str, optional): the sha256 hash for the main file "file_to_upload" associated with the dataaset
        keyword (str, optional): keyword tag associated with the dataset

        Note:   Values are case sensitive and
                expect exact matches with the exception of keywords.
                Keywords are case insensitive and will match substrings
                (eg. keyword = 'TEM' will return datasets with any of the following keywords: TEM, tem, Stem, etc)

    Returns:
        List[Dict]: Dataset objects matching filter criteria
    """

    filter_fields = {"unique_id": unique_id,
                     "public": public,
                     "dataset_name": dataset_name,
                     "file_to_upload": file_to_upload,
                     "owner_orcid": owner_orcid, 
                     "project_id": project_id,
                     "instrument_name": instrument_name,
                     "source_folder": source_folder, 
                     "creation_time": creation_time, 
                     "data_format": data_format, 
                     "measurement": measurement, 
                     "session_name": session_name, 
                     "sha256_hash_file_to_upload": sha256_hash_file_to_upload, 
                     "keyword": keyword
                    }
    
    provided_filters = {k: v for k, v in filter_fields.items() if v is not None}
    return client.list_datasets(sample_id, limit, **provided_filters)

@mcp.tool
def get_request_status(dsid: str, reqid: str, request_type: str) -> Dict:
    """Get the status of any type of request.

    Args:
        dsid (str): Dataset ID
        reqid (str): Request ID
        request_type (str): Type of request ('ingest' or 'scicat_update')

    Returns:
        Dict: Request status information
    """
    return client.get_request_status(dsid, reqid, request_type)

@mcp.tool
def get_thumbnails(dsid: str, limit: int = 100) -> List[Dict]:
    """Get thumbnails for a dataset.
    Args:
        dsid (str): Dataset ID
        limit (int): Maximum number of results to return (default: 100)

    Returns:
        List[Dict]: Thumbnail objects with base64-encoded images
    """
    return client.get_thumbnails(dsid, limit)

@mcp.tool
def get_associated_files(dsid: str, limit: int = 100) -> List[Dict]:
    """Get associated files for a dataset.

    Args:
        dsid (str): Dataset ID
        limit (int): Maximum number of results to return (default: 100)

    Returns:
        List[Dict]: File metadata with names, sizes, and hashes
    """
    return client.get_associated_files(dsid, limit)

@mcp.tool
def get_keywords(dsid: str = None, limit: int = 100) -> List[Dict]:
    """List keywords, option to filter on keywords associated with a given dataset.

    Args:
        limit (int): Maximum number of results to return (default: 100)

    Returns:
        List[Dict]: Keyword objects with keyword text and num_datasets counts
    """
    return client.get_keywords(dsid, limit)

@mcp.tool
def get_google_drive_location(dsid: str) -> List[Dict]:
    """Get current Google Drive location information for a dataset.

    Args:
        dsid (str): Dataset ID

    Returns:
        Dict: Google Drive location information
    """
    return client.get_google_drive_location(dsid)

@mcp.tool
def list_instruments(limit: int = 100) -> List[Dict]:
    """List all available instruments.

    Args:
        limit (int): Maximum number of results to return (default: 100)

    Returns:
        List[Dict]: Instrument objects with specifications and metadata
    """
    return client.list_instruments(limit)

@mcp.tool
def get_instrument(instrument_name: str = None, instrument_id: str = None) -> Dict:
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

@mcp.tool
def get_sample(sample_id: str) -> Dict:
    """Get sample information by ID.

    Args:
        sample_id (str): Sample unique identifier

    Returns:
        Dict: Sample information with associated datasets
    """
    return client.get_sample(sample_id)

@mcp.tool
def list_samples(dataset_id: str = None, parent_id: str = None, limit: int = 100, sample_name: str = None, owner_orcid: str = None, date_created: str = None, project_id: str = None, description: str = None) -> List[Dict]:
    """List samples with optional filtering.

    Args:
        dataset_id (str, optional): Get samples from specific dataset
        parent_id (str, optional): Get child samples from parent
        limit (int): Maximum number of results to return (default: 100)

        # arguments that can be used to filter samples
        sample_name (str, optional): human readable name/ID for the sample
        owner_orcid(str, optional): orcid for the user who owns the sample
        date_created(str, optional): date when the sample was created in isoformat
        project_id(str, optional): project name / ID that the sample is associated with
        description(str, optional): longer name describing the sample

    Returns:
        List[Dict]: Sample information
    """
    filter_fields = {"sample_name":sample_name,
                     "owner_orcid":owner_orcid, 
                     "date_created":date_created,
                     "project_id":project_id,
                     "description":description
                    }
    
    provided_filters = {k: v for k, v in filter_fields.items() if v is not None}
        
    return client.list_samples(dataset_id, parent_id, limit, **provided_filters)
    


if __name__ == "__main__":
    # initialize the client connection
    api_url = os.getenv("CRUCIBLE_API_URL")
    api_key = os.getenv("CRUCIBLE_API_KEY")

    if not api_url or not api_key:
        print("Error: CRUCIBLE_API_URL and CRUCIBLE_API_KEY environment variables must be set", file=sys.stderr)
        sys.exit(1)

    client = CrucibleClient(api_url, api_key)
    mcp.run(transport = "stdio")