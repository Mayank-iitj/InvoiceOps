import pytest
from backend.app.database import SessionLocal, Base, engine
from backend.app.models.all_models import BenchmarkAnswerKey, Invoice, ExceptionRecord
from backend.app.services.seed_service import seed_database
from backend.app.services.ap_data_loader import feed_ap_data
from backend.app.services.matching_engine import run_three_way_match

@pytest.fixture(scope="module", autouse=True)
def setup_benchmark_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db, run_initial_match=False)
    feed_ap_data(db, run_matches=False)
    db.close()
    yield

def test_benchmark_scenarios_s01_to_s04_pass():
    db = SessionLocal()
    try:
        for inv_id in ["I-2001", "I-2002", "I-2003", "I-2004"]:
            run, exs = run_three_way_match(db, inv_id)
            assert run.overall_status == "PASS"
            assert len(exs) == 0
    finally:
        db.close()

def test_benchmark_scenario_s05_tolerance_auto_close():
    """S05 (I-2005): BOM-5531 discrepancy INR 80 <= 500 and <= 2% -> Auto-close under Rule R1"""
    db = SessionLocal()
    try:
        run, exs = run_three_way_match(db, "I-2005")
        assert run.overall_status == "PASS"
        assert len(exs) == 0
    finally:
        db.close()

def test_benchmark_scenario_s06_short_ship():
    """S06 (I-2006): INV-V01-2209 short shipment -> warehouse_lead owner"""
    db = SessionLocal()
    try:
        run, exs = run_three_way_match(db, "I-2006")
        assert run.overall_status == "BLOCKED"
        codes = [e.code for e in exs]
        owners = [e.owner_role for e in exs]
        assert "QTY_EXCEEDS_RECEIVED" in codes
        assert "warehouse_lead" in owners
    finally:
        db.close()

def test_benchmark_scenario_s07_price_variance_rejected():
    """S07 (I-2007): HE-8842 future price row cannot justify -> buyer owner"""
    db = SessionLocal()
    try:
        run, exs = run_three_way_match(db, "I-2007")
        assert run.overall_status == "BLOCKED"
        codes = [e.code for e in exs]
        owners = [e.owner_role for e in exs]
        assert "PRICE_VARIANCE" in codes
        assert "buyer" in owners
    finally:
        db.close()

def test_benchmark_scenario_s08_price_variance_amendment():
    """S08 (I-2008): KP/10/0431 price amendment effective before PO date -> buyer owner to accept"""
    db = SessionLocal()
    try:
        run, exs = run_three_way_match(db, "I-2008")
        assert run.overall_status == "BLOCKED"
        codes = [e.code for e in exs]
        owners = [e.owner_role for e in exs]
        assert "PRICE_VARIANCE" in codes
        assert "buyer" in owners
    finally:
        db.close()

def test_benchmark_scenario_s09_uom_mismatch():
    """S09 (I-2009): INV-V01-2214 2000 EA vs 20 BOX, disputed > 50,000 -> ap_manager owner"""
    db = SessionLocal()
    try:
        run, exs = run_three_way_match(db, "I-2009")
        assert run.overall_status == "BLOCKED"
        codes = [e.code for e in exs]
        owners = [e.owner_role for e in exs]
        assert "UOM_MISMATCH" in codes
        assert "ap_manager" in owners
    finally:
        db.close()

def test_benchmark_scenario_s10_duplicate_prior_billing():
    """S10 (I-2010): BOM-5602 duplicate of settled I-2000 -> ap_clerk owner"""
    db = SessionLocal()
    try:
        run, exs = run_three_way_match(db, "I-2010")
        assert run.overall_status == "BLOCKED"
        codes = [e.code for e in exs]
        owners = [e.owner_role for e in exs]
        assert "DUPLICATE_INVOICE" in codes
        assert "ap_clerk" in owners
    finally:
        db.close()

def test_benchmark_scenario_s11_extra_freight_charge():
    """S11 (I-2011): SSG/2610/91 freight charge when prepaid -> buyer owner"""
    db = SessionLocal()
    try:
        run, exs = run_three_way_match(db, "I-2011")
        assert run.overall_status == "BLOCKED"
        codes = [e.code for e in exs]
        owners = [e.owner_role for e in exs]
        assert "EXTRA_CHARGE" in codes
        assert "buyer" in owners
    finally:
        db.close()

def test_benchmark_scenario_s12_quantity_conflict():
    """S12 (I-2012): BOM-5617 32 vs 40 conflict -> warehouse_lead owner"""
    db = SessionLocal()
    try:
        run, exs = run_three_way_match(db, "I-2012")
        assert run.overall_status == "BLOCKED"
        codes = [e.code for e in exs]
        owners = [e.owner_role for e in exs]
        assert "QTY_EXCEEDS_RECEIVED" in codes
        assert "warehouse_lead" in owners
    finally:
        db.close()

