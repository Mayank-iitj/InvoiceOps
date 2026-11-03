import os
from decimal import Decimal
from typing import List

class Settings:
    APP_ENV: str = os.getenv("APP_ENV", "demo")
    APP_NAME: str = os.getenv("APP_NAME", "InvoiceOps")
    API_PREFIX: str = os.getenv("API_PREFIX", "/api/v1")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/invoiceops.db")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./data/uploads")
    MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "15"))
    ALLOWED_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,*").split(",")
    ]
    JWT_SECRET: str = os.getenv("JWT_SECRET", "demo-secret-key-change-in-prod")
    DEFAULT_CURRENCY: str = os.getenv("DEFAULT_CURRENCY", "INR")
    
    # Matching policy
    PRICE_VARIANCE_PERCENT: Decimal = Decimal(os.getenv("PRICE_VARIANCE_PERCENT", "0.50"))
    PRICE_VARIANCE_ABSOLUTE_PAISE: Decimal = Decimal(os.getenv("PRICE_VARIANCE_ABSOLUTE_PAISE", "100")) # in paise, i.e. 1.00 INR
    PRICE_VARIANCE_ABSOLUTE: Decimal = PRICE_VARIANCE_ABSOLUTE_PAISE / Decimal("100")
    QUANTITY_TOLERANCE: Decimal = Decimal(os.getenv("QUANTITY_TOLERANCE", "0"))
    EXTRACTION_CONFIDENCE_THRESHOLD: float = float(os.getenv("EXTRACTION_CONFIDENCE_THRESHOLD", "0.90"))
    POLICY_VERSION: str = "demo-policy-1.0"
    AUDIT_RETENTION_DAYS: int = int(os.getenv("AUDIT_RETENTION_DAYS", "365"))

settings = Settings()

