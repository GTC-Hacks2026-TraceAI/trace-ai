"""Trace AI – FastAPI application entry point."""

from fastapi import FastAPI

from app.routes import router

app = FastAPI(
    title="Trace AI",
    description=(
        "Missing-person investigation backend. "
        "Surfaces likely sightings from indexed security footage, "
        "builds movement timelines, and recommends next cameras to inspect."
    ),
    version="0.1.0",
)

app.include_router(router)


@app.get("/health", tags=["system"])
def health_check() -> dict:
    return {"status": "ok", "service": "trace-ai"}
