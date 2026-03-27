import os
from fastmcp import FastMCP
from src.core.config import settings
from src.repositories.skill_repository import SkillRepository
from src.repositories.document_repository import DocumentRepository
from src.services.skill_service import SkillService
from src.services.document_service import DocumentService
from src.mcp.skill_tools import register_skill_tools
from src.mcp.document_tools import register_document_tools

def create_app() -> FastMCP:
    # Initialize components
    skill_repo = SkillRepository(settings.PATH_SKILLS)
    skill_service = SkillService(skill_repo)
    
    doc_repo = DocumentRepository(settings.PATH_DOCS)
    doc_service = DocumentService(doc_repo)
    
    # Initialize FastMCP server
    mcp = FastMCP("SkillServer")
    
    # Register tools
    register_skill_tools(mcp, skill_service)
    register_document_tools(mcp, doc_service)
    
    return mcp

mcp = create_app()

def run():
    mcp.run()

if __name__ == "__main__":
    run()
