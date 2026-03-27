import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PATH_SKILLS: str = os.getenv("PATH_SKILLS", "./data/skills")
    PATH_DOCS: str = os.getenv("PATH_DOCS", "./data/docs")

settings = Settings()
