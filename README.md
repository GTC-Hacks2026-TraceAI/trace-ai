# Trace AI

> Human-in-the-loop missing-person investigation backend — built with **FastAPI**.

---

## Project description

Trace AI is a backend service that helps investigators locate missing persons
faster by automatically scanning a network of indexed security cameras.
Given a case (subject name, last known location, clothing description), the
system scores every available camera frame using a configurable matching
pipeline, ranks the results by confidence, and stitches confirmed sightings
into a chronological movement timeline.  It then uses the camera graph to
recommend which cameras the investigator should pull footage from next —
so every hour of manual review is spent on the highest-probability leads.

---

## Problem statement

When a person goes missing, investigators must manually review hours of
security-camera footage across dozens of cameras.  The process is slow,
prone to missed sightings, and does not scale to large camera networks.
Trace AI automates the initial triage: it scores every indexed frame,
surfaces the top matches for human review, and continuously narrows the
search corridor based on confirmed sightings.

---

## Why this matters for missing-person investigations

| Pain point | How Trace AI addresses it |
|---|---|
| Hours of manual footage review | Automated scoring narrows hundreds of frames to a ranked shortlist in milliseconds |
| Missed sightings due to fatigue | Confidence-weighted matching catches low-salience appearances that humans overlook |
| No sense of movement direction | Timeline service orders confirmed sightings chronologically and generates a plain-English path summary |
| Unclear which camera to check next | Camera-recommendation service traverses the camera graph and surfaces neighbour cameras ordered by priority |
| Footage overwritten before review | Urgency levels and `review_before` timestamps alert investigators before retention windows expire |

---

## Architecture overview

```
┌───────────────────────────────────────────────────────────┐
│                         HTTP clients                       │
└───────────────────────────┬───────────────────────────────┘
                            │ REST / JSON
┌───────────────────────────▼───────────────────────────────┐
│                    FastAPI  (app/main.py)                   │
│  ┌────────────────────────────────────────────────────┐   │
│  │                  app/routes.py                      │   │
│  │  /cases  /search  /timeline  /recommendations       │   │
│  └──────┬──────────────┬──────────────────────────────┘   │
│         │              │                                    │
│  ┌──────▼──────┐ ┌─────▼──────────────────────────────┐  │
│  │ CaseRepo    │ │         Services                     │  │
│  │ (memory /   │ │  SearchService ──► ISearchBackend    │  │
│  │  JSON file) │ │  TimelineService                     │  │
│  └─────────────┘ │  NextCameraRecommendationService     │  │
│                  └────────────────────────────────────┘   │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │               app/mock.py                            │  │
│  │  CAMERAS (10)  ·  SAMPLE_FRAMES (40)                 │  │
│  │  MockSearchBackend (metadata heuristics)             │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

### Key components

| Component | File | Responsibility |
|---|---|---|
| **Routes** | `app/routes.py` | HTTP handlers; thin orchestration layer |
| **SearchService** | `app/services/search.py` | Delegates to a pluggable `ISearchBackend` |
| **MockSearchBackend** | `app/services/search.py` | Heuristic scorer (clothing, accessories, location, time, face, tags) |
| **TimelineService** | `app/services/timeline.py` | Filters, sorts, and enriches sightings into a timeline |
| **NextCameraRecommendationService** | `app/services/camera_recommendation.py` | Graph traversal to rank neighbour cameras |
| **CaseRepository** | `app/repositories/` | CRUD for cases and sightings (in-memory default; JSON-backed option) |
| **Mock data** | `app/mock.py` | 10 cameras, 40 sample frames with metadata |
| **Seed data** | `data/` | `seed_cameras.json`, `seed_frames.json`, `demo_case.json` |

---

## Local setup

**Prerequisites:** Python 3.11+, Node.js 18+

```bash
# 1. Clone the repo (if you haven't already)
git clone https://github.com/RishitSrinivas/trace-test.git
cd trace-test

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Frontend setup (Next.js)

```bash
cd "Front End"
npm install --no-audit --progress=false
```

If `npm` looks stuck on downloads, this is usually first-run binary fetches for
`next` (`@next/swc-*`) and image tooling (`sharp`). These are large optional
packages and can take a while on slower networks. Workarounds:

```bash
# retry with longer network timeouts
npm install --no-audit --progress=false --fetch-timeout=600000 --fetch-retries=5

# if the network blocks optional binary downloads, use the JS fallback
npm install --omit=optional --no-audit --progress=false
```

### Optional: enable NVIDIA Nemotron enhancements

Create either `backend/.env` or `.env` with:

```bash
NEMOTRON_API_KEY=...
NEMOTRON_MODEL=...
NVIDIA_API_BASE=...
```

If these variables are missing or the API call fails, Trace AI keeps running and
automatically falls back to deterministic local explanations.

---

## Running the server

```bash
python -m uvicorn app.main:app --reload
```

The API is now available at **http://127.0.0.1:8000**  
Interactive Swagger docs at **http://127.0.0.1:8000/docs**

---

## Running tests

```bash
python -m pytest tests/ -v
```

The test suite covers 150+ cases across five files:

| File | Scope |
|---|---|
| `tests/test_api.py` | End-to-end route integration tests |
| `tests/test_repositories.py` | Case & sighting repository |
| `tests/test_search_service.py` | Scoring helpers and `SearchService` |
| `tests/test_timeline_service.py` | Timeline ordering and summaries |
| `tests/test_camera_recommendation_service.py` | Graph-based recommendations |

---

## API reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/cases` | Create a missing-person case |
| `GET` | `/cases` | List all cases |
| `GET` | `/cases/{case_id}` | Get a single case |
| `POST` | `/cases/{case_id}/search` | Run vision search; returns ranked sightings |
| `GET` | `/cases/{case_id}/timeline` | Build chronological movement timeline |
| `GET` | `/cases/{case_id}/recommendations` | Recommend next cameras to inspect |

---

## Example API calls

All examples assume the server is running on `http://127.0.0.1:8000`.

### 1 — Health check

```bash
curl -s http://127.0.0.1:8000/health | python -m json.tool
```

Expected response:

```json
{"status": "ok", "service": "trace-ai"}
```

### 2 — Create a case

```bash
curl -s -X POST http://127.0.0.1:8000/cases \
  -H "Content-Type: application/json" \
  -d '{
        "subject_name": "Alex Johnson",
        "description": "Adult, medium build, brown hair",
        "last_known_location": "North Campus Main Entrance",
        "clothing": "blue hoodie backpack"
      }' | python -m json.tool
```

Expected response (ids and timestamps will differ):

```json
{
    "id": "3e4c1a20-...",
    "subject_name": "Alex Johnson",
    "description": "Adult, medium build, brown hair",
    "last_known_location": "North Campus Main Entrance",
    "clothing": "blue hoodie backpack",
    "status": "open",
    "created_at": "2026-01-15T10:00:00Z"
}
```

### 3 — Run a search

```bash
CASE_ID="<id from step 2>"

curl -s -X POST "http://127.0.0.1:8000/cases/${CASE_ID}/search" \
  | python -m json.tool
```

Returns a ranked list of `Sighting` objects with `similarity_score` and a
human-readable `explanation`.

### 4 — Get the movement timeline

```bash
curl -s "http://127.0.0.1:8000/cases/${CASE_ID}/timeline" \
  | python -m json.tool
```

Returns a `Timeline` object with chronologically ordered `entries` and a
plain-English `summary`.

### 5 — Get camera recommendations

```bash
curl -s "http://127.0.0.1:8000/cases/${CASE_ID}/recommendations" \
  | python -m json.tool
```

Returns a prioritised list of cameras to check next, each annotated with
`reason`, `urgency_level`, and (where available) GPS coordinates.

---

## End-to-end demo flow

The file `scripts/demo.sh` automates the full flow below.  Run it while the
server is running:

```bash
bash scripts/demo.sh
```

### Step-by-step walkthrough

```
1. POST /cases            → creates case for "Alex Johnson"
2. POST /cases/{id}/search → scores 40 frames; returns top sightings
3. GET  /cases/{id}/timeline → orders sightings; prints path summary
4. GET  /cases/{id}/recommendations → suggests next cameras to pull
```

A typical run produces output similar to this:

```
=== STEP 1 — Create case ===
Case created: 3e4c1a20-f1b2-...  (subject: Alex Johnson)

=== STEP 2 — Run search ===
Top sighting: cam-001 | score 0.712 | Matched blue clothing; location aligns
              with last known area (North Campus - Main Entrance Gate).

=== STEP 3 — Build timeline ===
Summary: Alex Johnson was seen at North Campus - Main Entrance Gate (cam-001)
         at 09:15, then at Building B - 1st Floor (cam-003) at 09:22.

=== STEP 4 — Recommend next cameras ===
#1 cam-002 — Parking Lot A (priority 1, high urgency, retention 48 h)
#2 cam-004 — Cafeteria     (priority 2, medium urgency, retention 24 h)
```

---

## Future work

### Replacing mock search with real vision embeddings

The current `MockSearchBackend` uses metadata heuristics (colour tokens,
accessory keywords, location overlap, time proximity, text tags).  It is
designed to be a **drop-in placeholder** — the `ISearchBackend` interface
deliberately exposes only `rank_frames(case, frames, camera_map)` so that
swapping in a real model requires no changes to routes, timeline, or
recommendation code.

**Recommended migration path:**

1. **Choose an embedding model** — CLIP (`openai/clip-vit-base-patch32`) is a
   natural fit: it produces both image and text embeddings in the same vector
   space, so a clothing description like *"blue hoodie, backpack"* can be
   compared directly against frame thumbnails.

2. **Index your frames** — compute a CLIP embedding for every frame thumbnail
   and store them in a vector database such as FAISS (local), Qdrant, Pinecone,
   or pgvector.

3. **Implement `ISearchBackend`**:

   ```python
   # app/services/clip_backend.py  (example sketch)
   from app.services.search import ISearchBackend

   class ClipFaissBackend(ISearchBackend):
       def __init__(self, index_path: str) -> None:
           import faiss, clip, torch
           self.model, self.preprocess = clip.load("ViT-B/32")
           self.index = faiss.read_index(index_path)
           # ... load frame-id mapping ...

       def rank_frames(self, case, frames, camera_map, *, max_results=10, min_confidence=0.0):
           # Encode the case text as a query vector
           # Search the FAISS index for nearest neighbours
           # Return list[Sighting] ordered by cosine similarity
           ...
   ```

4. **Wire it in `app/store.py`** — replace one line:

   ```python
   # Before (mock):
   search_service = SearchService(backend=MockSearchBackend())

   # After (real):
   from app.services.clip_backend import ClipFaissBackend
   search_service = SearchService(backend=ClipFaissBackend("data/frame_index.faiss"))
   ```

5. Everything else — routes, timeline, recommendations, tests — stays
   unchanged.

### Other planned improvements

| Area | Idea |
|---|---|
| Persistence | Swap `MemoryCaseRepository` for `JsonCaseRepository` (already implemented) or a PostgreSQL/SQLite backed repository |
| Auth | Add API-key or OAuth2 middleware for multi-agency access control |
| Streaming | Server-Sent Events for live search progress on large camera networks |
| Geospatial routing | Use actual GPS coordinates (already on `Camera` model) with a road/walkway graph instead of the simple neighbour list |
| Re-ID pipeline | Integrate a person re-identification model (e.g. OSNet) as a second-stage re-ranker after the coarse CLIP search |
