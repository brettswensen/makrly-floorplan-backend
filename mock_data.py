from __future__ import annotations

import copy
import re
from typing import Dict, List

from models import Door, FloorPlan, Point, Room, Scale, Wall, Window


ROOM_SHIFTABLE_NAMES = {"kitchen", "living room", "bedroom", "bathroom", "office"}


def _rectangle_points(x1: float, y1: float, x2: float, y2: float) -> List[Point]:
    return [Point(x=x1, y=y1), Point(x=x2, y=y1), Point(x=x2, y=y2), Point(x=x1, y=y2)]


def generate_mock_floor_plan(filename: str | None = None) -> FloorPlan:
    """Creates a realistic 5-room house-like plan in feet."""
    plan_name = "Hardy Residence - Main Level" if filename else "Mock Residence - Main Level"

    rooms = [
        Room(id="room_living", name="Living Room", polygon=_rectangle_points(0, 0, 18, 14), area_sqft=252),
        Room(id="room_kitchen", name="Kitchen", polygon=_rectangle_points(18, 0, 30, 12), area_sqft=144),
        Room(id="room_bed1", name="Bedroom", polygon=_rectangle_points(0, 14, 14, 26), area_sqft=168),
        Room(id="room_bath", name="Bathroom", polygon=_rectangle_points(14, 14, 20, 22), area_sqft=48),
        Room(id="room_office", name="Office", polygon=_rectangle_points(20, 12, 30, 26), area_sqft=140),
    ]

    walls = [
        Wall(id="w1", start=Point(x=0, y=0), end=Point(x=30, y=0)),
        Wall(id="w2", start=Point(x=30, y=0), end=Point(x=30, y=26)),
        Wall(id="w3", start=Point(x=30, y=26), end=Point(x=0, y=26)),
        Wall(id="w4", start=Point(x=0, y=26), end=Point(x=0, y=0)),
        Wall(id="w5", start=Point(x=18, y=0), end=Point(x=18, y=14)),
        Wall(id="w6", start=Point(x=0, y=14), end=Point(x=20, y=14)),
        Wall(id="w7", start=Point(x=14, y=14), end=Point(x=14, y=22)),
        Wall(id="w8", start=Point(x=20, y=12), end=Point(x=20, y=26)),
    ]

    doors = [
        Door(id="d1", wall_id="w4", position=Point(x=0, y=6), width=3.0),
        Door(id="d2", wall_id="w5", position=Point(x=18, y=8), width=2.8),
        Door(id="d3", wall_id="w6", position=Point(x=10, y=14), width=3.0),
    ]

    windows = [
        Window(id="win1", wall_id="w1", position=Point(x=10, y=0), width=5.0),
        Window(id="win2", wall_id="w2", position=Point(x=30, y=10), width=4.0),
        Window(id="win3", wall_id="w3", position=Point(x=22, y=26), width=4.5),
    ]

    return FloorPlan(
        name=plan_name,
        width=30,
        height=26,
        rooms=rooms,
        walls=walls,
        doors=doors,
        windows=windows,
        scale=Scale(unit="feet", pixels_per_unit=12.0),
    )


def _extract_distance_feet(command: str) -> float:
    # Supports: "2 feet", "2 ft", "2.5"
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:feet|foot|ft)?", command.lower())
    if not match:
        return 2.0
    return float(match.group(1))


def _direction_to_vector(direction: str, distance: float) -> tuple[float, float]:
    direction = direction.lower()
    if direction in {"left", "west"}:
        return -distance, 0.0
    if direction in {"right", "east"}:
        return distance, 0.0
    if direction in {"up", "north"}:
        return 0.0, distance
    if direction in {"down", "south"}:
        return 0.0, -distance
    return -distance, 0.0


def _move_room(room: Room, dx: float, dy: float) -> None:
    room.polygon = [Point(x=p.x + dx, y=p.y + dy) for p in room.polygon]


def apply_mock_modification(floor_plan: FloorPlan, command: str) -> Dict:
    updated = copy.deepcopy(floor_plan)
    normalized = command.lower().strip()

    distance = _extract_distance_feet(normalized)

    direction = "left"
    for d in ["left", "right", "up", "down", "north", "south", "east", "west"]:
        if d in normalized:
            direction = d
            break

    target_room = None
    for room in updated.rooms:
        if room.name.lower() in normalized:
            target_room = room
            break

    if target_room is None:
        # fall back: move kitchen if command references wall generically
        for room in updated.rooms:
            if room.name.lower() == "kitchen":
                target_room = room
                break

    if target_room is None:
        return {
            "floorPlan": updated,
            "applied": False,
            "message": "No modifiable room found in floor plan.",
        }

    dx, dy = _direction_to_vector(direction, distance)
    _move_room(target_room, dx, dy)

    return {
        "floorPlan": updated,
        "applied": True,
        "message": f"Applied mock modification: moved {target_room.name} {distance} ft {direction}.",
    }
