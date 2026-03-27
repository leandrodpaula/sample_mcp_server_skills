import os
from src.core.config import settings

class DocumentRepository:
    def __init__(self, base_path: str = settings.PATH_DOCS):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def _get_user_path(self, userid: str) -> str:
        user_path = os.path.join(self.base_path, userid)
        os.makedirs(user_path, exist_ok=True)
        return user_path

    def save_document(self, userid: str, filename: str, content: bytes) -> str:
        user_path = self._get_user_path(userid)
        # Basic filename safety
        safe_filename = "".join([c for c in filename if c.isalnum() or c in ('.', '-', '_')]).strip()
        if not safe_filename:
            safe_filename = "downloaded_file"
            
        file_path = os.path.join(user_path, safe_filename)
        
        with open(file_path, "wb") as f:
            f.write(content)
        return file_path

    def list_recent_documents(self, userid: str, minutes: int) -> list[str]:
        import time
        user_path = os.path.join(self.base_path, userid)
        if not os.path.exists(user_path):
            return []
            
        current_time = time.time()
        threshold_time = current_time - (minutes * 60)
        
        recent_files = []
        for filename in os.listdir(user_path):
            file_path = os.path.join(user_path, filename)
            if os.path.isfile(file_path):
                if os.path.getmtime(file_path) >= threshold_time:
                    recent_files.append(filename)
        return recent_files

    def search_documents(self, userid: str, query: str) -> list[str]:
        user_path = os.path.join(self.base_path, userid)
        if not os.path.exists(user_path):
            return []
            
        query_lower = query.lower()
        matched_files = []
        for filename in os.listdir(user_path):
            if os.path.isfile(os.path.join(user_path, filename)) and query_lower in filename.lower():
                matched_files.append(filename)
        return matched_files
