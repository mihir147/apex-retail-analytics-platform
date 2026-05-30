# config.py

# Video files
VIDEO_PATHS = {
    "CAM_1": "part1/CCTV Footage/CAM 1.mp4",
    "CAM_2": "part1/CCTV Footage/CAM 2.mp4",
    "CAM_3": "part1/CCTV Footage/CAM 3.mp4",
    "CAM_4": "part1/CCTV Footage/CAM 4.mp4",
    "CAM_5": "part1/CCTV Footage/CAM 5.mp4"
}

# Store information
STORE_ID = "STORE_BLR_002"

# Video settings
FPS = 30

# Generate ZONE_DWELL event after visitor stays in a zone
DWELL_THRESHOLD_SEC = 30

# Detection settings
CONFIDENCE_THRESHOLD = 0.25

# Queue settings
QUEUE_ZONE_ID = "BILLING"

# Re-ID settings (future enhancement)
REID_SIMILARITY_THRESHOLD = 0.7

# Display settings
SHOW_VIDEO = True

# Output file
EVENT_LOG_FILE = "retail_events.json"