from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, UniqueConstraint
import datetime

Base = declarative_base()

class Indicator(Base):
    __tablename__ = "indicators"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, index=True)
    source = Column(String)
    name = Column(String)
    frequency = Column(String, default="D")
    unit = Column(String, default="")
    last_refreshed_at = Column(DateTime, nullable=True)

class IndicatorObservation(Base):
    __tablename__ = "indicator_observations"
    id = Column(Integer, primary_key=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id"), index=True)
    date = Column(DateTime, index=True)
    value = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    __table_args__ = (UniqueConstraint("indicator_id", "date", name="uq_indicator_date"),)
