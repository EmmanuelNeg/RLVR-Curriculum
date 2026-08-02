"""
Grader: Complete Agricultural Spraying Drone Sketch

Verifies that an Excalidraw project preserves the original drone sketch
and completes it into a recognizable agricultural spraying drone.

The task requires the model to:

1. Preserve the original drone seed elements.
2. Add four propellers associated with the four existing motors.
3. Add a central spray tank below the drone body.
4. Add at least two tank support struts.
5. Add a horizontal spray boom below the tank.
6. Add at least four spray nozzles distributed across the boom.
7. Add visible spray output below the nozzles.
8. Add five specific component labels:
   - Propeller
   - Camera
   - Spray Tank
   - Spray Boom
   - Spray Nozzle

Rubrics are intentionally separated into small, diagnostic checks so that
calibration results clearly show which parts of the task succeeded or failed.
"""

import sys
import json
import math
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_root))

from curriculum.sdk import ExcalidrawProject
from curriculum import GraderInput, rubricgrader, rubrics


# ============================================================================
# Helper functions
# ============================================================================

def center(element):
    """
    Return the center point of an Excalidraw element.
    """
    return (
        element.x + element.width / 2,
        element.y + element.height / 2,
    )


def distance(a, b):
    """
    Calculate the distance between the centers of two elements.
    """
    ax, ay = center(a)
    bx, by = center(b)

    return math.sqrt(
        (ax - bx) ** 2 +
        (ay - by) ** 2
    )


def get_text_elements(project):
    """
    Get all text elements from the project.

    Prefer the SDK's get_texts() method when available.
    Fall back to the raw element collection if necessary.
    """

    if hasattr(project, "get_texts"):
        return project.get_texts()

    if hasattr(project, "_elements"):
        return [
            element
            for element in project._elements
            if getattr(element, "type", None) == "text"
        ]

    return []


def get_line_elements(project):
    """
    Get all line elements from the project.

    Prefer the SDK's get_lines() method when available.
    Fall back to the raw element collection if necessary.
    """

    if hasattr(project, "get_lines"):
        return project.get_lines()

    if hasattr(project, "_elements"):
        return [
            element
            for element in project._elements
            if getattr(element, "type", None) == "line"
        ]

    return []


def is_horizontal_line(element, tolerance=15):
    """
    Return True if an element is approximately horizontal.
    """

    return (
        abs(element.height) <= tolerance
        and abs(element.width) > tolerance
    )


def is_vertical_line(element, tolerance=15):
    """
    Return True if an element is approximately vertical.
    """

    return (
        abs(element.width) <= tolerance
        and abs(element.height) > tolerance
    )


def is_near(a, b, max_distance=180):
    """
    Return True if two elements are spatially close.
    """

    return distance(a, b) <= max_distance


def text_contains_any(text, keywords):
    """
    Case-insensitive keyword matching.

    Used for specific required component labels.
    """

    if not text:
        return False

    normalized = text.strip().lower()

    return any(
        keyword.lower() in normalized
        for keyword in keywords
    )


# ============================================================================
# Label detection
# ============================================================================

def has_label(text_elements, keywords):
    """
    Check whether a required semantic label exists.

    The grader accepts reasonable variations.

    Examples:

    Camera:
        "Camera"
        "Camera Sensor"

    Spray Tank:
        "Spray Tank"

    Spray Boom:
        "Spray Boom"

    Spray Nozzle:
        "Spray Nozzle"
        "Nozzles"
    """

    for element in text_elements:

        text = getattr(element, "text", "")

        if text_contains_any(text, keywords):
            return True

    return False


# ============================================================================
# Main grader
# ============================================================================

@rubricgrader
def grader(input: GraderInput):

    project = ExcalidrawProject(
        input["snapshots"]["excalidraw"]
    )

    rectangles = project.get_rectangles()
    ellipses = project.get_ellipses()
    lines = get_line_elements(project)
    texts = get_text_elements(project)


    # ========================================================================
    # 1. IDENTIFY ORIGINAL SEED ELEMENTS
    # ========================================================================

    # The original seed is expected to contain:
    #
    # - One central drone body
    # - One yellow landing pad
    # - Four motor ellipses
    # - Four arm lines
    #
    # Additional elements are expected to be added by the model.
    #
    # The detection below intentionally uses approximate geometry rather
    # than exact element counts because the completed drone will contain
    # additional rectangles, ellipses, and lines.


    # ------------------------------------------------------------------------
    # Original drone body
    # ------------------------------------------------------------------------

    body_candidates = [
        rectangle
        for rectangle in rectangles
        if (
            180 <= rectangle.width <= 260
            and 80 <= rectangle.height <= 140
            and 500 <= rectangle.x <= 700
            and 200 <= rectangle.y <= 400
        )
    ]

    body = (
        body_candidates[0]
        if len(body_candidates) == 1
        else None
    )


    # ------------------------------------------------------------------------
    # Original yellow landing pad
    # ------------------------------------------------------------------------

    landing_pad_candidates = [
        rectangle
        for rectangle in rectangles
        if rectangle.has_background_color("#ffec99")
    ]

    landing_pad = (
        landing_pad_candidates[0]
        if len(landing_pad_candidates) == 1
        else None
    )


    # ------------------------------------------------------------------------
    # Motor candidates
    # ------------------------------------------------------------------------

    motor_candidates = [
        ellipse
        for ellipse in ellipses
        if (
            20 <= ellipse.width <= 100
            and 20 <= ellipse.height <= 100
        )
    ]


    # ------------------------------------------------------------------------
    # Arm candidates
    # ------------------------------------------------------------------------

    arm_candidates = [
        line
        for line in lines
        if (
            (
                is_horizontal_line(line)
                or is_vertical_line(line)
            )
            and max(line.width, line.height) >= 100
        )
    ]


    # ========================================================================
    # 2. SEED PRESERVATION RUBRICS
    # ========================================================================

    rubrics.assertTrue(
        "seed_one_body_preserved",
        len(body_candidates) == 1,
        success=(
            "Original central drone body was preserved."
        ),
        failure=(
            "Expected exactly one original central drone body, "
            f"but detected {len(body_candidates)} matching body candidate(s)."
        ),
    )


    rubrics.assertTrue(
        "seed_one_landing_pad_preserved",
        len(landing_pad_candidates) == 1,
        success=(
            "Original yellow landing pad was preserved."
        ),
        failure=(
            "Expected exactly one yellow landing pad, "
            f"but detected {len(landing_pad_candidates)}."
        ),
    )


    rubrics.assertTrue(
        "seed_four_arms_preserved",
        len(arm_candidates) >= 4,
        success=(
            "The original four drone arms were preserved."
        ),
        failure=(
            "Expected at least four original drone arm lines, "
            f"but detected only {len(arm_candidates)} suitable line(s)."
        ),
    )


    rubrics.assertTrue(
        "seed_four_motors_preserved",
        len(motor_candidates) >= 4,
        success=(
            "The original four motor ellipses were preserved."
        ),
        failure=(
            "Expected at least four motor ellipses, "
            f"but detected only {len(motor_candidates)}."
        ),
    )


    # ========================================================================
    # 3. FOUR PROPELLERS
    # ========================================================================

    # Propellers are expected to be larger, elongated ellipses.
    #
    # Small motor ellipses are excluded by the minimum size requirement.

    propeller_candidates = [
        ellipse
        for ellipse in ellipses
        if (
            max(ellipse.width, ellipse.height) >= 80
            and min(ellipse.width, ellipse.height) >= 15
        )
    ]


    rubrics.assertTrue(
        "four_propellers",
        len(propeller_candidates) >= 4,
        success=(
            f"Detected {len(propeller_candidates)} propeller-shaped "
            "elements. At least four are required."
        ),
        failure=(
            f"Only {len(propeller_candidates)}/4 propeller-shaped "
            "elements were detected."
        ),
    )


    # ========================================================================
    # 4. PROPELLERS ASSOCIATED WITH MOTORS
    # ========================================================================

    motor_propeller_matches = 0

    if (
        len(motor_candidates) >= 4
        and len(propeller_candidates) >= 4
    ):

        for motor in motor_candidates:

            nearby_propellers = [
                propeller
                for propeller in propeller_candidates
                if is_near(
                    motor,
                    propeller,
                    max_distance=180
                )
            ]

            if nearby_propellers:
                motor_propeller_matches += 1


    rubrics.assertTrue(
        "propellers_associated_with_motors",
        motor_propeller_matches >= 4,
        success=(
            "All four original motor positions have nearby "
            "propeller elements."
        ),
        failure=(
            f"Only {motor_propeller_matches}/4 motor positions "
            "have nearby propeller elements."
        ),
    )


    # ========================================================================
    # 5. SPRAY TANK
    # ========================================================================

    tank_candidates = []

    if body is not None:

        for rectangle in rectangles:

            if rectangle is body:
                continue

            # Tank should be:
            # - below the drone body
            # - reasonably large
            # - rectangular

            if (
                rectangle.width >= 100
                and rectangle.height >= 50
                and rectangle.y > body.y + body.height
            ):
                tank_candidates.append(rectangle)


    spray_tank = (
        tank_candidates[0]
        if tank_candidates
        else None
    )


    rubrics.assertTrue(
        "spray_tank",
        spray_tank is not None,
        success=(
            "Central spray tank detected beneath the drone body."
        ),
        failure=(
            "Central spray tank was not detected beneath the drone body."
        ),
    )


    # ========================================================================
    # 6. TANK SUPPORTS
    # ========================================================================

    support_candidates = []

    if spray_tank is not None:

        for line in lines:

            if (
                line.y <= spray_tank.y + spray_tank.height
                and line.y + line.height >= spray_tank.y - 100
            ):
                support_candidates.append(line)


    rubrics.assertTrue(
        "tank_supports",
        len(support_candidates) >= 2,
        success=(
            f"Detected {len(support_candidates)} tank support struts."
        ),
        failure=(
            "Fewer than two tank support struts were detected. "
            f"Found {len(support_candidates)}."
        ),
    )


    # ========================================================================
    # 7. SPRAY BOOM
    # ========================================================================

    boom_candidates = []

    if spray_tank is not None:

        for line in lines:

            if (
                is_horizontal_line(line)
                and line.y > spray_tank.y + spray_tank.height
                and line.width >= 150
            ):
                boom_candidates.append(line)


    spray_boom = (
        boom_candidates[0]
        if boom_candidates
        else None
    )


    rubrics.assertTrue(
        "spray_boom",
        spray_boom is not None,
        success=(
            "Horizontal spray boom detected beneath the spray tank."
        ),
        failure=(
            "Spray boom was not detected beneath the spray tank."
        ),
    )


    # ========================================================================
    # 8. SPRAY NOZZLES
    # ========================================================================

    nozzle_candidates = []

    if spray_boom is not None:

        # Small line-based nozzles

        for line in lines:

            if (
                line.y >= spray_boom.y
                and line.y <= spray_boom.y + 100
                and max(line.width, line.height) <= 80
            ):
                nozzle_candidates.append(line)


        # Small ellipse-based nozzles

        for ellipse in ellipses:

            if (
                ellipse.y >= spray_boom.y
                and ellipse.y <= spray_boom.y + 100
                and ellipse.width <= 80
                and ellipse.height <= 80
            ):
                nozzle_candidates.append(ellipse)


    rubrics.assertTrue(
        "four_nozzles",
        len(nozzle_candidates) >= 4,
        success=(
            f"Detected {len(nozzle_candidates)} spray nozzles. "
            "At least four are required."
        ),
        failure=(
            f"Only {len(nozzle_candidates)} suitable spray nozzles "
            "were detected. At least four are required."
        ),
    )


    # ========================================================================
    # 9. NOZZLES DISTRIBUTED ACROSS THE BOOM
    # ========================================================================

    distributed_nozzles = 0

    if (
        spray_boom is not None
        and nozzle_candidates
    ):

        boom_left = spray_boom.x
        boom_right = (
            spray_boom.x
            + spray_boom.width
        )

        # Ignore the extreme ends of the boom.
        # This ensures nozzles are spread across the usable spray area.

        usable_left = (
            boom_left
            + spray_boom.width * 0.15
        )

        usable_right = (
            boom_right
            - spray_boom.width * 0.15
        )

        for nozzle in nozzle_candidates:

            nozzle_x, _ = center(nozzle)

            if (
                usable_left
                <= nozzle_x
                <= usable_right
            ):
                distributed_nozzles += 1


    rubrics.assertTrue(
        "nozzles_distributed_across_boom",
        distributed_nozzles >= 4,
        success=(
            "At least four spray nozzles are distributed across "
            "the spray boom."
        ),
        failure=(
            f"Only {distributed_nozzles}/4 detected nozzles are "
            "distributed across the usable width of the spray boom."
        ),
    )


    # ========================================================================
    # 10. SPRAY OUTPUT
    # ========================================================================

    spray_output_candidates = []

    if spray_boom is not None:

        for line in lines:

            if (
                line.y > spray_boom.y + spray_boom.height
                and max(line.width, line.height) >= 20
            ):
                spray_output_candidates.append(line)


    rubrics.assertTrue(
        "spray_output",
        len(spray_output_candidates) >= 3,
        success=(
            f"Detected {len(spray_output_candidates)} visible spray "
            "output lines beneath the spray boom."
        ),
        failure=(
            "Visible spray output was not sufficiently detected. "
            "Expected at least three spray output lines below "
            f"the boom, but found {len(spray_output_candidates)}."
        ),
    )


    # ========================================================================
    # 11. REQUIRED LABEL: PROPELLER
    # ========================================================================

    rubrics.assertTrue(
        "label_propeller",
        has_label(
            texts,
            [
                "propeller",
                "propellers",
            ],
        ),
        success=(
            "Required component label 'Propeller' detected."
        ),
        failure=(
            "Missing required component label: Propeller."
        ),
    )


    # ========================================================================
    # 12. REQUIRED LABEL: CAMERA
    # ========================================================================

    rubrics.assertTrue(
        "label_camera",
        has_label(
            texts,
            [
                "camera",
                "camera sensor",
            ],
        ),
        success=(
            "Required component label 'Camera' detected."
        ),
        failure=(
            "Missing required component label: Camera."
        ),
    )


    # ========================================================================
    # 13. REQUIRED LABEL: SPRAY TANK
    # ========================================================================

    rubrics.assertTrue(
        "label_spray_tank",
        has_label(
            texts,
            [
                "spray tank",
            ],
        ),
        success=(
            "Required component label 'Spray Tank' detected."
        ),
        failure=(
            "Missing required component label: Spray Tank."
        ),
    )


    # ========================================================================
    # 14. REQUIRED LABEL: SPRAY BOOM
    # ========================================================================

    rubrics.assertTrue(
        "label_spray_boom",
        has_label(
            texts,
            [
                "spray boom",
            ],
        ),
        success=(
            "Required component label 'Spray Boom' detected."
        ),
        failure=(
            "Missing required component label: Spray Boom."
        ),
    )


    # ========================================================================
    # 15. REQUIRED LABEL: SPRAY NOZZLE
    # ========================================================================

    rubrics.assertTrue(
        "label_spray_nozzle",
        has_label(
            texts,
            [
                "spray nozzle",
                "spray nozzles",
                "nozzle",
                "nozzles",
            ],
        ),
        success=(
            "Required component label 'Spray Nozzle' detected."
        ),
        failure=(
            "Missing required component label: Spray Nozzle."
        ),
    )


# ============================================================================
# Standalone execution
# ============================================================================

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

    for key, value in result["metadata"]["rubrics"].items():

        print(
            f"  {'PASS' if value['pass'] else 'FAIL'} "
            f"{key}: "
            f"{value.get('message') or value.get('description', '')}"
        )