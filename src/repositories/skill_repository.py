import os
from typing import List, Optional
from src.core.config import settings

class SkillRepository:
    def __init__(self, base_path: str = settings.PATH_SKILLS):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def _get_user_path(self, userid: str) -> str:
        user_path = os.path.join(self.base_path, userid)
        os.makedirs(user_path, exist_ok=True)
        return user_path

    def _get_safe_filename(self, skill_name: str) -> str:
        return "".join([c for c in skill_name if c.isalnum() or c in ('-', '_')]).strip()

    def save_skill(self, userid: str, skill_name: str, content: str) -> bool:
        filename = self._get_safe_filename(skill_name)
        if not filename:
            return False
            
        user_path = self._get_user_path(userid)
        file_path = os.path.join(user_path, f"{filename}.md")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    def list_skills(self, userid: str) -> List[str]:
        user_path = os.path.join(self.base_path, userid)
        if not os.path.exists(user_path):
            return []
            
        return [f.replace(".md", "") for f in os.listdir(user_path) if f.endswith(".md")]

    def get_skill_content(self, userid: str, skill_name: str) -> Optional[str]:
        filename = self._get_safe_filename(skill_name)
        user_path = os.path.join(self.base_path, userid)
        file_path = os.path.join(user_path, f"{filename}.md")
        
        if not os.path.exists(file_path):
            return None
            
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
