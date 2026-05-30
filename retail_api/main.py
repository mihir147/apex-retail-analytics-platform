from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from logger import logger
from database import engine, SessionLocal, Base
from models import Event as EventModel
from schemas import Event
import time
import uuid
from datetime import datetime, timezone
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Retail Analytics API"
)

@app.middleware("http")
async def log_requests(request: Request, call_next):

    trace_id = str(uuid.uuid4())
    start_time = time.time()

    response = await call_next(request)

    latency_ms = round((time.time() - start_time) * 1000, 2)

    logger.info(
        f"trace_id={trace_id} endpoint={request.url.path} latency_ms={latency_ms} status_code={response.status_code}"
    )

    response.headers["X-Trace-ID"] = trace_id

    return response

Base.metadata.create_all(bind=engine)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@app.get("/")
def home():

    return {
        "message": "Retail Analytics API Running"
    }


# Ingest events endpoint
@app.post("/events/ingest")
def ingest_events(
    events: List[Event],
    db: Session = Depends(get_db)
):

    received = len(events)
    logger.info(

        f"endpoint=/events/ingest "

        f"event_count={received}"

    )

    if received > 500:
        return {
            "error": "Maximum 500 events allowed per batch"
        }

    inserted = 0
    duplicates = 0
    errors = []

    for event in events:

        existing = db.query(EventModel).filter(
            EventModel.event_id == event.event_id
        ).first()

        if existing:
            duplicates += 1
            continue

        try:

            db_event = EventModel(
                event_id=event.event_id,
                store_id=event.store_id,
                camera_id=event.camera_id,
                visitor_id=event.visitor_id,
                event_type=event.event_type,
                timestamp=event.timestamp,
                zone_id=event.zone_id,
                dwell_ms=event.dwell_ms,
                is_staff=event.is_staff,
                confidence=event.confidence,
                queue_depth=event.metadata.queue_depth,
                sku_zone=event.metadata.sku_zone,
                session_seq=event.metadata.session_seq
            )

            db.add(db_event)
            inserted += 1

        except Exception as e:

            errors.append(str(e))

    db.commit()

    return {
        "received": received,
        "inserted": inserted,
        "duplicates": duplicates,
        "errors": errors
    }

@app.get("/health")
def health(
    db: Session = Depends(get_db)
):

    try:

        total_events = db.query(EventModel).count()

        latest_event = db.query(
            EventModel
        ).order_by(
            EventModel.timestamp.desc()
        ).first()

        warning = None

        if latest_event:

            try:
                event_time = datetime.fromisoformat(
                    latest_event.timestamp.replace("Z", "+00:00")
                )

                now = datetime.now(timezone.utc)

                minutes_since_last_event = (
                    now - event_time
                ).total_seconds() / 60

                if minutes_since_last_event > 10:
                    warning = "STALE_FEED"

            except Exception:
                warning = None

        return {
            "status": "UP",
            "total_events": total_events,
            "last_event_timestamp": latest_event.timestamp if latest_event else None,
            "warning": warning
        }

    except Exception:

        raise HTTPException(
            status_code=503,
            detail={
                "error": "DATABASE_UNAVAILABLE",
                "message": "Database service is temporarily unavailable"
            }
        )
    
@app.get("/stores/{store_id}/metrics")
def get_metrics(
    store_id: str,
    db: Session = Depends(get_db)
):
    try:
        events = db.query(EventModel).filter(
            EventModel.store_id == store_id,
            EventModel.is_staff == False
        ).all()

        unique_visitors = len(
            set(e.visitor_id for e in events)
        )

        dwell_events = [
            e for e in events
            if e.event_type == "ZONE_DWELL"
        ]

        avg_dwell = 0

        if dwell_events:
            avg_dwell = sum(
                e.dwell_ms for e in dwell_events
            ) / len(dwell_events)

        return {
            "store_id": store_id,
            "unique_visitors": unique_visitors,
            "conversion_rate": 0,
            "avg_dwell_ms": round(avg_dwell, 2),
            "queue_depth": 0,
            "abandonment_rate": 0
        }
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "DATABASE_UNAVAILABLE"
            }
        )

@app.get("/stores/{store_id}/funnel")
def get_funnel(
    store_id: str,
    db: Session = Depends(get_db)
):
    try:
        events = db.query(EventModel).filter(
            EventModel.store_id == store_id,
            EventModel.is_staff == False
        ).all()

        visitors = set(e.visitor_id for e in events)

        zone_visitors = set(
            e.visitor_id
            for e in events
            if e.event_type == "ZONE_ENTER"
        )

        billing_visitors = set(
            e.visitor_id
            for e in events
            if e.event_type == "BILLING_QUEUE_JOIN"
        )

        purchase_visitors = set(
            e.visitor_id
            for e in events
            if e.event_type == "PURCHASE"
        )

        return {
            "entry": len(visitors),
            "zone_visit": len(zone_visitors),
            "billing_queue": len(billing_visitors),
            "purchase": len(purchase_visitors)
        }
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "DATABASE_UNAVAILABLE"
            }
        )
@app.get("/stores/{store_id}/heatmap")
def get_heatmap(
    store_id: str,
    db: Session = Depends(get_db)
):
    try:
        events = db.query(EventModel).filter(
            EventModel.store_id == store_id,
            EventModel.is_staff == False
        ).all()

        zone_stats = {}

        for event in events:

            if not event.zone_id:
                continue

            if event.zone_id not in zone_stats:

                zone_stats[event.zone_id] = {
                    "visits": 0,
                    "total_dwell": 0,
                    "dwell_count": 0
                }

            if event.event_type == "ZONE_ENTER":
                zone_stats[event.zone_id]["visits"] += 1

            if event.event_type == "ZONE_DWELL":

                zone_stats[event.zone_id]["total_dwell"] += event.dwell_ms

                zone_stats[event.zone_id]["dwell_count"] += 1

        max_visits = max(
            [z["visits"] for z in zone_stats.values()],
            default=1
        )

        heatmap = []

        for zone, stats in zone_stats.items():

            avg_dwell = 0

            if stats["dwell_count"] > 0:

                avg_dwell = (
                    stats["total_dwell"]
                    /
                    stats["dwell_count"]
                )

            score = int(
                (stats["visits"] / max_visits) * 100
            )

            heatmap.append({
                "zone": zone,
                "visits": stats["visits"],
                "avg_dwell_ms": round(avg_dwell, 2),
                "score": score
            })

        sessions = len(
            set(
                e.visitor_id
                for e in events
            )
        )

        return {
            "data_confidence":
                "LOW"
                if sessions < 20
                else "HIGH",
            "zones": heatmap
        }
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "DATABASE_UNAVAILABLE"
            }
        )
    
@app.get("/stores/{store_id}/anomalies")
def get_anomalies(
    store_id: str,
    db: Session = Depends(get_db)
):
    try:
        events = db.query(EventModel).filter(
            EventModel.store_id == store_id
        ).all()

        anomalies = []

        queue_events = [
            e for e in events
            if e.event_type == "BILLING_QUEUE_JOIN"
        ]

        if len(queue_events) > 10:

            anomalies.append({
                "severity": "WARN",
                "type": "QUEUE_SPIKE",
                "suggested_action":
                    "Open additional checkout counters"
            })

        zone_visits = {}

        for event in events:

            if event.event_type == "ZONE_ENTER":

                zone_visits[event.zone_id] = (
                    zone_visits.get(
                        event.zone_id,
                        0
                    ) + 1
                )

        for zone, visits in zone_visits.items():

            if visits == 0:

                anomalies.append({
                    "severity": "INFO",
                    "type": "DEAD_ZONE",
                    "zone": zone,
                    "suggested_action":
                        "Review product placement"
                })

        if not anomalies:

            anomalies.append({
                "severity": "INFO",
                "type": "NO_ACTIVE_ANOMALIES",
                "suggested_action":
                    "Store operating normally"
            })

        return anomalies
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "DATABASE_UNAVAILABLE"
            }
        )