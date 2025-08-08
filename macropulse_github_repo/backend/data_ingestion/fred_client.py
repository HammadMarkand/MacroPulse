import os, requests, datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from backend.db import SessionLocal
from backend.db.models import Indicator, IndicatorObservation

FRED_API_KEY = os.getenv("FRED_API_KEY")
FRED_BASE = "https://api.stlouisfed.org/fred"

DEFAULT_SERIES = [
    {"code":"FEDFUNDS","name":"Effective Federal Funds Rate","frequency":"D","unit":"%"},
    {"code":"UNRATE","name":"Unemployment Rate","frequency":"M","unit":"%"},
    {"code":"CPIAUCSL","name":"CPI All Urban Consumers","frequency":"M","unit":"Index 1982-84=100"},
    {"code":"GDPC1","name":"Real GDP","frequency":"Q","unit":"Billions Chained 2017$"}
]

def _ensure_indicators(db: Session):
    for s in DEFAULT_SERIES:
        if not db.query(Indicator).filter_by(code=s["code"]).first():
            db.add(Indicator(code=s["code"], source="FRED", name=s["name"], frequency=s["frequency"], unit=s["unit"]))
    db.commit()

def fetch_series_observations(series_id: str, last_n_days: Optional[int]=None) -> Dict:
    assert FRED_API_KEY, "FRED_API_KEY not set"
    params = {"series_id": series_id, "api_key": FRED_API_KEY, "file_type": "json", "observation_start": "1900-01-01"}
    if last_n_days:
        start = (datetime.datetime.utcnow() - datetime.timedelta(days=last_n_days)).date().isoformat()
        params["observation_start"] = start
    r = requests.get(f"{FRED_BASE}/series/observations", params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def upsert(db: Session, code: str, observations: List[Dict]) -> int:
    ind = db.query(Indicator).filter_by(code=code).first()
    if not ind:
        ind = Indicator(code=code, source="FRED", name=code, frequency="", unit="")
        db.add(ind); db.commit(); db.refresh(ind)
    inserted = 0
    from sqlalchemy.exc import IntegrityError
    for obs in observations:
        if obs.get("value") in (".", "", None): continue
        try:
            date = datetime.datetime.fromisoformat(obs["date"])
        except Exception:
            date = datetime.datetime.strptime(obs["date"], "%Y-%m-%d")
        row = IndicatorObservation(indicator_id=ind.id, date=date, value=float(obs["value"]))
        db.add(row)
        try:
            db.commit(); inserted += 1
        except IntegrityError:
            db.rollback()
    ind.last_refreshed_at = datetime.datetime.utcnow(); db.commit()
    return inserted

def update_all(last_n_days: int = 3650) -> dict:
    db = SessionLocal()
    try:
        _ensure_indicators(db)
        results = {}
        for s in DEFAULT_SERIES:
            data = fetch_series_observations(s["code"], last_n_days=last_n_days)
            obs = data.get("observations", [])
            results[s["code"]] = upsert(db, s["code"], obs)
        return {"status":"ok","inserted":results}
    finally:
        db.close()
