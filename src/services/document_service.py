import os
import httpx
import re
import base64
from typing import Optional
from src.repositories.document_repository import DocumentRepository
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import io
from googleapiclient.http import MediaIoBaseDownload

class DocumentService:
    def __init__(self, repository: DocumentRepository):
        self.repository = repository

    def _extract_drive_file_id(self, url: str) -> Optional[str]:
        # Typical format: https://drive.google.com/file/d/FILE_ID/view
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)
        # Alternate format: https://drive.google.com/open?id=FILE_ID
        match = re.search(r'id=([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)
        return None

    async def download_document(self, userid: str, link: str, token: Optional[str] = None) -> str:
        
        # --- Google Drive Specific Handling ---
        if "drive.google.com" in link:
            file_id = self._extract_drive_file_id(link)
            if not file_id:
                return "Error: Could not extract file ID from Google Drive URL."
                
            if not token:
                return "Error: A valid token is required to download from Google Drive."

            try:
                # Use provided token as an access token
                creds = Credentials(token=token)
                drive_service = build('drive', 'v3', credentials=creds)
                
                # Get file metadata to determine name
                request_meta = drive_service.files().get(fileId=file_id, fields="name")
                file_metadata = request_meta.execute()
                filename = file_metadata.get('name', 'drive_downloaded_file')
                
                # Download file content
                request_content = drive_service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request_content)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()

                # Save file
                saved_path = self.repository.save_document(userid, filename, fh.getvalue())
                return f"Google Drive document downloaded and saved to: {saved_path}"
                
            except Exception as e:
                return f"Error downloading from Google Drive: {str(e)}"
        
        # --- Standard HTTP Download ---
        headers = {}
        # Try authorization header for google storage links too
        if "googleapis.com" in link and token:
            headers["Authorization"] = f"Bearer {token}"
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(link, headers=headers, follow_redirects=True)
                response.raise_for_status()
                
                # Try to get filename from content-disposition
                filename = "downloaded_file"
                cd = response.headers.get("content-disposition")
                if cd and "filename=" in cd:
                    filename = cd.split("filename=")[1].strip('"')
                else:
                    # Fallback to URL path
                    path_name = os.path.basename(link.split("?")[0])
                    if path_name:
                        filename = path_name
                
                # Determine extension if missing and possible
                if "." not in filename:
                    ct = response.headers.get("content-type", "")
                    if "pdf" in ct:
                        filename += ".pdf"
                    elif "text/plain" in ct:
                        filename += ".txt"
                    elif "application/vnd.openxmlformats-officedocument" in ct:
                        filename += ".docx"
                
                saved_path = self.repository.save_document(userid, filename, response.content)
                return f"Document downloaded and saved to: {saved_path}"
                
        except httpx.HTTPStatusError as e:
            return f"Error downloading document: HTTP {e.response.status_code} - {str(e)}"
        except Exception as e:
            return f"Error downloading document: {str(e)}"

    def save_base64_document(self, userid: str, filename: str, content_base64: str) -> str:
        """
        Decodes a base64 string and saves it as a document.
        """
        try:
            # Clean up potential data URI scheme parts (e.g., "data:image/png;base64,")
            if "," in content_base64:
                content_base64 = content_base64.split(",")[1]
                
            decoded_content = base64.b64decode(content_base64)
            saved_path = self.repository.save_document(userid, filename, decoded_content)
            return f"Base64 document saved to: {saved_path}"
        except Exception as e:
            return f"Error saving base64 document: {str(e)}"

    def list_recent_documents(self, userid: str, minutes: int) -> str:
        """
        Lists documents uploaded by the user in the last N minutes.
        """
        try:
            files = self.repository.list_recent_documents(userid, minutes)
            if not files:
                return f"No documents found for user {userid} in the last {minutes} minutes."
            return f"Recent documents ({minutes}m): " + ", ".join(files)
        except Exception as e:
            return f"Error listing recent documents: {str(e)}"

    def search_documents(self, userid: str, query: str) -> str:
        """
        Searches for documents by filename query.
        """
        try:
            files = self.repository.search_documents(userid, query)
            if not files:
                return f"No documents found matching '{query}' for user {userid}."
            return f"Found matching documents: " + ", ".join(files)
        except Exception as e:
            return f"Error searching documents: {str(e)}"

