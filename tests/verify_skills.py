import asyncio
import os
import shutil
from src.services.skill_service import SkillService
from src.services.document_service import DocumentService
from src.repositories.skill_repository import SkillRepository
from src.repositories.document_repository import DocumentRepository
from src.core.config import settings

async def test_server():
    print("--- Starting Server Tests (Clean Architecture) ---")
    
    # Setup components
    skill_repo = SkillRepository(settings.PATH_SKILLS)
    skill_service = SkillService(skill_repo)
    
    doc_repo = DocumentRepository(settings.PATH_DOCS)
    doc_service = DocumentService(doc_repo)
    
    # Paths to test
    PATH_SKILLS = settings.PATH_SKILLS
    PATH_DOCS = settings.PATH_DOCS

    # Clean up before tests
    for p in ["./data", PATH_SKILLS, PATH_DOCS]:
        if os.path.exists(p):
            try:
                shutil.rmtree(p)
            except:
                pass
    os.makedirs(PATH_SKILLS, exist_ok=True)
    os.makedirs(PATH_DOCS, exist_ok=True)
    
    userid_1 = "user_123"
    
    # --- Skills Tests ---
    print(f"Testing skills for {userid_1}...")
    skill_service.register_skill(userid=userid_1, skill_name="python-pro", content="Python Expert")
    skills = skill_service.list_user_skills(userid=userid_1)
    assert "python-pro" in skills
    print("Skills OK.")

    # --- Document Tests ---
    print(f"Testing document download for {userid_1}...")
    # Use a real public URL for testing
    test_url = "https://raw.githubusercontent.com/leandrodpaula/tutto-mcp-server/main/pyproject.toml"
    res = await doc_service.download_document(userid=userid_1, link=test_url)
    print(res)
    assert "saved to" in res
    
    # Verify file exists
    user_doc_path = os.path.join(PATH_DOCS, userid_1)
    files = os.listdir(user_doc_path)
    print(f"Downloaded files: {files}")
    assert len(files) > 0
    assert "pyproject.toml" in files
    
    # --- Base64 Document Tests ---
    print(f"Testing base64 document save for {userid_1}...")
    import base64
    test_content = b"Hello from base64!"
    b64_string = base64.b64encode(test_content).decode('utf-8')
    res_b64 = doc_service.save_base64_document(userid_1, "hello_b64.txt", b64_string)
    print(res_b64)
    assert "saved to" in res_b64
    
    files_after = os.listdir(user_doc_path)
    print(f"Files after base64 save: {files_after}")
    assert "hello_b64.txt" in files_after
    
    # Verify content
    with open(os.path.join(user_doc_path, "hello_b64.txt"), "rb") as f:
        saved_content = f.read()
    assert saved_content == test_content
    
    print("--- All tests passed! ---")
    
    print("--- All tests passed! ---")

if __name__ == "__main__":
    asyncio.run(test_server())
