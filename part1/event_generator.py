import uuid
from datetime import datetime


def create_event(
    store_id,
    camera_id,
    visitor_id,
    event_type,
    zone_id,
    dwell_ms,
    confidence,
    session_seq,
    sku_zone,
    queue_depth=None
):

    event = {

        "event_id": str(uuid.uuid4()),

        "store_id": store_id,

        "camera_id": camera_id,

        "visitor_id": visitor_id,

        "event_type": event_type,

        "timestamp": datetime.utcnow().isoformat() + "Z",

        "zone_id": zone_id,

        "dwell_ms": dwell_ms,

        "is_staff": False,

        "confidence": float(confidence),

        "metadata": {

            "queue_depth": queue_depth,

            "sku_zone": sku_zone,

            "session_seq": session_seq
        }
    }

    return event