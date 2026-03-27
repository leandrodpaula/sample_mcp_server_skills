import pytest
from unittest.mock import MagicMock, patch
from fastmcp import FastMCP
from src.mcp.skill_tools import register_skill_tools
from src.mcp.document_tools import register_document_tools
from src.services.skill_service import SkillService
from src.services.document_service import DocumentService
from src.main import create_app

@pytest.mark.asyncio
async def test_register_skill_tools():
    mcp_mock = MagicMock(spec=FastMCP)
    mcp_mock.registered_tools = {}
    
    def mock_tool(*args, **kwargs):
        def decorator(func):
            mcp_mock.registered_tools[func.__name__] = func
            return func
        return decorator
        
    mcp_mock.tool = mock_tool
    service_mock = MagicMock(spec=SkillService)
    
    register_skill_tools(mcp_mock, service_mock)
    
    assert "register_skill" in mcp_mock.registered_tools
    assert "list_skills" in mcp_mock.registered_tools
    assert "read_skill" in mcp_mock.registered_tools
    
    # Call inner functions to boost coverage
    await mcp_mock.registered_tools["register_skill"]("u1", "s1", "c1")
    service_mock.register_skill.assert_called_once_with("u1", "s1", "c1")
    
    await mcp_mock.registered_tools["list_skills"]("u1")
    service_mock.list_user_skills.assert_called_once_with("u1")
    
    await mcp_mock.registered_tools["read_skill"]("u1", "s1")
    service_mock.get_skill.assert_called_once_with("u1", "s1")

@pytest.mark.asyncio
async def test_register_document_tools():
    mcp_mock = MagicMock(spec=FastMCP)
    mcp_mock.registered_tools = {}
    
    def mock_tool(*args, **kwargs):
        def decorator(func):
            mcp_mock.registered_tools[func.__name__] = func
            return func
        return decorator
        
    mcp_mock.tool = mock_tool
    service_mock = MagicMock(spec=DocumentService)
    
    register_document_tools(mcp_mock, service_mock)
    
    assert "download_document" in mcp_mock.registered_tools
    assert "save_base64_document" in mcp_mock.registered_tools
    assert "list_recent_documents" in mcp_mock.registered_tools
    assert "search_documents" in mcp_mock.registered_tools
    
    await mcp_mock.registered_tools["download_document"]("u1", "link")
    service_mock.download_document.assert_called_once_with("u1", "link", None)
    
    mcp_mock.registered_tools["save_base64_document"]("u1", "f1", "b64")
    service_mock.save_base64_document.assert_called_once_with("u1", "f1", "b64")
    
    mcp_mock.registered_tools["list_recent_documents"]("u1", 30)
    service_mock.list_recent_documents.assert_called_once_with("u1", 30)
    
    mcp_mock.registered_tools["search_documents"]("u1", "query")
    service_mock.search_documents.assert_called_once_with("u1", "query")

@patch('src.main.FastMCP')
def test_create_app(mcp_class_mock):
    # Mock settings to avoid creating actual dirs if it does
    with patch('src.core.config.settings.PATH_SKILLS', '/tmp/test_skills'), \
         patch('src.core.config.settings.PATH_DOCS', '/tmp/test_docs'):
        app = create_app()
    assert app is not None
