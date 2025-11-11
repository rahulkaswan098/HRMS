import os
OPENAI_API_KEY="YOUR-OPENAI-API-KEY-HERE" 

# Flask Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB per file

# Application Settings
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 5000))

# Screening Settings
DEFAULT_MIN_EXPERIENCE = 0
DEFAULT_MAX_EXPERIENCE = 20
MAX_RESUMES_PER_UPLOAD = 50

# File Settings
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}