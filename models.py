from __future__ import annotations

from typing import List, Literal, Optional

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
    wall_id: str
    position: Point
    width: float = 3.0


class Window(BaseModel):
    id: str
    wall_id: str
    position: Point
    width: float = 4.0


class Room(BaseModel):
    id: str
    name: str
    polygon: List[Point]
    area_sqft: float


class Scale(BaseModel):
    unit: Literal["feet", "meters"] = "feet"
    pixels_per_unit: float = Field(..., gt=0)


class FloorPlan(BaseModel):
    name: str = "Parsed Floor Plan"
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    rooms: List[Room]
    walls: List[Wall]
    doors: List[Door]
    windows: List[Window]
    scale: Scale


class ModifyFloorPlanRequest(BaseModel):
    floorPlan: FloorPlan
    command: str = Field(..., min_length=3)


class ParseFloorPlanResponse(BaseModel):
    floorPlan: FloorPlan
    source_filename: Optional[str] = None
    message: str = "Mock floor plan parsed successfully"


class ExportPdfRequest(BaseModel):
    floorPlan: FloorPlan
