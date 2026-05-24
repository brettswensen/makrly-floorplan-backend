from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Point(BaseModel):
    x: float
    y: float


class Wall(BaseModel):
    id: str
    start: Point
    end: Point
    thickness: float = 0.5


class Door(BaseModel):
    id: str
    wallId: str
    position: float = Field(..., ge=0.0, le=1.0)
    width: float = 3.0


class Window(BaseModel):
    id: str
    wallId: str
    position: float = Field(..., ge=0.0, le=1.0)
    width: float = 4.0


class Room(BaseModel):
    id: str
    name: str
    points: List[Point]
    areaSqft: float


class FloorPlan(BaseModel):
    id: str = "fp_mock_1"
    name: str = "Parsed Floor Plan"
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    rooms: List[Room]
    walls: List[Wall]
    doors: List[Door]
    windows: List[Window]
    scale: float = Field(0.125, gt=0)


class ModifyFloorPlanRequest(BaseModel):
    floorPlan: FloorPlan
    command: str = Field(..., min_length=3)


class ParseFloorPlanResponse(BaseModel):
    floorPlan: FloorPlan
    source_filename: Optional[str] = None
    message: str = "Mock floor plan parsed successfully"


class ExportPdfRequest(BaseModel):
    floorPlan: FloorPlan
