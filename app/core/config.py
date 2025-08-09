from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://atta_user:atta_password123@localhost:5432/atta_db"
    
    # JWT
    jwt_secret_key: str = "atta_jwt_secret_key_super_secure_2025"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_hours: int = 72
    
    # AWS S3
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    aws_s3_bucket: str = "atta-montacargas-files"
    
    # Upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_image_types: list = ["image/jpeg", "image/png", "image/jpg"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
