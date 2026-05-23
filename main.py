from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from models import ExportPdfRequest, ModifyFloorPlanRequest, ParseFloorPlanResponse
from mock_data import apply_mock_modification, generate_mock_floor_plan
from pdf_generator import generate_floor_plan_pdf

ALLOWED_FILE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}

app = FastAPI(title="Makrly Floor Plan Backend", version="0.1.0")

# Replit + local development: allow Vercel frontend and localhost previews
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-hriwmbv45-bretts-projects-5b005afd.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/parse-floorplan", response_model=ParseFloorPlanResponse)
async def parse_floorplan(file: UploadFile = File(...)) -> ParseFloorPlanResponse:
    filename = file.filename or "upload"
    lowered = filename.lower()

    if not any(lowered.endswith(ext) for ext in ALLOWED_FILE_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload JPG, PNG, or PDF.",
        )

    # Consume file bytes for validation/use in future AI parsing
    _ = await file.read()

    plan = generate_mock_floor_plan(filename=filename)

    return ParseFloorPlanResponse(
        floorPlan=plan,
        source_filename=filename,
        message="Mock floor plan generated from uploaded file.",
    )


@app.post("/api/modify-floorplan")
def modify_floorplan(payload: ModifyFloorPlanRequest) -> dict:
    try:
        result = apply_mock_modification(payload.floorPlan, payload.command)
        return result
    except Exception as exc:  # pragma: no cover - broad catch for API safety
        raise HTTPException(status_code=500, detail=f"Failed to modify floor plan: {exc}")


@app.post("/api/export-pdf")
def export_pdf(payload: ExportPdfRequest):
    try:
        pdf_bytes = generate_floor_plan_pdf(payload.floorPlan)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {exc}")

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=floorplan-export.pdf"},
    )
