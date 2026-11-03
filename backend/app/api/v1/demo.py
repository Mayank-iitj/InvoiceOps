from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.services.seed_service import reset_database, seed_database

router = APIRouter()

@router.post("/demo/reset", tags=["Demo"])
def demo_reset():
    reset_database()
    from backend.app.database import SessionLocal
    db = SessionLocal()
    try:
        result = seed_database(db, run_initial_match=True)
        return {"status": "reset_and_seeded", "details": result}
    finally:
        db.close()

@router.post("/demo/seed", tags=["Demo"])
def demo_seed(db: Session = Depends(get_db)):
    result = seed_database(db, run_initial_match=True)
    return {"status": "seeded", "details": result}

