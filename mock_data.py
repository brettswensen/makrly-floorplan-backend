from __future__ import annotations

import copy
import re
from typing import Dict, List

from models import Door, FloorPlan, Point, Room, Wall, Window


ROOM_SHIFTABLE_NAMES = {"kitchen", "living room", "bedroom", "bathroom", "office"}


def _rectangle_points(x1: float, y1: float, x2: float, y2: float) -> List[Point]:
    return [Point(x=x1, y=y1), Point(x=x2, y=y1), Point(x=x2, y=y2), Point(x=x1, y=y2)]


def _position_along_wall(wall: Wall, p: Point) -> float:
    dx = wall.end.x - wall.start.x
    dy = wall.end.y - wall.start.y
    denom = dx * dx + dy * dy
    if denom <= 0:
        return 0.0
    t = ((p.x - wall.start.x) * dx + (p.y - wall.start.y) * dy) / denom
    return max(0.0, min(1.0, t))


def generate_mock_floor_plan(filename: str | None = None) -> FloorPlan:
    """Creates a realistic 5-room house-like plan in feet."""
    plan_name = "Hardy Residence - Main Level" if filename else "Mock Residence - Main Level"

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
    wall_map = {w.id: w for w in walls}

    rooms = [
        Room(id="room_living", name="Living Room", points=_rectangle_points(0, 0, 18, 14), areaSqft=252),
        Room(id="room_kitchen", name="Kitchen", points=_rectangle_points(18, 0, 30, 12), areaSqft=144),
        Room(id="room_bed1", name="Bedroom", points=_rectangle_points(0, 14, 14, 26), areaSqft=168),
        Room(id="room_bath", name="Bathroom", points=_rectangle_points(14, 14, 20, 22), areaSqft=48),
        Room(id="room_office", name="Office", points=_rectangle_points(20, 12, 30, 26), areaSqft=140),
    ]

    door_points = [
        ("d1", "w4", Point(x=0, y=6), 3.0),
        ("d2", "w5", Point(x=18, y=8), 2.8),
        ("d3", "w6", Point(x=10, y=14), 3.0),
    ]
    doors = [
        Door(id=d_id, wallId=wall_id, position=_position_along_wall(wall_map[wall_id], p), width=width)
        for d_id, wall_id, p, width in door_points
    ]

    window_points = [
        ("win1", "w1", Point(x=10, y=0), 5.0),
        ("win2", "w2", Point(x=30, y=10), 4.0),
        ("win3", "w3", Point(x=22, y=26), 4.5),
    ]
    windows = [
        Window(id=w_id, wallId=wall_id, position=_position_along_wall(wall_map[wall_id], p), width=width)
        for w_id, wall_id, p, width in window_points
    ]

    return FloorPlan(
        id="fp_mock_1",
        name=plan_name,
        width=30,
        height=26,
        rooms=rooms,
        walls=walls,
        doors=doors,
        windows=windows,
        scale=0.125,
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
    room.points = [Point(x=p.x + dx, y=p.y + dy) for p in room.points]


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
