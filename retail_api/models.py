from sqlalchemy import Column, String, Float, Boolean, Integer
from database import Base

class Event(Base):

    __tablename__ = "events"

    event_id = Column(String, primary_key=True, index=True)

    store_id = Column(String)

    camera_id = Column(String)

    visitor_id = Column(String)

    event_type = Column(String)

    timestamp = Column(String)

    zone_id = Column(String, nullable=True)

    dwell_ms = Column(Integer)

    is_staff = Column(Boolean)

    confidence = Column(Float)

    queue_depth = Column(Integer, nullable=True)

    sku_zone = Column(String, nullable=True)

    session_seq = Column(Integer)