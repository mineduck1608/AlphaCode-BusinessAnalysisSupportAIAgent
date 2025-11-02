from typing import Optional
try:
    from pydantic_settings import BaseSettings
except Exception:
    # Fallback for environments with older pydantic or missing pydantic_settings
    try:
        from pydantic import BaseSettings
    except Exception:
        # Minimal shim if BaseSettings is not available; Settings will behave like a plain object
        class BaseSettings(object):
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)


class Settings(BaseSettings):
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "alphacode"
    DATABASE_URL: Optional[str] = None  # Có thể override từ .env
    DB_URL: Optional[str] = None  # Alternative name from .env

    # AI / LLM
    GENAI_API_KEY: Optional[str] = None
    LLM_MODEL: Optional[str] = None
    EMBED_MODEL: Optional[str] = None
    CHROMA_PERSIST_DIR: Optional[str] = None

    # Security
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database URL helpers
    @property
    def sync_database_url(self) -> str:
        """
        URL để kết nối đồng bộ với SQLAlchemy.
        Nếu DATABASE_URL hoặc DB_URL được set trong env, sẽ dùng giá trị đó.
        """
        db_url = self.DATABASE_URL or self.DB_URL
        if db_url:
            return db_url
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    @property
    def async_database_url(self) -> str:
        """
        URL để kết nối bất đồng bộ với asyncpg.
        """
        db_url = self.DATABASE_URL or self.DB_URL
        if db_url:
            # Convert postgresql:// to postgresql+asyncpg://
            if db_url.startswith("postgresql://"):
                return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return db_url
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True         # phân biệt chữ hoa / thường
        env_file = ".env"             # đọc biến môi trường từ file .env
        extra = "allow"               # cho phép biến môi trường không khai báo trong class


# Khởi tạo settings global để import ở các module khác
settings = Settings()
