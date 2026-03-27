import os
from fastmcp import FastMCP
from src.core.config import settings
from src.repositories.skill_repository import SkillRepository
from src.repositories.document_repository import DocumentRepository
from src.services.skill_service import SkillService
from src.services.document_service import DocumentService
from src.mcp.skill_tools import register_skill_tools
from src.mcp.document_tools import register_document_tools
import json
from starlette.requests import Request
from starlette.responses import Response

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

    @mcp.custom_route("/healthz", methods=["GET"], name="healthz", include_in_schema=True)
    async def healthz(request: Request) -> Response:
        """Health check endpoint for Cloud Run."""
        return Response(
            content=json.dumps({"status": "ok", "service": "sample-mcp-server-skills"}),
            media_type="application/json",
            status_code=200,
        )
    
    return mcp

mcp = create_app()

def run():
    if settings.MCP_TRANSPORT == "http":
        mcp.run(transport="http", host="0.0.0.0", port=settings.PORT)
    else:
        mcp.run(transport=settings.MCP_TRANSPORT)

if __name__ == "__main__":
    run()
