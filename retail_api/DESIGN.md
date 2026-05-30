# Retail Analytics Platform Design

## Overview

The solution consists of two major components:

1. Computer Vision Pipeline
2. Analytics API

The Computer Vision Pipeline processes CCTV footage using YOLOv8 for person detection and ByteTrack for multi-object tracking. Detected visitor activities are converted into structured retail events such as ZONE_ENTER, ZONE_EXIT and ZONE_DWELL.

The Analytics API ingests these events through FastAPI endpoints and stores them in SQLite. The API computes visitor metrics, conversion funnels, heatmaps and operational anomalies.

## System Architecture

CCTV Footage

↓

YOLOv8 Detection

↓

ByteTrack Tracking

↓

Event Generator

↓

FastAPI

↓

SQLite

↓

Analytics Endpoints

## AI-Assisted Decisions

### Decision 1: Detection Model Selection

AI suggested several models including YOLOv8, RT-DETR and YOLOv9.

I selected YOLOv8 because it provided the best balance of speed, documentation and ease of deployment on a local machine.

### Decision 2: Tracking Framework

AI suggested ByteTrack, DeepSORT and StrongSORT.

I selected ByteTrack because it performs well for crowded scenes while requiring minimal configuration.

### Decision 3: Analytics API Design

AI suggested PostgreSQL and Redis for production-scale deployments.

For this assignment I overrode the recommendation and selected SQLite because it reduced setup complexity while still satisfying the assignment requirements.