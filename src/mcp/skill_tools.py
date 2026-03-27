from fastmcp import FastMCP
from typing import List
from src.services.skill_service import SkillService

def register_skill_tools(mcp: FastMCP, service: SkillService) -> None:
    @mcp.tool()
    async def register_skill(userid: str, skill_name: str, content: str) -> str:
        """
        Registers or updates a skill for a specific user.
        
        Args:
            userid: The ID of the user owning the skill
            skill_name: The slug or name of the skill (e.g. 'coding-style')
            content: The technical instructions or content of the skill
        """
        return service.register_skill(userid, skill_name, content)

    @mcp.tool()
    async def list_skills(userid: str) -> List[str]:
        """
        Lists all skill names registered for a specific user.
        
        Args:
            userid: The ID of the user
        """
        return service.list_user_skills(userid)

    @mcp.tool()
    async def read_skill(userid: str, skill_name: str) -> str:
        """
        Reads the content of a specific skill for a user.
        
        Args:
            userid: The ID of the user
            skill_name: The name of the skill to read
        """
        return service.get_skill(userid, skill_name)
