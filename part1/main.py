import cv2
import time
import json

from tracker import PersonTracker
from zone_manager import ZoneManager
from event_generator import create_event

from config import *

ENTRY_LINE_Y = 300

tracker = PersonTracker()

zone_manager = ZoneManager("store_layout.json")

# Open all video streams
caps = {}

for camera_id, video_path in VIDEO_PATHS.items():

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Could not open {video_path}")
        continue

    caps[camera_id] = cap

track_history = {}
session_counter = {}

ENTRY_LINE_Y = 300

while True:

    active_cameras = 0

    for camera_id, cap in caps.items():

        ret, frame = cap.read()

        if not ret:
            continue

        active_cameras += 1

        results = tracker.track(frame)

        if results.boxes.id is None:
            continue

        boxes = results.boxes.xyxy.cpu().numpy()
        ids = results.boxes.id.cpu().numpy()
        confs = results.boxes.conf.cpu().numpy()

        for box, track_id, conf in zip(
                boxes,
                ids,
                confs):

            x1, y1, x2, y2 = box

            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            zone = zone_manager.get_zone(cx, cy)

            # Prevent collisions across cameras
            visitor_id = f"{camera_id}_VIS_{int(track_id)}"

            if visitor_id not in session_counter:
                session_counter[visitor_id] = 1

            if visitor_id not in track_history:

                track_history[visitor_id] = {
                    "zone": None,
                    "enter_time": time.time(),
                    "last_y": cy,
                    "entered_store": False
                }

            current_zone = (
                zone["zone_id"]
                if zone else None
            )

            previous_zone = track_history[
                visitor_id
            ]["zone"]

            last_y = track_history[visitor_id].get("last_y", cy)

            if not track_history[visitor_id]["entered_store"]:

                if last_y < ENTRY_LINE_Y and cy >= ENTRY_LINE_Y:

                    event = create_event(
                        store_id=zone_manager.store_id,
                        camera_id=camera_id,
                        visitor_id=visitor_id,
                        event_type="ENTRY",
                        zone_id=None,
                        dwell_ms=0,
                        confidence=float(conf),
                        session_seq=session_counter[visitor_id],
                        sku_zone=None
                    )

                    session_counter[visitor_id] += 1
                    track_history[visitor_id]["entered_store"] = True
                    print(json.dumps(event, indent=2))

            elif last_y >= ENTRY_LINE_Y and cy < ENTRY_LINE_Y:

                event = create_event(
                    store_id=zone_manager.store_id,
                    camera_id=camera_id,
                    visitor_id=visitor_id,
                    event_type="EXIT",
                    zone_id=None,
                    dwell_ms=0,
                    confidence=float(conf),
                    session_seq=session_counter[visitor_id],
                    sku_zone=None
                )

                session_counter[visitor_id] += 1
                print(json.dumps(event, indent=2))

            track_history[visitor_id]["last_y"] = cy

            if previous_zone and previous_zone != current_zone:

                event = create_event(
                    store_id=zone_manager.store_id,
                    camera_id=camera_id,
                    visitor_id=visitor_id,
                    event_type="ZONE_EXIT",
                    zone_id=previous_zone,
                    dwell_ms=0,
                    confidence=float(conf),
                    session_seq=session_counter[visitor_id],
                    sku_zone=None
                )

                session_counter[visitor_id] += 1
                print(json.dumps(event, indent=2))

            # -------------------------
            # ZONE ENTER EVENT
            # -------------------------

            if current_zone != previous_zone:

                track_history[
                    visitor_id
                ]["zone"] = current_zone

                track_history[
                    visitor_id
                ]["enter_time"] = time.time()

                if current_zone:

                    event = create_event(
                        store_id=zone_manager.store_id,
                        camera_id=camera_id,
                        visitor_id=visitor_id,
                        event_type="ZONE_ENTER",
                        zone_id=current_zone,
                        dwell_ms=0,
                        confidence=float(conf),
                        session_seq=session_counter[
                            visitor_id
                        ],
                        sku_zone=zone["sku_zone"]
                    )

                    session_counter[
                        visitor_id
                    ] += 1

                    print(
                        json.dumps(
                            event,
                            indent=2
                        )
                    )

            # -------------------------
            # ZONE DWELL EVENT
            # -------------------------

            if current_zone:

                dwell = (
                    time.time()
                    -
                    track_history[
                        visitor_id
                    ]["enter_time"]
                )

                if dwell > DWELL_THRESHOLD_SEC:

                    event = create_event(
                        store_id=zone_manager.store_id,
                        camera_id=camera_id,
                        visitor_id=visitor_id,
                        event_type="ZONE_DWELL",
                        zone_id=current_zone,
                        dwell_ms=int(
                            dwell * 1000
                        ),
                        confidence=float(conf),
                        session_seq=session_counter[
                            visitor_id
                        ],
                        sku_zone=zone["sku_zone"]
                    )

                    session_counter[
                        visitor_id
                    ] += 1

                    print(
                        json.dumps(
                            event,
                            indent=2
                        )
                    )

                    track_history[
                        visitor_id
                    ]["enter_time"] = time.time()

            # -------------------------
            # DRAW DETECTIONS
            # -------------------------

            cv2.rectangle(
                frame,
                (int(x1), int(y1)),
                (int(x2), int(y2)),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                visitor_id,
                (int(x1), int(y1) - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        if SHOW_VIDEO:

            cv2.imshow(
                camera_id,
                frame
            )

    # Stop when all videos end
    if active_cameras == 0:
        break

    if cv2.waitKey(1) & 0xFF == 27:
        break

for cap in caps.values():
    cap.release()

cv2.destroyAllWindows()