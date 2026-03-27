import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PATH_SKILLS: str = os.getenv("PATH_SKILLS", "./data/skills")
    PATH_DOCS: str = os.getenv("PATH_DOCS", "./data/docs")
    PORT: int = int(os.getenv("PORT", os.getenv("SERVER_PORT", 8000)))
    MCP_TRANSPORT: str = os.getenv("MCP_TRANSPORT", "stdio")

settings = Settings()
