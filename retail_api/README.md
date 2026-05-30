# Apex Retail Analytics

## Setup

```bash
conda activate retailapi

pip install -r requirements.txt

uvicorn main:app --reload
```

## Open API

Open:

http://127.0.0.1:8000/docs

## Run Detection Pipeline

Go to Part 1 folder:

```bash
cd purple

python main.py
```

This generates retail events from CCTV videos.

## Available APIs

POST /events/ingest

GET /health

GET /stores/{store_id}/metrics

GET /stores/{store_id}/funnel

GET /stores/{store_id}/heatmap

GET /stores/{store_id}/anomalies

## Run Tests

```bash
pytest
```