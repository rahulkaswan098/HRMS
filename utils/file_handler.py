import os
import uuid
from werkzeug.utils import secure_filename
from typing import List

class FileHandler:
    """Handle file uploads and storage"""
    
    def __init__(self, upload_folder: str = 'uploads'):
        self.upload_folder = upload_folder
        self.allowed_extensions = {'pdf', 'doc', 'docx'}
        
        # Create upload folder if it doesn't exist
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_files(self, files) -> tuple:
        """
        Save uploaded files and return their paths
        
        Args:
            files: FileStorage objects from Flask request
            
        Returns:
            Tuple of (saved_paths, session_id)
        """
        session_id = str(uuid.uuid4())
        session_folder = os.path.join(self.upload_folder, session_id)
        os.makedirs(session_folder, exist_ok=True)
        
        saved_paths = []
        
        for file in files:
            if file and self.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
                filepath = os.path.join(session_folder, unique_filename)
                file.save(filepath)
                saved_paths.append(filepath)
        
        return saved_paths, session_id
    
    def cleanup_session(self, session_id: str):
        """Delete all files for a session"""
        session_folder = os.path.join(self.upload_folder, session_id)
        if os.path.exists(session_folder):
            for filename in os.listdir(session_folder):
                file_path = os.path.join(session_folder, filename)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error removing file {file_path}: {str(e)}")
            try:
                os.rmdir(session_folder)
            except Exception as e:
                print(f"Error removing folder {session_folder}: {str(e)}")