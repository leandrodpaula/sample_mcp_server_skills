from fastmcp import FastMCP
from typing import Optional
from src.services.document_service import DocumentService

def register_document_tools(mcp: FastMCP, service: DocumentService) -> None:
    @mcp.tool()
    async def download_document(userid: str, link: str, token: Optional[str] = None) -> str:
        """
        Downloads a document from a link and saves it for a specific user.
        
        Args:
            userid: The ID of the user
            link: The URL of the document to download
            token: Optional authorization token (required for private Google links)
        """
        return await service.download_document(userid, link, token)

    @mcp.tool()
    def save_base64_document(userid: str, filename: str, content_base64: str) -> str:
        """
        Saves a document from a base64 encoded string for a specific user.
        
        Args:
            userid: The ID of the user
            filename: The name of the file to save (e.g., 'report.pdf')
            content_base64: The base64 encoded content of the file
        """
        return service.save_base64_document(userid, filename, content_base64)

    @mcp.tool()
    def list_recent_documents(userid: str, minutes: int) -> str:
        """
        Lists documents that were uploaded or modified in the last specified number of minutes.
        
        Args:
            userid: The ID of the user
            minutes: The time window in minutes to look back
        """
        return service.list_recent_documents(userid, minutes)

    @mcp.tool()
    def search_documents(userid: str, query: str) -> str:
        """
        Searches the user's documents for a specific string match in the filename.
        
        Args:
            userid: The ID of the user
            query: Partially or fully matched filename string
        """
        return service.search_documents(userid, query)
