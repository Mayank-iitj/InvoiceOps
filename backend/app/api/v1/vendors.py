from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.all_models import Vendor
from backend.app.config import settings

router = APIRouter()

@router.get("/vendors", tags=["Vendors"])
def list_vendors(db: Session = Depends(get_db)):
    vendors = db.query(Vendor).all()
    return {
        "items": [
            {
                "id": v.id,
                "legal_name": v.legal_name,
                "display_name": v.display_name,
                "currency": v.currency,
                "is_active": bool(v.is_active),
                "version": v.version,
            }
            for v in vendors
        ]
    }

@router.get("/settings/policy", tags=["Settings"])
def get_matching_policy():
    return {
        "policy_version": settings.POLICY_VERSION,
        "default_currency": settings.DEFAULT_CURRENCY,
        "quantity_tolerance": str(settings.QUANTITY_TOLERANCE),
        "price_variance_percent": str(settings.PRICE_VARIANCE_PERCENT),
        "price_variance_absolute_inr": str(settings.PRICE_VARIANCE_ABSOLUTE),
        "price_variance_absolute_paise": str(settings.PRICE_VARIANCE_ABSOLUTE_PAISE),
        "extraction_confidence_threshold": settings.EXTRACTION_CONFIDENCE_THRESHOLD,
        "audit_retention_days": settings.AUDIT_RETENTION_DAYS,
        "max_upload_mb": settings.MAX_UPLOAD_MB,
    }

