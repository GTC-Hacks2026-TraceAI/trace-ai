"""Mock camera network and deterministic frame search for demo purposes."""

from __future__ import annotations

import hashlib
import random
from datetime import datetime, timezone

from app.models import Camera, Sighting

CAMERAS: list[Camera] = [
    Camera(id="cam-001", name="Main Entrance", location="Building A - Front Gate", zone="north", neighbors=["cam-002", "cam-003"], retention_hours=72.0),
    Camera(id="cam-002", name="Parking Lot A", location="Building A - West Lot", zone="north", neighbors=["cam-001", "cam-004"], retention_hours=48.0),
    Camera(id="cam-003", name="Hallway B1", location="Building B - 1st Floor", zone="central", neighbors=["cam-001", "cam-005", "cam-006"], retention_hours=24.0),
    Camera(id="cam-004", name="Cafeteria", location="Building A - Ground Floor", zone="north", neighbors=["cam-002", "cam-005"], retention_hours=24.0),
    Camera(id="cam-005", name="Library Entrance", location="Building C - Main Door", zone="central", neighbors=["cam-003", "cam-004", "cam-007"], retention_hours=48.0),
    Camera(id="cam-006", name="South Exit", location="Building B - Rear Door", zone="south", neighbors=["cam-003", "cam-007"], retention_hours=72.0),
    Camera(id="cam-007", name="East Quad Walkway", location="East Quad - Central Walkway", zone="east", neighbors=["cam-006", "cam-008", "cam-009"]),
    Camera(id="cam-008", name="Science Hall Lobby", location="Langford Science Hall - Main Lobby", zone="east", neighbors=["cam-007", "cam-009"]),
    Camera(id="cam-009", name="South Plaza", location="South Campus Plaza - Fountain Area", zone="south", neighbors=["cam-005", "cam-006", "cam-010"], retention_hours=12.0),
    Camera(id="cam-010", name="Transit Stop", location="Bus Stop - University Ave", zone="south", neighbors=["cam-006", "cam-009"], retention_hours=12.0),
]

CAMERA_MAP: dict[str, Camera] = {c.id: c for c in CAMERAS}

# Simulated indexed frames extracted from camera footage.
# Timestamps span 08:00-08:44 UTC (44-minute window) on 2026-03-15.
# Candidate frames (strong match for red hoodie + black backpack):
#   frame-002, frame-007, frame-014, frame-022, frame-029, frame-034, frame-039
# Distractor / partial-match frames:
#   frame-003 (red jacket, no backpack)
#   frame-009 (red jacket, no backpack)
#   frame-012 (dark hoodie, black backpack - no red)
#   frame-018 (black backpack, white shirt - no red)
#   frame-024 (red scarf, no backpack)
#   frame-032 (orange hoodie, black backpack - wrong colour)
SAMPLE_FRAMES: list[dict] = [
    # frame-001
    {
        "frame_id": "frame-001", "camera_id": "cam-001",
        "timestamp": datetime(2026, 3, 15, 8, 0, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-day",
            "clothing_colors": ["navy", "white"],
            "accessories": ["bag"],
            "shoes": "white sneakers",
            "direction": "inbound", "zone": "north",
            "text_tags": ["navy jacket", "white shirt", "white sneakers", "messenger bag"],
            "face_match_score": None,
        },
    },
    # frame-002 - CANDIDATE (red hoodie + black backpack)
    {
        "frame_id": "frame-002", "camera_id": "cam-001",
        "timestamp": datetime(2026, 3, 15, 8, 2, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-day",
            "clothing_colors": ["red", "black", "blue"],
            "accessories": ["backpack"],
            "shoes": "white sneakers",
            "direction": "inbound", "zone": "north",
            "text_tags": ["red hoodie", "black backpack", "dark blue jeans", "white sneakers"],
            "face_match_score": 0.78,
        },
    },
    # frame-003 - DISTRACTOR (red jacket, no backpack)
    {
        "frame_id": "frame-003", "camera_id": "cam-002",
        "timestamp": datetime(2026, 3, 15, 8, 4, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-parking",
            "clothing_colors": ["red", "gray"],
            "accessories": ["sunglasses"],
            "shoes": "brown boots",
            "direction": "inbound", "zone": "north",
            "text_tags": ["red jacket", "gray pants", "brown boots", "sunglasses"],
            "face_match_score": None,
        },
    },
    # frame-004
    {
        "frame_id": "frame-004", "camera_id": "cam-001",
        "timestamp": datetime(2026, 3, 15, 8, 7, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-day",
            "clothing_colors": ["black", "white"],
            "accessories": ["cap"],
            "shoes": "black sneakers",
            "direction": "inbound", "zone": "north",
            "text_tags": ["black hoodie", "white t-shirt", "black sneakers", "black cap"],
            "face_match_score": None,
        },
    },
    # frame-005
    {
        "frame_id": "frame-005", "camera_id": "cam-003",
        "timestamp": datetime(2026, 3, 15, 8, 8, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "720p", "fps": 25, "scene": "exterior-transit",
            "clothing_colors": ["green", "khaki"],
            "accessories": ["backpack", "hat"],
            "shoes": "hiking boots",
            "direction": "outbound", "zone": "north",
            "text_tags": ["green parka", "khaki pants", "hiking boots", "gray backpack", "beanie hat"],
            "face_match_score": None,
        },
    },
    # frame-006
    {
        "frame_id": "frame-006", "camera_id": "cam-003",
        "timestamp": datetime(2026, 3, 15, 8, 9, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "720p", "fps": 25, "scene": "exterior-transit",
            "clothing_colors": ["blue", "white"],
            "accessories": [],
            "shoes": "loafers",
            "direction": "inbound", "zone": "north",
            "text_tags": ["blue polo shirt", "white slacks", "loafers"],
            "face_match_score": None,
        },
    },
    # frame-007 - CANDIDATE (red hoodie + black backpack)
    {
        "frame_id": "frame-007", "camera_id": "cam-004",
        "timestamp": datetime(2026, 3, 15, 8, 9, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "interior-lobby",
            "clothing_colors": ["red", "black", "blue"],
            "accessories": ["backpack"],
            "shoes": "white sneakers",
            "direction": "inbound", "zone": "central",
            "text_tags": ["red hoodie", "black backpack", "dark blue jeans", "white sneakers"],
            "face_match_score": 0.82,
        },
    },
    # frame-008
    {
        "frame_id": "frame-008", "camera_id": "cam-004",
        "timestamp": datetime(2026, 3, 15, 8, 11, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "interior-lobby",
            "clothing_colors": ["purple", "black"],
            "accessories": ["glasses"],
            "shoes": "black flats",
            "direction": "inbound", "zone": "central",
            "text_tags": ["purple sweater", "black jeans", "black flats", "glasses"],
            "face_match_score": None,
        },
    },
    # frame-009 - DISTRACTOR (red jacket, no backpack)
    {
        "frame_id": "frame-009", "camera_id": "cam-002",
        "timestamp": datetime(2026, 3, 15, 8, 11, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-parking",
            "clothing_colors": ["red", "black"],
            "accessories": [],
            "shoes": "running shoes",
            "direction": "inbound", "zone": "north",
            "text_tags": ["red jacket", "black leggings", "running shoes"],
            "face_match_score": None,
        },
    },
    # frame-010
    {
        "frame_id": "frame-010", "camera_id": "cam-004",
        "timestamp": datetime(2026, 3, 15, 8, 14, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "interior-lobby",
            "clothing_colors": ["orange", "gray"],
            "accessories": ["backpack"],
            "shoes": "white sneakers",
            "direction": "inbound", "zone": "central",
            "text_tags": ["orange t-shirt", "gray joggers", "white sneakers", "gray backpack"],
            "face_match_score": None,
        },
    },
    # frame-011
    {
        "frame_id": "frame-011", "camera_id": "cam-006",
        "timestamp": datetime(2026, 3, 15, 8, 14, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "720p", "fps": 25, "scene": "exterior-entrance",
            "clothing_colors": ["beige", "brown"],
            "accessories": ["bag", "scarf"],
            "shoes": "ankle boots",
            "direction": "inbound", "zone": "central",
            "text_tags": ["beige coat", "brown scarf", "ankle boots", "leather bag"],
            "face_match_score": None,
        },
    },
    # frame-012 - DISTRACTOR (dark hoodie + black backpack, no red)
    {
        "frame_id": "frame-012", "camera_id": "cam-005",
        "timestamp": datetime(2026, 3, 15, 8, 15, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "interior-cafeteria",
            "clothing_colors": ["black", "gray"],
            "accessories": ["backpack"],
            "shoes": "black sneakers",
            "direction": "inbound", "zone": "central",
            "text_tags": ["dark hoodie", "black backpack", "gray jeans", "black sneakers"],
            "face_match_score": 0.45,
        },
    },
    # frame-013
    {
        "frame_id": "frame-013", "camera_id": "cam-001",
        "timestamp": datetime(2026, 3, 15, 8, 15, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-day",
            "clothing_colors": ["yellow", "blue"],
            "accessories": ["cap"],
            "shoes": "white sneakers",
            "direction": "outbound", "zone": "north",
            "text_tags": ["yellow rain jacket", "blue jeans", "white sneakers", "cap"],
            "face_match_score": None,
        },
    },
    # frame-014 - CANDIDATE (red hoodie + black backpack)
    {
        "frame_id": "frame-014", "camera_id": "cam-006",
        "timestamp": datetime(2026, 3, 15, 8, 16, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "720p", "fps": 25, "scene": "exterior-entrance",
            "clothing_colors": ["red", "black", "blue"],
            "accessories": ["backpack"],
            "shoes": "white sneakers",
            "direction": "inbound", "zone": "central",
            "text_tags": ["red hoodie", "black backpack", "dark blue jeans", "white sneakers"],
            "face_match_score": 0.75,
        },
    },
    # frame-015
    {
        "frame_id": "frame-015", "camera_id": "cam-006",
        "timestamp": datetime(2026, 3, 15, 8, 17, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "720p", "fps": 25, "scene": "exterior-entrance",
            "clothing_colors": ["white", "navy"],
            "accessories": ["purse"],
            "shoes": "heels",
            "direction": "inbound", "zone": "central",
            "text_tags": ["white blouse", "navy skirt", "heels", "purse"],
            "face_match_score": None,
        },
    },
    # frame-016
    {
        "frame_id": "frame-016", "camera_id": "cam-005",
        "timestamp": datetime(2026, 3, 15, 8, 18, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "interior-cafeteria",
            "clothing_colors": ["gray", "blue"],
            "accessories": ["glasses"],
            "shoes": "blue sneakers",
            "direction": "inbound", "zone": "central",
            "text_tags": ["gray crewneck", "blue jeans", "blue sneakers", "glasses"],
            "face_match_score": None,
        },
    },
    # frame-017
    {
        "frame_id": "frame-017", "camera_id": "cam-004",
        "timestamp": datetime(2026, 3, 15, 8, 18, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "interior-lobby",
            "clothing_colors": ["maroon", "gray"],
            "accessories": ["backpack", "cap"],
            "shoes": "gray sneakers",
            "direction": "outbound", "zone": "central",
            "text_tags": ["maroon hoodie", "gray joggers", "gray sneakers", "gray backpack", "cap"],
            "face_match_score": None,
        },
    },
    # frame-018 - DISTRACTOR (black backpack + white shirt, no red)
    {
        "frame_id": "frame-018", "camera_id": "cam-006",
        "timestamp": datetime(2026, 3, 15, 8, 20, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "720p", "fps": 25, "scene": "exterior-entrance",
            "clothing_colors": ["white", "black"],
            "accessories": ["backpack"],
            "shoes": "white sneakers",
            "direction": "outbound", "zone": "central",
            "text_tags": ["white t-shirt", "black backpack", "black jeans", "white sneakers"],
            "face_match_score": None,
        },
    },
    # frame-019
    {
        "frame_id": "frame-019", "camera_id": "cam-007",
        "timestamp": datetime(2026, 3, 15, 8, 21, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-walkway",
            "clothing_colors": ["blue", "gray"],
            "accessories": ["backpack"],
            "shoes": "gray sneakers",
            "direction": "inbound", "zone": "east",
            "text_tags": ["blue denim jacket", "gray hoodie", "gray jeans", "gray sneakers", "gray backpack"],
            "face_match_score": None,
        },
    },
    # frame-020
    {
        "frame_id": "frame-020", "camera_id": "cam-005",
        "timestamp": datetime(2026, 3, 15, 8, 22, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "interior-cafeteria",
            "clothing_colors": ["pink", "white"],
            "accessories": ["bag"],
            "shoes": "sandals",
            "direction": "outbound", "zone": "central",
            "text_tags": ["pink hoodie", "white shorts", "sandals", "tote bag"],
            "face_match_score": None,
        },
    },
    # frame-021
    {
        "frame_id": "frame-021", "camera_id": "cam-007",
        "timestamp": datetime(2026, 3, 15, 8, 23, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-walkway",
            "clothing_colors": ["black", "white"],
            "accessories": ["sunglasses"],
            "shoes": "white sneakers",
            "direction": "outbound", "zone": "east",
            "text_tags": ["black coat", "white shirt", "white sneakers", "sunglasses"],
            "face_match_score": None,
        },
    },
    # frame-022 - CANDIDATE (red hoodie + black backpack)
    {
        "frame_id": "frame-022", "camera_id": "cam-007",
        "timestamp": datetime(2026, 3, 15, 8, 24, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-walkway",
            "clothing_colors": ["red", "black", "blue"],
            "accessories": ["backpack"],
            "shoes": "white sneakers",
            "direction": "inbound", "zone": "east",
            "text_tags": ["red hoodie", "black backpack", "dark blue jeans", "white sneakers"],
            "face_match_score": 0.79,
        },
    },
    # frame-023
    {
        "frame_id": "frame-023", "camera_id": "cam-002",
        "timestamp": datetime(2026, 3, 15, 8, 26, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-parking",
            "clothing_colors": ["black", "blue"],
            "accessories": ["glasses"],
            "shoes": "dress shoes",
            "direction": "inbound", "zone": "north",
            "text_tags": ["black blazer", "blue dress shirt", "dress shoes", "glasses"],
            "face_match_score": None,
        },
    },
    # frame-024 - DISTRACTOR (red scarf, no backpack)
    {
        "frame_id": "frame-024", "camera_id": "cam-007",
        "timestamp": datetime(2026, 3, 15, 8, 27, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-walkway",
            "clothing_colors": ["red", "gray"],
            "accessories": ["bag"],
            "shoes": "red sneakers",
            "direction": "outbound", "zone": "east",
            "text_tags": ["red scarf", "gray jacket", "gray jeans", "red sneakers", "tote bag"],
            "face_match_score": None,
        },
    },
    # frame-025
    {
        "frame_id": "frame-025", "camera_id": "cam-004",
        "timestamp": datetime(2026, 3, 15, 8, 28, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "interior-lobby",
            "clothing_colors": ["green", "black"],
            "accessories": ["backpack"],
            "shoes": "black boots",
            "direction": "outbound", "zone": "central",
            "text_tags": ["green vest", "black long-sleeve shirt", "black boots", "black backpack"],
            "face_match_score": None,
        },
    },
    # frame-026
    {
        "frame_id": "frame-026", "camera_id": "cam-008",
        "timestamp": datetime(2026, 3, 15, 8, 29, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "720p", "fps": 25, "scene": "interior-lobby",
            "clothing_colors": ["brown", "khaki"],
            "accessories": ["glasses", "hat"],
            "shoes": "loafers",
            "direction": "inbound", "zone": "east",
            "text_tags": ["brown cardigan", "khaki pants", "loafers", "glasses", "flat cap"],
            "face_match_score": None,
        },
    },
    # frame-027
    {
        "frame_id": "frame-027", "camera_id": "cam-005",
        "timestamp": datetime(2026, 3, 15, 8, 30, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "interior-cafeteria",
            "clothing_colors": ["gray", "blue"],
            "accessories": ["backpack"],
            "shoes": "running shoes",
            "direction": "outbound", "zone": "central",
            "text_tags": ["gray sweatshirt", "blue jeans", "running shoes", "blue backpack"],
            "face_match_score": None,
        },
    },
    # frame-028
    {
        "frame_id": "frame-028", "camera_id": "cam-009",
        "timestamp": datetime(2026, 3, 15, 8, 30, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-plaza",
            "clothing_colors": ["black", "white"],
            "accessories": ["cap", "backpack"],
            "shoes": "white sneakers",
            "direction": "outbound", "zone": "south",
            "text_tags": ["black hoodie", "white joggers", "white sneakers", "black cap", "black backpack"],
            "face_match_score": None,
        },
    },
    # frame-029 - CANDIDATE (red hoodie + black backpack)
    {
        "frame_id": "frame-029", "camera_id": "cam-008",
        "timestamp": datetime(2026, 3, 15, 8, 31, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "720p", "fps": 25, "scene": "interior-lobby",
            "clothing_colors": ["red", "black", "blue"],
            "accessories": ["backpack"],
            "shoes": "white sneakers",
            "direction": "inbound", "zone": "east",
            "text_tags": ["red hoodie", "black backpack", "dark blue jeans", "white sneakers"],
            "face_match_score": 0.71,
        },
    },
    # frame-030
    {
        "frame_id": "frame-030", "camera_id": "cam-007",
        "timestamp": datetime(2026, 3, 15, 8, 33, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-walkway",
            "clothing_colors": ["navy", "white"],
            "accessories": ["glasses", "bag"],
            "shoes": "oxford shoes",
            "direction": "inbound", "zone": "east",
            "text_tags": ["navy blazer", "white button-down", "oxford shoes", "leather bag", "glasses"],
            "face_match_score": None,
        },
    },
    # frame-031
    {
        "frame_id": "frame-031", "camera_id": "cam-009",
        "timestamp": datetime(2026, 3, 15, 8, 33, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-plaza",
            "clothing_colors": ["yellow", "blue"],
            "accessories": [],
            "shoes": "sandals",
            "direction": "inbound", "zone": "south",
            "text_tags": ["yellow sundress", "blue cardigan", "sandals"],
            "face_match_score": None,
        },
    },
    # frame-032 - DISTRACTOR (orange hoodie + black backpack, wrong colour)
    {
        "frame_id": "frame-032", "camera_id": "cam-006",
        "timestamp": datetime(2026, 3, 15, 8, 35, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "720p", "fps": 25, "scene": "exterior-entrance",
            "clothing_colors": ["orange", "black"],
            "accessories": ["backpack"],
            "shoes": "black sneakers",
            "direction": "outbound", "zone": "central",
            "text_tags": ["orange hoodie", "black backpack", "black jeans", "black sneakers"],
            "face_match_score": 0.42,
        },
    },
    # frame-033
    {
        "frame_id": "frame-033", "camera_id": "cam-008",
        "timestamp": datetime(2026, 3, 15, 8, 37, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "720p", "fps": 25, "scene": "interior-lobby",
            "clothing_colors": ["blue", "gray"],
            "accessories": ["cap"],
            "shoes": "sneakers",
            "direction": "outbound", "zone": "east",
            "text_tags": ["blue hoodie", "gray sweatpants", "sneakers", "blue cap"],
            "face_match_score": None,
        },
    },
    # frame-034 - CANDIDATE (red hoodie + black backpack)
    {
        "frame_id": "frame-034", "camera_id": "cam-009",
        "timestamp": datetime(2026, 3, 15, 8, 37, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-plaza",
            "clothing_colors": ["red", "black", "blue"],
            "accessories": ["backpack"],
            "shoes": "white sneakers",
            "direction": "outbound", "zone": "south",
            "text_tags": ["red hoodie", "black backpack", "dark blue jeans", "white sneakers"],
            "face_match_score": 0.68,
        },
    },
    # frame-035
    {
        "frame_id": "frame-035", "camera_id": "cam-003",
        "timestamp": datetime(2026, 3, 15, 8, 38, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "720p", "fps": 25, "scene": "exterior-transit",
            "clothing_colors": ["black", "white"],
            "accessories": ["backpack"],
            "shoes": "sneakers",
            "direction": "outbound", "zone": "north",
            "text_tags": ["black puffer jacket", "white jeans", "sneakers", "black backpack"],
            "face_match_score": None,
        },
    },
    # frame-036
    {
        "frame_id": "frame-036", "camera_id": "cam-010",
        "timestamp": datetime(2026, 3, 15, 8, 39, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-transit",
            "clothing_colors": ["tan", "brown"],
            "accessories": ["bag"],
            "shoes": "loafers",
            "direction": "outbound", "zone": "south",
            "text_tags": ["tan trench coat", "brown pants", "loafers", "leather bag"],
            "face_match_score": None,
        },
    },
    # frame-037
    {
        "frame_id": "frame-037", "camera_id": "cam-009",
        "timestamp": datetime(2026, 3, 15, 8, 40, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-plaza",
            "clothing_colors": ["gray", "pink"],
            "accessories": ["purse"],
            "shoes": "ballet flats",
            "direction": "inbound", "zone": "south",
            "text_tags": ["gray peacoat", "pink scarf", "ballet flats", "black purse"],
            "face_match_score": None,
        },
    },
    # frame-038
    {
        "frame_id": "frame-038", "camera_id": "cam-010",
        "timestamp": datetime(2026, 3, 15, 8, 40, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-transit",
            "clothing_colors": ["black", "navy"],
            "accessories": ["backpack", "cap"],
            "shoes": "work boots",
            "direction": "outbound", "zone": "south",
            "text_tags": ["black jacket", "navy work pants", "work boots", "gray backpack", "cap"],
            "face_match_score": None,
        },
    },
    # frame-039 - CANDIDATE (red hoodie + black backpack)
    {
        "frame_id": "frame-039", "camera_id": "cam-010",
        "timestamp": datetime(2026, 3, 15, 8, 42, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-transit",
            "clothing_colors": ["red", "black", "blue"],
            "accessories": ["backpack"],
            "shoes": "white sneakers",
            "direction": "outbound", "zone": "south",
            "text_tags": ["red hoodie", "black backpack", "dark blue jeans", "white sneakers"],
            "face_match_score": 0.74,
        },
    },
    # frame-040
    {
        "frame_id": "frame-040", "camera_id": "cam-010",
        "timestamp": datetime(2026, 3, 15, 8, 44, 0, tzinfo=timezone.utc).isoformat(),
        "metadata": {
            "resolution": "1080p", "fps": 30, "scene": "exterior-transit",
            "clothing_colors": ["white", "black"],
            "accessories": ["umbrella"],
            "shoes": "black sneakers",
            "direction": "inbound", "zone": "south",
            "text_tags": ["white windbreaker", "black joggers", "black sneakers", "umbrella"],
            "face_match_score": None,
        },
    },
]


def mock_search(
    case_id: str,
    description: str | None,
    clothing: str | None,
) -> list[Sighting]:
    """Deterministic mock search against indexed frame metadata.

    Returns sightings ranked by similarity score (descending).
    Seeded on case_id so repeated calls return identical results.
    """
    seed = int(hashlib.md5(case_id.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    n_matches = rng.randint(3, min(6, len(SAMPLE_FRAMES)))
    frames = rng.sample(SAMPLE_FRAMES, n_matches)

    sightings: list[Sighting] = []
    for frame in frames:
        score = rng.uniform(0.55, 0.97)
        if description:
            score = min(1.0, score + 0.03)
        if clothing:
            score = min(1.0, score + 0.02)
        score = round(score, 3)

        camera = CAMERA_MAP.get(frame["camera_id"])
        location = camera.location if camera else "Unknown"

        parts = [f"Visual similarity {score:.0%}"]
        if clothing:
            parts.append(f"clothing match ({clothing[:30]})")
        parts.append("temporal proximity to last known sighting")

        sightings.append(Sighting(
            case_id=case_id,
            camera_id=frame["camera_id"],
            frame_id=frame["frame_id"],
            timestamp=datetime.fromisoformat(frame["timestamp"]),
            location=location,
            similarity_score=score,
            explanation="; ".join(parts),
        ))

    sightings.sort(key=lambda s: s.similarity_score, reverse=True)
    return sightings
