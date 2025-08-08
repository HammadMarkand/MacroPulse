import os, datetime
from fastapi import APIRouter, HTTPException, Header
from backend.data_ingestion.fred_client import update_all as fred_update
from backend.db import SessionLocal
from backend.db.models import Indicator, IndicatorObservation
from sqlalchemy.orm import Session

router = APIRouter(prefix="/data", tags=["data-secure"])
CRON_TOKEN = os.getenv("CRON_TOKEN")

def _check(token):
    if not CRON_TOKEN: raise HTTPException(status_code=500, detail="CRON_TOKEN not set")
    if token != CRON_TOKEN: raise HTTPException(status_code=401, detail="Unauthorized")

@router.post("/refresh/fred/secure")
def refresh_fred_secure(x_cron_token: str = Header(None), last_n_days: int = 3650):
    _check(x_cron_token); return fred_update(last_n_days=last_n_days)

@router.get("/series/{code}")
def get_series(code: str, limit: int = 500):
    db: Session = SessionLocal()
    try:
        ind = db.query(Indicator).filter_by(code=code).first()
        if not ind: raise HTTPException(status_code=404, detail="Indicator not found")
        obs = (db.query(IndicatorObservation)
                .filter(IndicatorObservation.indicator_id==ind.id)
                .order_by(IndicatorObservation.date.desc())
                .limit(limit).all())
        return {"indicator":{"code":ind.code,"name":ind.name,"unit":ind.unit},
                "observations":[{"date":o.date.isoformat(),"value":o.value} for o in reversed(obs)]}
    finally:
        db.close()

@router.get("/health/data")
def data_health():
    db: Session = SessionLocal()
    try:
        now = datetime.datetime.utcnow()
        rows = []
        inds = db.query(Indicator).all()
        for ind in inds:
            last = (db.query(IndicatorObservation)
                    .filter(IndicatorObservation.indicator_id==ind.id)
                    .order_by(IndicatorObservation.date.desc()).first())
            staleness = (now - last.date).days if last else None
            rows.append({"code":ind.code,"name":ind.name,"source":ind.source,"frequency":ind.frequency,"unit":ind.unit,
                         "last_refreshed_at": ind.last_refreshed_at.isoformat() if ind.last_refreshed_at else None,
                         "last_obs_date": last.date.isoformat() if last else None,
                         "last_obs_value": last.value if last else None,
                         "staleness_days": staleness})
        return {"indicators": rows}
    finally:
        db.close()
