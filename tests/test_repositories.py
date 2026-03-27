import os
import pytest
from src.repositories.skill_repository import SkillRepository
from src.repositories.document_repository import DocumentRepository

def test_skill_repository_initialization(tmp_path):
    repo = SkillRepository(base_path=str(tmp_path))
    assert os.path.exists(tmp_path)
    assert repo.base_path == str(tmp_path)

def test_skill_repository_save_and_get(tmp_path):
    repo = SkillRepository(base_path=str(tmp_path))
    userid = "test_user"
    skill_name = "test_skill"
    content = "This is a test skill."

    # Test Save
    assert repo.save_skill(userid, skill_name, content) is True
    file_path = os.path.join(repo.base_path, userid, f"{skill_name}.md")
    assert os.path.exists(file_path)
    
    with open(file_path, "r", encoding="utf-8") as f:
        saved_content = f.read()
    assert saved_content == content

    # Test Get
    retrieved_content = repo.get_skill_content(userid, skill_name)
    assert retrieved_content == content

def test_skill_repository_get_nonexistent(tmp_path):
    repo = SkillRepository(base_path=str(tmp_path))
    content = repo.get_skill_content("test_user", "nonexistent")
    assert content is None

def test_skill_repository_list_skills(tmp_path):
    repo = SkillRepository(base_path=str(tmp_path))
    userid = "list_user"
    repo.save_skill(userid, "skill1", "content1")
    repo.save_skill(userid, "skill2", "content2")

    skills = repo.list_skills(userid)
    assert len(skills) == 2
    assert "skill1" in skills
    assert "skill2" in skills

def test_skill_repository_list_empty(tmp_path):
    repo = SkillRepository(base_path=str(tmp_path))
    assert repo.list_skills("ghost_user") == []

# --- DocumentRepository Tests ---

def test_document_repository_initialization(tmp_path):
    repo = DocumentRepository(base_path=str(tmp_path))
    assert os.path.exists(tmp_path)
    assert repo.base_path == str(tmp_path)

def test_document_repository_save_document(tmp_path):
    repo = DocumentRepository(base_path=str(tmp_path))
    userid = "doc_user"
    filename = "test_doc.pdf"
    content = b"fake pdf content"

    file_path = repo.save_document(userid, filename, content)
    assert os.path.exists(file_path)
    assert os.path.basename(file_path) == filename

    with open(file_path, "rb") as f:
        saved_content = f.read()
    assert saved_content == content

def test_document_repository_save_unsafe_filename(tmp_path):
    repo = DocumentRepository(base_path=str(tmp_path))
    userid = "doc_user"
    filename = "../../../etc/passwd"
    content = b"hacked"

    file_path = repo.save_document(userid, filename, content)
    # The safe filename calculation should strip non-alphanumeric/dot/dash/underscore
    # So "../../../etc/passwd" becomes "......etcpasswd"
    expected_safe_name = "......etcpasswd"
    
    assert os.path.basename(file_path) == expected_safe_name
    assert str(tmp_path) in file_path # Ensures it stayed within the base path
    
def test_document_repository_list_recent_documents(tmp_path):
    import time
    repo = DocumentRepository(base_path=str(tmp_path))
    userid = "recent_user"
    
    # Save a file right now (should be recent)
    path1 = repo.save_document(userid, "new.txt", b"new")
    
    # Save a file and modify its time to be 2 hours ago
    path2 = repo.save_document(userid, "old.txt", b"old")
    two_hours_ago = time.time() - (2 * 60 * 60 + 10)
    os.utime(path2, (two_hours_ago, two_hours_ago))
    
    recent = repo.list_recent_documents(userid, 60) # Last 60 mins
    assert "new.txt" in recent
    assert "old.txt" not in recent

def test_document_repository_list_recent_empty(tmp_path):
    repo = DocumentRepository(base_path=str(tmp_path))
    assert repo.list_recent_documents("ghost", 10) == []

def test_document_repository_search_documents(tmp_path):
    repo = DocumentRepository(base_path=str(tmp_path))
    userid = "search_user"
    
    repo.save_document(userid, "report_2023.pdf", b"data")
    repo.save_document(userid, "invoice_june.png", b"data")
    repo.save_document(userid, "invoice_july.png", b"data")
    
    results = repo.search_documents(userid, "invo")
    assert len(results) == 2
    assert "invoice_june.png" in results
    assert "invoice_july.png" in results
    
    results = repo.search_documents(userid, "2023")
    assert len(results) == 1
    assert "report_2023.pdf" in results

def test_document_repository_search_empty(tmp_path):
    repo = DocumentRepository(base_path=str(tmp_path))
    assert repo.search_documents("ghost", "query") == []

    repo = DocumentRepository(base_path=str(tmp_path))
    userid = "doc_user"
    filename = "!@#$%^"
    content = b"content"

    file_path = repo.save_document(userid, filename, content)
    # "downloaded_file" is the fallback for completely unsafe names
    expected_safe_name = "downloaded_file"
    
    assert os.path.basename(file_path) == expected_safe_name
    assert str(tmp_path) in file_path
