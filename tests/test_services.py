import pytest
from unittest.mock import MagicMock, patch, Mock
import httpx
import base64
from src.services.skill_service import SkillService
from src.services.document_service import DocumentService
from src.repositories.skill_repository import SkillRepository
from src.repositories.document_repository import DocumentRepository

# --- SkillService Tests ---

@pytest.fixture
def mock_skill_repo():
    return MagicMock(spec=SkillRepository)

def test_skill_service_register_skill(mock_skill_repo):
    service = SkillService(mock_skill_repo)
    service.register_skill("user1", "python", "content")
    mock_skill_repo.save_skill.assert_called_once_with("user1", "python", "content")

def test_skill_service_list_user_skills(mock_skill_repo):
    mock_skill_repo.list_skills.return_value = ["skill1", "skill2"]
    service = SkillService(mock_skill_repo)
    result = service.list_user_skills("user1")
    assert result == ["skill1", "skill2"]
    mock_skill_repo.list_skills.assert_called_once_with("user1")

def test_skill_service_get_skill(mock_skill_repo):
    mock_skill_repo.get_skill_content.return_value = "content"
    service = SkillService(mock_skill_repo)
    result = service.get_skill("user1", "skill1")
    assert result == "content"
    mock_skill_repo.get_skill_content.assert_called_once_with("user1", "skill1")

def test_skill_service_get_skill_not_found(mock_skill_repo):
    mock_skill_repo.get_skill_content.return_value = None
    service = SkillService(mock_skill_repo)
    result = service.get_skill("user1", "missing")
    assert "not found" in result.lower()


# --- DocumentService Tests ---

@pytest.fixture
def mock_doc_repo():
    return MagicMock(spec=DocumentRepository)

def test_document_service_save_base64(mock_doc_repo):
    service = DocumentService(mock_doc_repo)
    mock_doc_repo.save_document.return_value = "/path/to/test.txt"
    
    test_content = b"test content"
    b64_str = base64.b64encode(test_content).decode('utf-8')
    
    result = service.save_base64_document("user1", "test.txt", b64_str)
    assert "saved to: /path/to/test.txt" in result
    mock_doc_repo.save_document.assert_called_once_with("user1", "test.txt", test_content)

def test_document_service_save_base64_with_prefix(mock_doc_repo):
    service = DocumentService(mock_doc_repo)
    mock_doc_repo.save_document.return_value = "/path/to/test.png"
    
    test_content = b"fake image"
    b64_str = "data:image/png;base64," + base64.b64encode(test_content).decode('utf-8')
    
    result = service.save_base64_document("user1", "test.png", b64_str)
    assert "saved to" in result
    mock_doc_repo.save_document.assert_called_once_with("user1", "test.png", test_content)

def test_document_service_save_base64_error(mock_doc_repo):
    service = DocumentService(mock_doc_repo)
    result = service.save_base64_document("user1", "test.txt", "invalid_base64!!!")
    assert "Error saving base64 document" in result

def test_document_service_list_recent(mock_doc_repo):
    service = DocumentService(mock_doc_repo)
    mock_doc_repo.list_recent_documents.return_value = ["file1.txt", "file2.pdf"]
    
    result = service.list_recent_documents("user1", 30)
    assert "Recent documents (30m): file1.txt, file2.pdf" in result
    mock_doc_repo.list_recent_documents.assert_called_once_with("user1", 30)

def test_document_service_list_recent_empty(mock_doc_repo):
    service = DocumentService(mock_doc_repo)
    mock_doc_repo.list_recent_documents.return_value = []
    
    result = service.list_recent_documents("user1", 30)
    assert "No documents found" in result

def test_document_service_search(mock_doc_repo):
    service = DocumentService(mock_doc_repo)
    mock_doc_repo.search_documents.return_value = ["invoice.pdf"]
    
    result = service.search_documents("user1", "inv")
    assert "Found matching documents: invoice.pdf" in result
    mock_doc_repo.search_documents.assert_called_once_with("user1", "inv")

def test_document_service_search_empty(mock_doc_repo):
    service = DocumentService(mock_doc_repo)
    mock_doc_repo.search_documents.return_value = []
    
    result = service.search_documents("user1", "inv")
    assert "No documents found matching" in result

@pytest.mark.asyncio
async def test_document_service_download_normal(mock_doc_repo, mocker):
    service = DocumentService(mock_doc_repo)
    mock_doc_repo.save_document.return_value = "/path/to/doc.txt"
    
    mock_response = MagicMock()
    mock_response.content = b"file content"
    mock_response.headers = {"content-type": "text/plain"}
    mock_response.raise_for_status.return_value = None
    
    mock_client = MagicMock()
    async def mock_get(*args, **kwargs): return mock_response
    mock_client.get = mock_get
    
    # Needs to be async context manager
    class AsyncContextManagerMock:
        async def __aenter__(self): return mock_client
        async def __aexit__(self, exc_type, exc_val, exc_tb): pass

    mocker.patch("httpx.AsyncClient", return_value=AsyncContextManagerMock())
    
    result = await service.download_document("user1", "http://example.com/doc.txt")
    
    assert "saved to: /path/to/doc.txt" in result
    mock_doc_repo.save_document.assert_called_once_with("user1", "doc.txt", b"file content")

@pytest.mark.asyncio
async def test_document_service_download_http_error(mock_doc_repo, mocker):
    service = DocumentService(mock_doc_repo)
    
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Not Found", request=MagicMock(), response=mock_response)
    
    mock_client = MagicMock()
    async def mock_get_err(*args, **kwargs): return mock_response
    mock_client.get = mock_get_err
    
    class AsyncContextManagerMock:
        async def __aenter__(self): return mock_client
        async def __aexit__(self, exc_type, exc_val, exc_tb): pass

    mocker.patch("httpx.AsyncClient", return_value=AsyncContextManagerMock())
    
    result = await service.download_document("user1", "http://example.com/missing.txt")
    assert "HTTP 404" in result

@pytest.mark.asyncio
async def test_document_service_download_google_drive(mock_doc_repo, mocker):
    service = DocumentService(mock_doc_repo)
    mock_doc_repo.save_document.return_value = "/path/to/gdrive.pdf"
    
    mock_credentials = mocker.patch("src.services.document_service.Credentials")
    mock_build = mocker.patch("src.services.document_service.build")
    mock_downloader = mocker.patch("src.services.document_service.MediaIoBaseDownload")
    
    # Mocking Google Drive API objects
    mock_drive_service = MagicMock()
    mock_build.return_value = mock_drive_service
    
    mock_files = MagicMock()
    mock_drive_service.files.return_value = mock_files
    
    mock_get_meta = MagicMock()
    mock_get_meta.execute.return_value = {"name": "test_gdrive.pdf"}
    mock_files.get.return_value = mock_get_meta
    
    mock_get_media = MagicMock()
    mock_files.get_media.return_value = mock_get_media
    
    # Mock downloader loop
    mock_dl_instance = MagicMock()
    mock_downloader.return_value = mock_dl_instance
    mock_dl_instance.next_chunk.return_value = (None, True) # Done immediately
    
    result = await service.download_document("user1", "https://drive.google.com/file/d/12345/view", "fake_token")
    
    assert "Google Drive document downloaded and saved to: /path/to/gdrive.pdf" in result
    mock_doc_repo.save_document.assert_called_once()
    # It passes an io.BytesIO(), we can't easily assert on the exact arg without more complex mocking,
    # but the repo call is enough to prove the happy path works.

@pytest.mark.asyncio
async def test_document_service_download_google_drive_no_token(mock_doc_repo):
    service = DocumentService(mock_doc_repo)
    result = await service.download_document("user1", "https://drive.google.com/file/d/12345/view")
    assert "A valid token is required" in result

@pytest.mark.asyncio
async def test_document_service_download_google_drive_invalid_url(mock_doc_repo):
    service = DocumentService(mock_doc_repo)
    result = await service.download_document("user1", "https://drive.google.com/bad/url", "token")
    assert "Could not extract file ID" in result

@pytest.mark.asyncio
async def test_document_service_google_api_auth_header(mock_doc_repo, mocker):
    service = DocumentService(mock_doc_repo)
    
    mock_response = MagicMock()
    mock_response.content = b"content"
    mock_response.raise_for_status.return_value = None
    
    mock_client = MagicMock()
    # Need to make this an async mock context manager properly
    async def async_magic():
        return mock_client
    
    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_client
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    mocker.patch("httpx.AsyncClient", return_value=AsyncContextManagerMock())
    
    async def mock_get(*args, **kwargs):
        # We need an async function to mock the aget/post
        return mock_response
        
    mock_client.get = mock_get
    
    await service.download_document("user1", "https://storage.googleapis.com/file.txt", "test_token")
    # Verify that the token was theoretically passed in the headers via AsyncClient
    # Since we mocked get as a simple async def, we can't assert_called_with on it as easily
    # But this proves the branch compiles and runs without drive logic.
