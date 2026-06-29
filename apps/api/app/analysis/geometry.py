from __future__ import annotations

from math import asin, atan2, cos, degrees, radians, sin, sqrt


def haversine_distance_meters(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    earth_radius_m = 6_371_000
    latitude_delta = radians(latitude_b - latitude_a)
    longitude_delta = radians(longitude_b - longitude_a)
    source_latitude = radians(latitude_a)
    target_latitude = radians(latitude_b)
    arc = (
        sin(latitude_delta / 2) ** 2
        + cos(source_latitude) * cos(target_latitude) * sin(longitude_delta / 2) ** 2
    )
    return 2 * earth_radius_m * asin(sqrt(arc))


def point_in_polygon(
    latitude: float,
    longitude: float,
    polygon_points: tuple[tuple[float, float], ...],
) -> bool:
    inside = False
    point_count = len(polygon_points)
    if point_count < 3:
        return False

    previous_longitude, previous_latitude = polygon_points[-1]
    for current_longitude, current_latitude in polygon_points:
        intersects = ((current_latitude > latitude) != (previous_latitude > latitude)) and (
            longitude
            < (previous_longitude - current_longitude)
            * (latitude - current_latitude)
            / (previous_latitude - current_latitude + 1e-12)
            + current_longitude
        )
        if intersects:
            inside = not inside
        previous_longitude = current_longitude
        previous_latitude = current_latitude
    return inside


def build_circle_polygon(
    latitude: float,
    longitude: float,
    radius_m: int,
    *,
    steps: int = 32,
) -> list[list[float]]:
    earth_radius_m = 6_371_000
    angular_distance = radius_m / earth_radius_m
    latitude_radians = radians(latitude)
    longitude_radians = radians(longitude)
    ring: list[list[float]] = []

    for step in range(steps):
        bearing = 2 * 3.141592653589793 * step / steps
        projected_latitude = asin(
            sin(latitude_radians) * cos(angular_distance)
            + cos(latitude_radians) * sin(angular_distance) * cos(bearing),
        )
        projected_longitude = longitude_radians + atan2(
            sin(bearing) * sin(angular_distance) * cos(latitude_radians),
            cos(angular_distance) - sin(latitude_radians) * sin(projected_latitude),
        )
        ring.append(
            [
                round(degrees(projected_longitude), 7),
                round(degrees(projected_latitude), 7),
            ],
        )

    if ring:
        ring.append(ring[0])
    return ring
