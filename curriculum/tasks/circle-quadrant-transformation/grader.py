from __future__ import annotations

import math
import sys
import json
from pathlib import Path

from curriculum import GraderInput, rubricgrader, rubrics


# ============================================================
# TOLERANCES
# ============================================================

CENTER_TOLERANCE = 15.0
BOUNDARY_TOLERANCE = 8.0
DIAMETER_TOLERANCE = 15.0
CONCENTRIC_TOLERANCE = 15.0

# Triangle-specific tolerances
TRIANGLE_CLOSURE_TOLERANCE = 2.0
TRIANGLE_MIN_HEIGHT = 10.0
TRIANGLE_MIN_TOP_SEPARATION = 5.0

MIN_BOUNDARY_CROSSING_RATIO = 0.05


# ============================================================
# SAFE HELPERS
# ============================================================

def number(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def get_points(element):
    points = element.get("points", [])

    if not isinstance(points, list):
        return []

    return points


def is_live(element):
    return (
        isinstance(element, dict)
        and not element.get("isDeleted", False)
    )


def valid_point(point):
    return (
        isinstance(point, (list, tuple))
        and len(point) >= 2
    )


# ============================================================
# BASIC GEOMETRY
# ============================================================

def element_center(element):
    return (
        number(element.get("x"))
        + number(element.get("width")) / 2,

        number(element.get("y"))
        + number(element.get("height")) / 2,
    )


def element_bounds(element):
    x = number(element.get("x"))
    y = number(element.get("y"))

    width = number(element.get("width"))
    height = number(element.get("height"))

    return (
        x,
        y,
        x + width,
        y + height,
    )


def distance(point_a, point_b):
    return math.hypot(
        point_a[0] - point_b[0],
        point_a[1] - point_b[1],
    )


# ============================================================
# ELEMENT TYPE DETECTION
# ============================================================

def is_circle(element):
    if element.get("type") != "ellipse":
        return False

    width = number(element.get("width"))
    height = number(element.get("height"))

    if width <= 0 or height <= 0:
        return False

    return abs(width - height) <= BOUNDARY_TOLERANCE


def is_rectangle(element):
    return element.get("type") == "rectangle"


def is_line(element):
    return (
        element.get("type") == "line"
        and len(get_points(element)) >= 2
    )


# ============================================================
# TRIANGLE DETECTION
# ============================================================

def normalized_triangle_points(triangle):
    """
    Return the triangle's point list after removing a duplicate
    closing point if one exists.

    Excalidraw line elements may represent a closed triangle as:

        [A, B, C, A]

    or simply:

        [A, B, C]

    This function normalizes both representations to:

        [A, B, C]
    """

    points = get_points(triangle)

    valid_points = [
        point
        for point in points
        if valid_point(point)
    ]

    if len(valid_points) < 3:
        return []

    # Remove duplicate closing point.
    if len(valid_points) >= 4:

        first = valid_points[0]
        last = valid_points[-1]

        if (
            abs(
                number(first[0])
                - number(last[0])
            )
            <= TRIANGLE_CLOSURE_TOLERANCE

            and

            abs(
                number(first[1])
                - number(last[1])
            )
            <= TRIANGLE_CLOSURE_TOLERANCE
        ):
            valid_points = valid_points[:-1]

    return valid_points


def is_triangle(element):
    """
    Detect a triangle stored as an Excalidraw line element.

    A valid triangle must:

    1. Be a line element.
    2. Contain exactly 3 geometric vertices after normalization.
    3. Have three non-collinear vertices.
    """

    if element.get("type") != "line":
        return False

    points = normalized_triangle_points(element)

    if len(points) != 3:
        return False

    absolute_points = triangle_points_absolute(element)

    if len(absolute_points) != 3:
        return False

    # Reject degenerate / collinear triangles.
    area = triangle_signed_area(
        absolute_points[0],
        absolute_points[1],
        absolute_points[2],
    )

    return abs(area) > 1.0


# ============================================================
# LINE GEOMETRY
# ============================================================

def line_endpoints(line):

    points = get_points(line)

    if len(points) < 2:
        return None

    first = points[0]
    last = points[-1]

    if (
        not valid_point(first)
        or not valid_point(last)
    ):
        return None

    x = number(line.get("x"))
    y = number(line.get("y"))

    p1 = (
        x + number(first[0]),
        y + number(first[1]),
    )

    p2 = (
        x + number(last[0]),
        y + number(last[1]),
    )

    return p1, p2


# ============================================================
# CIRCLE GEOMETRY
# ============================================================

def point_inside_circle(
    point,
    circle,
    tolerance=0.0,
):

    cx, cy = element_center(circle)

    rx = number(circle.get("width")) / 2
    ry = number(circle.get("height")) / 2

    if rx <= 0 or ry <= 0:
        return False

    normalized_distance = (
        ((point[0] - cx) / rx) ** 2
        + ((point[1] - cy) / ry) ** 2
    )

    return normalized_distance <= 1.0 + tolerance


def circle_inside_circle(inner, outer):

    inner_cx, inner_cy = element_center(inner)
    outer_cx, outer_cy = element_center(outer)

    inner_radius = number(inner.get("width")) / 2
    outer_radius = number(outer.get("width")) / 2

    center_distance = math.hypot(
        inner_cx - outer_cx,
        inner_cy - outer_cy,
    )

    return (
        center_distance + inner_radius
        <= outer_radius + BOUNDARY_TOLERANCE
    )


def circles_are_concentric(circle_a, circle_b):

    center_a = element_center(circle_a)
    center_b = element_center(circle_b)

    return (
        distance(center_a, center_b)
        <= CONCENTRIC_TOLERANCE
    )


# ============================================================
# QUADRANTS
# ============================================================

def get_quadrant(point, circle):

    cx, cy = element_center(circle)

    x, y = point

    if x < cx and y < cy:
        return "upper-left"

    if x >= cx and y < cy:
        return "upper-right"

    if x < cx and y >= cy:
        return "lower-left"

    return "lower-right"


def element_is_in_quadrant(
    element,
    circle,
    quadrant,
):

    cx, cy = element_center(circle)

    left, top, right, bottom = element_bounds(element)

    if quadrant == "upper-left":
        return (
            right < cx - BOUNDARY_TOLERANCE
            and bottom < cy - BOUNDARY_TOLERANCE
        )

    if quadrant == "upper-right":
        return (
            left > cx + BOUNDARY_TOLERANCE
            and bottom < cy - BOUNDARY_TOLERANCE
        )

    if quadrant == "lower-left":
        return (
            right < cx - BOUNDARY_TOLERANCE
            and top > cy + BOUNDARY_TOLERANCE
        )

    if quadrant == "lower-right":
        return (
            left > cx + BOUNDARY_TOLERANCE
            and top > cy + BOUNDARY_TOLERANCE
        )

    return False


# ============================================================
# DIAMETER DETECTION
# ============================================================

def line_is_horizontal_diameter(line, circle):

    endpoints = line_endpoints(line)

    if endpoints is None:
        return False

    p1, p2 = endpoints

    cx, cy = element_center(circle)

    radius_x = number(circle.get("width")) / 2

    if radius_x <= 0:
        return False

    if abs(p1[1] - p2[1]) > DIAMETER_TOLERANCE:
        return False

    line_y = (
        p1[1] + p2[1]
    ) / 2

    if abs(line_y - cy) > CENTER_TOLERANCE:
        return False

    left_x = min(
        p1[0],
        p2[0],
    )

    right_x = max(
        p1[0],
        p2[0],
    )

    required_left = (
        cx
        - radius_x
        + DIAMETER_TOLERANCE
    )

    required_right = (
        cx
        + radius_x
        - DIAMETER_TOLERANCE
    )

    return (
        left_x <= required_left
        and right_x >= required_right
    )


def line_is_vertical_diameter(line, circle):

    endpoints = line_endpoints(line)

    if endpoints is None:
        return False

    p1, p2 = endpoints

    cx, cy = element_center(circle)

    radius_y = number(
        circle.get("height")
    ) / 2

    if radius_y <= 0:
        return False

    if abs(p1[0] - p2[0]) > DIAMETER_TOLERANCE:
        return False

    line_x = (
        p1[0] + p2[0]
    ) / 2

    if abs(line_x - cx) > CENTER_TOLERANCE:
        return False

    top_y = min(
        p1[1],
        p2[1],
    )

    bottom_y = max(
        p1[1],
        p2[1],
    )

    required_top = (
        cy
        - radius_y
        + DIAMETER_TOLERANCE
    )

    required_bottom = (
        cy
        + radius_y
        - DIAMETER_TOLERANCE
    )

    return (
        top_y <= required_top
        and bottom_y >= required_bottom
    )


def line_completely_outside_circle(
    line,
    circle,
):

    endpoints = line_endpoints(line)

    if endpoints is None:
        return False

    p1, p2 = endpoints

    samples = 21

    for i in range(samples + 1):

        t = i / samples

        point = (
            p1[0]
            + (p2[0] - p1[0]) * t,

            p1[1]
            + (p2[1] - p1[1]) * t,
        )

        if point_inside_circle(
            point,
            circle,
        ):
            return False

    return True


# ============================================================
# TRIANGLE GEOMETRY
# ============================================================

def triangle_points_absolute(triangle):

    points = normalized_triangle_points(triangle)

    if len(points) != 3:
        return []

    x = number(triangle.get("x"))
    y = number(triangle.get("y"))

    return [
        (
            x + number(point[0]),
            y + number(point[1]),
        )
        for point in points
    ]


def triangle_signed_area(
    point_a,
    point_b,
    point_c,
):
    """
    Twice the signed area of the triangle.

    A value close to zero means the three points
    are effectively collinear.
    """

    return (
        (point_b[0] - point_a[0])
        * (point_c[1] - point_a[1])

        -

        (point_c[0] - point_a[0])
        * (point_b[1] - point_a[1])
    )


def triangle_bounds(triangle):
    """
    Calculate actual bounds from the triangle's
    absolute vertices.

    Do NOT rely on line width/height for this.
    """

    points = triangle_points_absolute(triangle)

    if len(points) != 3:
        return None

    xs = [
        point[0]
        for point in points
    ]

    ys = [
        point[1]
        for point in points
    ]

    return (
        min(xs),
        min(ys),
        max(xs),
        max(ys),
    )


def triangle_center(triangle):
    """
    Returns the centroid of the three triangle vertices.
    """

    points = triangle_points_absolute(triangle)

    if len(points) != 3:
        return None

    return (
        sum(
            point[0]
            for point in points
        ) / 3,

        sum(
            point[1]
            for point in points
        ) / 3,
    )


def triangle_is_inverted(triangle):
    """
    Strictly verify that the triangle points downward.

    A downward/inverted triangle should have:

    - Exactly one bottom vertex.
    - Two upper vertices.
    - The bottom vertex must be meaningfully below
      the two upper vertices.
    - The top two vertices must be separated enough
      to form an actual triangle.

    This is stronger than simply checking that one
    point has the largest Y coordinate.
    """

    points = triangle_points_absolute(triangle)

    if len(points) != 3:
        return False

    # Sort by Y coordinate.
    # In Excalidraw/screen coordinates:
    # smaller Y = visually higher
    # larger Y = visually lower
    points_by_y = sorted(
        points,
        key=lambda point: point[1],
    )

    top_a = points_by_y[0]
    top_b = points_by_y[1]
    bottom = points_by_y[2]

    top_average_y = (
        top_a[1]
        + top_b[1]
    ) / 2

    height = (
        bottom[1]
        - top_average_y
    )

    if height < TRIANGLE_MIN_HEIGHT:
        return False

    # The two upper vertices should actually form
    # a meaningful top edge rather than being nearly
    # on top of each other.
    top_separation = distance(
        top_a,
        top_b,
    )

    if top_separation < TRIANGLE_MIN_TOP_SEPARATION:
        return False

    # The bottom vertex must be clearly lower
    # than the top edge.
    if (
        bottom[1]
        <= top_average_y
        + TRIANGLE_MIN_HEIGHT
    ):
        return False

    # Ensure the bottom vertex is not simply part
    # of a nearly horizontal shape.
    overall_height = (
        max(
            point[1]
            for point in points
        )
        -

        min(
            point[1]
            for point in points
        )
    )

    if overall_height < TRIANGLE_MIN_HEIGHT:
        return False

    return True


def triangle_inside_circle(
    triangle,
    circle,
):

    points = triangle_points_absolute(
        triangle
    )

    if len(points) != 3:
        return False

    # A triangle is convex, and a circle is convex.
    # If all three triangle vertices are inside
    # the circle, the entire triangle is inside
    # the circle.
    return all(
        point_inside_circle(
            point,
            circle,
            tolerance=0.02,
        )
        for point in points
    )


def triangle_is_in_upper_left_quadrant(
    triangle,
    circle,
):
    """
    Verify the ENTIRE triangle is in the upper-left
    quadrant of the main circle.

    This intentionally uses the triangle's actual
    vertices rather than element width/height.
    """

    points = triangle_points_absolute(triangle)

    if len(points) != 3:
        return False

    cx, cy = element_center(circle)

    for point in points:

        if not (
            point[0]
            < cx - BOUNDARY_TOLERANCE
        ):
            return False

        if not (
            point[1]
            < cy - BOUNDARY_TOLERANCE
        ):
            return False

    return True


# ============================================================
# RECTANGLE BOUNDARY
# ============================================================

def rectangle_crosses_circle_boundary(
    rectangle,
    circle,
):

    left, top, right, bottom = element_bounds(
        rectangle
    )

    width = right - left
    height = bottom - top

    if width <= 0 or height <= 0:
        return False

    inside = 0
    outside = 0

    samples_x = 15
    samples_y = 15

    for ix in range(samples_x + 1):

        x = (
            left
            + width * ix / samples_x
        )

        for iy in range(samples_y + 1):

            y = (
                top
                + height * iy / samples_y
            )

            if point_inside_circle(
                (x, y),
                circle,
            ):
                inside += 1
            else:
                outside += 1

    total = inside + outside

    if total == 0:
        return False

    inside_ratio = (
        inside / total
    )

    outside_ratio = (
        outside / total
    )

    return (
        inside_ratio
        >= MIN_BOUNDARY_CROSSING_RATIO

        and

        outside_ratio
        >= MIN_BOUNDARY_CROSSING_RATIO
    )


# ============================================================
# MAIN RUBRIC GRADER
# ============================================================

@rubricgrader
def grader(input: GraderInput):

    snapshot = input["snapshots"]["excalidraw"]

    raw_elements = snapshot.get(
        "elements",
        [],
    )

    elements = [
        element
        for element in raw_elements
        if is_live(element)
    ]

    # ========================================================
    # CLASSIFY ELEMENTS
    # ========================================================

    circles = [
        e
        for e in elements
        if is_circle(e)
    ]

    rectangles = [
        e
        for e in elements
        if is_rectangle(e)
    ]

    all_lines = [
        e
        for e in elements
        if is_line(e)
    ]

    triangles = [
        e
        for e in all_lines
        if is_triangle(e)
    ]

    # IMPORTANT:
    #
    # The triangle is stored as a line element.
    #
    # Therefore the expected structure is:
    #
    # 4 circles
    # 1 rectangle
    # 1 triangle stored as line
    # 4 straight lines
    #
    # Total = 10 live elements
    #
    # This means 5 total line elements:
    #
    # 1 triangle + 4 straight lines

    straight_lines = [
        e
        for e in all_lines
        if not is_triangle(e)
    ]

    # ========================================================
    # BASIC STRUCTURE
    # ========================================================

    rubrics.assertTrue(
        "exactly_10_live_elements",
        len(elements) == 10,
        success="Exactly 10 live elements remain.",
        failure=(
            f"Expected exactly 10 live elements, "
            f"found {len(elements)}."
        ),
    )

    rubrics.assertTrue(
        "four_circles_preserved",
        len(circles) == 4,
        success="Exactly 4 circular elements remain.",
        failure=(
            f"Expected 4 circles, "
            f"found {len(circles)}."
        ),
    )

    rubrics.assertTrue(
        "one_rectangle_preserved",
        len(rectangles) == 1,
        success="Exactly 1 rectangle remains.",
        failure=(
            f"Expected 1 rectangle, "
            f"found {len(rectangles)}."
        ),
    )

    rubrics.assertTrue(
        "one_triangle_preserved",
        len(triangles) == 1,
        success="The original triangle is preserved.",
        failure=(
            f"Expected exactly 1 triangle, "
            f"found {len(triangles)}."
        ),
    )

    rubrics.assertTrue(
        "four_straight_lines_preserved",
        len(straight_lines) == 4,
        success=(
            "Exactly 4 straight line elements "
            "remain in addition to the triangle."
        ),
        failure=(
            f"Expected 4 straight lines, "
            f"found {len(straight_lines)}."
        ),
    )

    # ========================================================
    # IDENTIFY MAIN CIRCLE
    # ========================================================

    main_circle = (
        max(
            circles,
            key=lambda e:
                number(e.get("width"))
                * number(e.get("height")),
        )
        if circles
        else None
    )

    inner_circles = (
        [
            circle
            for circle in circles
            if (
                main_circle
                and circle.get("id")
                != main_circle.get("id")
            )
        ]
        if main_circle
        else []
    )

    # ========================================================
    # DIAMETERS
    # ========================================================

    horizontal_diameters = (
        [
            line
            for line in straight_lines
            if (
                main_circle
                and line_is_horizontal_diameter(
                    line,
                    main_circle,
                )
            )
        ]
        if main_circle
        else []
    )

    vertical_diameters = (
        [
            line
            for line in straight_lines
            if (
                main_circle
                and line_is_vertical_diameter(
                    line,
                    main_circle,
                )
            )
        ]
        if main_circle
        else []
    )

    rubrics.assertTrue(
        "one_horizontal_diameter",
        len(horizontal_diameters) == 1,
        success=(
            "Exactly one straight line forms "
            "the horizontal diameter."
        ),
        failure=(
            f"Expected exactly 1 horizontal diameter, "
            f"found {len(horizontal_diameters)}."
        ),
    )

    rubrics.assertTrue(
        "one_vertical_diameter",
        len(vertical_diameters) == 1,
        success=(
            "Exactly one straight line forms "
            "the vertical diameter."
        ),
        failure=(
            f"Expected exactly 1 vertical diameter, "
            f"found {len(vertical_diameters)}."
        ),
    )

    diameter_ids = {
        line.get("id")
        for line in (
            horizontal_diameters
            + vertical_diameters
        )
    }

    unused_lines = [
        line
        for line in straight_lines
        if line.get("id")
        not in diameter_ids
    ]

    rubrics.assertTrue(
        "two_unused_lines",
        len(unused_lines) == 2,
        success=(
            "Exactly 2 straight lines remain unused."
        ),
        failure=(
            f"Expected 2 unused lines, "
            f"found {len(unused_lines)}."
        ),
    )

    unused_lines_outside = (
        all(
            line_completely_outside_circle(
                line,
                main_circle,
            )
            for line in unused_lines
        )
        if main_circle
        else False
    )

    rubrics.assertTrue(
        "unused_lines_outside_main_circle",
        unused_lines_outside,
        success=(
            "Both unused lines remain completely "
            "outside the main circle."
        ),
        failure=(
            "At least one unused line enters "
            "the main circle."
        ),
    )

    # ========================================================
    # TRIANGLE
    # ========================================================

    triangle = (
        triangles[0]
        if len(triangles) == 1
        else None
    )

    # --------------------------------------------------------
    # TRIANGLE ORIENTATION
    # --------------------------------------------------------

    triangle_inverted = (
        triangle_is_inverted(triangle)
        if triangle
        else False
    )

    rubrics.assertTrue(
        "triangle_inverted",
        triangle_inverted,
        success=(
            "Triangle is inverted and points downward."
        ),
        failure=(
            "Triangle is not a valid downward-pointing "
            "inverted triangle."
        ),
    )

    # --------------------------------------------------------
    # TRIANGLE UPPER-LEFT QUADRANT
    # --------------------------------------------------------

    triangle_upper_left = (
        triangle_is_in_upper_left_quadrant(
            triangle,
            main_circle,
        )
        if triangle and main_circle
        else False
    )

    rubrics.assertTrue(
        "triangle_upper_left_quadrant",
        triangle_upper_left,
        success=(
            "All three triangle vertices are "
            "inside the upper-left quadrant."
        ),
        failure=(
            "The triangle is not completely inside "
            "the upper-left quadrant."
        ),
    )

    # --------------------------------------------------------
    # TRIANGLE INSIDE MAIN CIRCLE
    # --------------------------------------------------------

    triangle_inside = (
        triangle_inside_circle(
            triangle,
            main_circle,
        )
        if triangle and main_circle
        else False
    )

    rubrics.assertTrue(
        "triangle_inside_main_circle",
        triangle_inside,
        success=(
            "All three triangle vertices are inside "
            "the main circle."
        ),
        failure=(
            "At least one triangle vertex extends "
            "outside the main circle."
        ),
    )

    # ========================================================
    # UPPER-RIGHT CIRCLE
    # ========================================================

    upper_right_candidates = (
        [
            circle
            for circle in inner_circles
            if (
                main_circle
                and element_is_in_quadrant(
                    circle,
                    main_circle,
                    "upper-right",
                )
            )
        ]
        if main_circle
        else []
    )

    rubrics.assertTrue(
        "one_upper_right_circle",
        len(upper_right_candidates) == 1,
        success=(
            "Exactly one inner circle is "
            "in the upper-right quadrant."
        ),
        failure=(
            f"Expected 1 upper-right circle, "
            f"found {len(upper_right_candidates)}."
        ),
    )

    upper_right_circle = (
        upper_right_candidates[0]
        if len(upper_right_candidates) == 1
        else None
    )

    upper_right_inside = (
        circle_inside_circle(
            upper_right_circle,
            main_circle,
        )
        if (
            upper_right_circle
            and main_circle
        )
        else False
    )

    rubrics.assertTrue(
        "upper_right_circle_inside_main",
        upper_right_inside,
        success=(
            "Upper-right circle is completely "
            "inside the main circle."
        ),
        failure=(
            "Upper-right circle is not completely "
            "inside the main circle."
        ),
    )

    # ========================================================
    # LOWER-LEFT CIRCLES
    # ========================================================

    lower_left_candidates = (
        [
            circle
            for circle in inner_circles
            if (
                main_circle
                and element_is_in_quadrant(
                    circle,
                    main_circle,
                    "lower-left",
                )
            )
        ]
        if main_circle
        else []
    )

    rubrics.assertTrue(
        "two_lower_left_circles",
        len(lower_left_candidates) == 2,
        success=(
            "Exactly 2 inner circles are "
            "in the lower-left quadrant."
        ),
        failure=(
            f"Expected 2 lower-left circles, "
            f"found {len(lower_left_candidates)}."
        ),
    )

    lower_left_large = (
        max(
            lower_left_candidates,
            key=lambda c:
                number(c.get("width")),
        )
        if len(lower_left_candidates) == 2
        else None
    )

    lower_left_small = (
        min(
            lower_left_candidates,
            key=lambda c:
                number(c.get("width")),
        )
        if len(lower_left_candidates) == 2
        else None
    )

    nested = (
        circle_inside_circle(
            lower_left_small,
            lower_left_large,
        )
        if (
            lower_left_small
            and lower_left_large
        )
        else False
    )

    rubrics.assertTrue(
        "lower_left_nested",
        nested,
        success=(
            "Smaller lower-left circle is "
            "completely inside the larger circle."
        ),
        failure=(
            "Smaller lower-left circle is not "
            "fully contained in the larger circle."
        ),
    )

    concentric = (
        circles_are_concentric(
            lower_left_small,
            lower_left_large,
        )
        if (
            lower_left_small
            and lower_left_large
        )
        else False
    )

    rubrics.assertTrue(
        "lower_left_concentric",
        concentric,
        success=(
            "The two lower-left circles are concentric."
        ),
        failure=(
            "The two lower-left circles are "
            "not sufficiently concentric."
        ),
    )

    large_lower_left_inside = (
        circle_inside_circle(
            lower_left_large,
            main_circle,
        )
        if (
            lower_left_large
            and main_circle
        )
        else False
    )

    rubrics.assertTrue(
        "large_lower_left_inside_main",
        large_lower_left_inside,
        success=(
            "Larger lower-left circle is completely "
            "inside the main circle."
        ),
        failure=(
            "Larger lower-left circle extends "
            "outside the main circle."
        ),
    )

    # ========================================================
    # RECTANGLE
    # ========================================================

    rectangle = (
        rectangles[0]
        if len(rectangles) == 1
        else None
    )

    rectangle_center_lower_right = (
        get_quadrant(
            element_center(rectangle),
            main_circle,
        )
        == "lower-right"
        if (
            rectangle
            and main_circle
        )
        else False
    )

    rubrics.assertTrue(
        "rectangle_center_lower_right",
        rectangle_center_lower_right,
        success=(
            "Rectangle center is in "
            "the lower-right quadrant."
        ),
        failure=(
            "Rectangle center is not in "
            "the lower-right quadrant."
        ),
    )

    rectangle_crosses = (
        rectangle_crosses_circle_boundary(
            rectangle,
            main_circle,
        )
        if (
            rectangle
            and main_circle
        )
        else False
    )

    rubrics.assertTrue(
        "rectangle_crosses_main_circle",
        rectangle_crosses,
        success=(
            "Rectangle meaningfully crosses the "
            "main circle boundary."
        ),
        failure=(
            "Rectangle does not have meaningful "
            "parts both inside and outside "
            "the main circle."
        ),
    )


# ============================================================
# LOCAL TEST ENTRYPOINT
# ============================================================

if __name__ == "__main__":

    path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path(__file__).parent / "seed.json"
    )

    with open(path) as f:
        data = json.load(f)

    result = grader(
        {
            "snapshots": {
                "excalidraw": data
            },
            "transcript": "",
            "extra_fields": {},
            "posted_answer": None,
        }
    )

    print(
        f"result={result['result']}"
    )

    for key, value in result[
        "metadata"
    ]["rubrics"].items():

        print(
            f"{'PASS' if value['pass'] else 'FAIL'} "
            f"{key}: "
            f"{value.get('message') or value.get('description', '')}"
        )