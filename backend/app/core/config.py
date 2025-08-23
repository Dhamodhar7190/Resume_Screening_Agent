import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str = "postgresql://username:password@localhost:5432/resume_screening_db"
    
    # API Keys
    google_api_key: Optional[str] = None
    
    # Application
    debug: bool = True
    max_file_size_mb: int = 10
    max_batch_size: int = 50
    upload_dir: str = "./uploads"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    
    # AI Settings
    default_ai_provider: str = "google"  # Google Gemini
    max_tokens: int = 4000
    temperature: float = 0.1
    
    # File Processing
    supported_formats: list = [".pdf", ".doc", ".docx"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)

# Print loaded settings for debugging
if settings.debug:
    print(f"🔧 Settings loaded:")
    print(f"   Database URL: {settings.database_url}")
    print(f"   AI Provider: {settings.default_ai_provider}")
    print(f"   Upload Dir: {settings.upload_dir}")
    print(f"   Debug Mode: {settings.debug}")