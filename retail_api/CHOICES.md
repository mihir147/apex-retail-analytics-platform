# Technical Choices

## 1. Detection Model Choice

### Options Considered

- YOLOv8
- YOLOv9
- RT-DETR

### AI Suggestion

The AI assistant recommended YOLOv8 or RT-DETR depending on speed requirements.

### Final Choice

YOLOv8

### Why

YOLOv8 provides:

- Strong person detection accuracy
- Real-time performance
- Easy integration with Python
- Extensive documentation

For this assignment YOLOv8 offered the best balance of implementation effort and performance.

---

## 2. Event Schema Design

### Options Considered

- Raw detection logs
- Session-based visitor events
- Aggregated analytics only

### AI Suggestion

AI recommended using structured event-driven architecture.

### Final Choice

Structured visitor events.

### Why

The event schema allows:

- Replayability
- Auditing
- Analytics independence
- Real-time processing

This approach mirrors production event-driven systems.

---

## 3. API Architecture Choice

### Options Considered

- Flask
- FastAPI
- Django

### AI Suggestion

AI recommended FastAPI because of automatic validation and OpenAPI support.

### Final Choice

FastAPI

### Why

FastAPI provides:

- Automatic Swagger documentation
- Pydantic validation
- Strong typing
- Easy testing

which made it well suited for this assignment.

---

## VLM Usage

No Vision Language Model was used in the final implementation.

The design considered VLM-assisted zone classification and staff detection. However, deterministic zone definitions from store_layout.json provided more reliable results for the supplied dataset.