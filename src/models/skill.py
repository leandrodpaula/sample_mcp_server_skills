from pydantic import BaseModel, Field
from typing import Optional

class SkillCreate(BaseModel):
    userid: str
    skill_name: str
    content: str

class Skill(BaseModel):
    name: str
    content: str
