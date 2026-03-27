from typing import List, Optional
from src.repositories.skill_repository import SkillRepository

class SkillService:
    def __init__(self, repository: SkillRepository):
        self.repository = repository

    def register_skill(self, userid: str, skill_name: str, content: str) -> str:
        success = self.repository.save_skill(userid, skill_name, content)
        if success:
            return f"Skill '{skill_name}' registered successfully for user {userid}."
        else:
            return "Error: Invalid skill name."

    def list_user_skills(self, userid: str) -> List[str]:
        return sorted(self.repository.list_skills(userid))

    def get_skill(self, userid: str, skill_name: str) -> str:
        content = self.repository.get_skill_content(userid, skill_name)
        if content is None:
            return f"Error: Skill '{skill_name}' not found for user {userid}."
        return content
