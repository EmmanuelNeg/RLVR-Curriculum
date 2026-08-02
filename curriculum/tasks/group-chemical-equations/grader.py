"""
Grader: Group Chemical Equations

Verifies that an Excalidraw project contains exactly 12 expected chemical
equations organized into four correctly labeled category boxes:

- SYNTHESIS
- DECOMPOSITION
- SINGLE DISPLACEMENT
- DOUBLE DISPLACEMENT

Additionally verifies that exactly three circles are placed in the
horizontal gaps between the four category boxes:

1. Between SYNTHESIS and DECOMPOSITION
2. Between DECOMPOSITION and SINGLE DISPLACEMENT
3. Between SINGLE DISPLACEMENT and DOUBLE DISPLACEMENT

Each circle must:
- Be approximately circular.
- Be fully contained within its horizontal gap.
- Not overlap either adjacent category box.
- Remain fully within the vertical bounds of the category boxes.

Rubrics:
- category_labels_preserved:
    All 4 required category labels exist

- category_boxes_present:
    Each category label is inside a grouping rectangle

- all_equations_present:
    All 12 expected chemical equations are present

- no_duplicate_equations:
    No chemical equation appears more than once

- expected_equations_present:
    No expected chemical equation is missing

- equations_fully_contained:
    Every equation is fully inside a category box

- equations_correctly_grouped:
    Every equation is inside its correct category

- equations_not_cross_grouped:
    No equation is contained by multiple category boxes

- three_circles_present:
    Exactly 3 approximately circular ellipses are present

- circle_between_synthesis_decomposition:
    One circle is fully positioned between SYNTHESIS and DECOMPOSITION

- circle_between_decomposition_single:
    One circle is fully positioned between DECOMPOSITION and
    SINGLE DISPLACEMENT

- circle_between_single_double:
    One circle is fully positioned between SINGLE DISPLACEMENT and
    DOUBLE DISPLACEMENT

- circles_within_vertical_bounds:
    All three circles remain fully within the vertical bounds of
    the category boxes
"""

from __future__ import annotations

import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Project root
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


from curriculum.sdk import ExcalidrawProject
from curriculum import GraderInput, rubricgrader, rubrics


# ---------------------------------------------------------------------------
# Expected chemical equations and their required categories
# ---------------------------------------------------------------------------

EXPECTED_GROUPS = {
    # Synthesis
    "2H₂ + O₂ → 2H₂O": "synthesis",
    "CaO + H₂O → Ca(OH)₂": "synthesis",
    "2Na + Cl₂ → 2NaCl": "synthesis",

    # Decomposition
    "CaCO₃ → CaO + CO₂": "decomposition",
    "2H₂O₂ → 2H₂O + O₂": "decomposition",
    "2KClO₃ → 2KCl + 3O₂": "decomposition",

    # Single Displacement
    "Zn + 2HCl → ZnCl₂ + H₂": "single_displacement",
    "Fe + CuSO₄ → FeSO₄ + Cu": "single_displacement",
    "2Al + 3CuCl₂ → 2AlCl₃ + 3Cu": "single_displacement",

    # Double Displacement
    "AgNO₃ + NaCl → AgCl + NaNO₃": "double_displacement",
    "BaCl₂ + Na₂SO₄ → BaSO₄ + 2NaCl": "double_displacement",
    "HCl + NaOH → NaCl + H₂O": "double_displacement",
}


# ---------------------------------------------------------------------------
# Category labels
# ---------------------------------------------------------------------------

CATEGORY_LABELS = {
    "SYNTHESIS": "synthesis",
    "DECOMPOSITION": "decomposition",
    "SINGLE DISPLACEMENT": "single_displacement",
    "DOUBLE DISPLACEMENT": "double_displacement",
}


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def get_bounds(element) -> tuple[float, float, float, float]:
    """
    Return element bounds as:

        (left, top, right, bottom)
    """

    return (
        element.x,
        element.y,
        element.x + element.width,
        element.y + element.height,
    )


def contains_element(
    container,
    element,
    padding: float = 0,
) -> bool:
    """
    Return True when the entire element is inside the container.

    Padding can be used as a tolerance from the container edges.
    """

    c_left, c_top, c_right, c_bottom = get_bounds(container)

    e_left, e_top, e_right, e_bottom = get_bounds(element)

    return (
        e_left >= c_left + padding
        and e_top >= c_top + padding
        and e_right <= c_right - padding
        and e_bottom <= c_bottom - padding
    )


def center_of(element) -> tuple[float, float]:
    """
    Return the center point of an element.
    """

    return (
        element.x + element.width / 2,
        element.y + element.height / 2,
    )


def point_inside(
    element,
    x: float,
    y: float,
) -> bool:
    """
    Return True when a point is inside an element.
    """

    return (
        element.x <= x <= element.x + element.width
        and element.y <= y <= element.y + element.height
    )


# ---------------------------------------------------------------------------
# Category detection
# ---------------------------------------------------------------------------

def find_category_labels(
    text_elements,
) -> dict[str, object]:
    """
    Find required category label text elements.

    Returns:

        {
            "synthesis": <text element>,
            "decomposition": <text element>,
            "single_displacement": <text element>,
            "double_displacement": <text element>,
        }
    """

    labels = {}

    for element in text_elements:

        text = element.text.strip()

        if text in CATEGORY_LABELS:

            category = CATEGORY_LABELS[text]

            labels[category] = element

    return labels


def find_category_boxes(
    rectangle_elements,
    category_labels,
) -> dict[str, object]:
    """
    Associate each category label with its containing rectangle.

    The rectangle is dynamically identified from the label's position.

    No hard-coded coordinates are required.
    """

    category_boxes = {}

    for category, label in category_labels.items():

        label_center_x, label_center_y = center_of(label)

        candidates = [
            rectangle
            for rectangle in rectangle_elements
            if point_inside(
                rectangle,
                label_center_x,
                label_center_y,
            )
        ]

        if not candidates:
            continue

        # If nested rectangles exist, choose the smallest
        # rectangle containing the category label.
        candidates.sort(
            key=lambda rectangle:
            rectangle.width * rectangle.height
        )

        category_boxes[category] = candidates[0]

    return category_boxes


# ---------------------------------------------------------------------------
# Circle detection
# ---------------------------------------------------------------------------

def find_circles(
    project,
    tolerance: float = 5,
) -> list[object]:
    """
    Find approximately circular ellipse elements.

    Excalidraw represents circles as ellipse elements.

    An ellipse is considered a circle when its width and height
    differ by no more than the specified tolerance.
    """

    circles = []

    ellipse_elements = project.get_ellipses()

    for element in ellipse_elements:

        width = abs(element.width)

        height = abs(element.height)

        # Ignore zero-size elements.
        if width == 0 or height == 0:
            continue

        # Treat approximately square ellipses as circles.
        if abs(width - height) <= tolerance:

            circles.append(element)

    return circles


# ---------------------------------------------------------------------------
# Check whether a circle is inside a horizontal gap
# ---------------------------------------------------------------------------

def circle_in_horizontal_gap(
    circle,
    left_box,
    right_box,
) -> bool:
    """
    Return True when the entire circle is positioned inside the
    horizontal gap between two adjacent category boxes.

    The circle must satisfy:

        circle.left >= left_box.right

    and:

        circle.right <= right_box.left

    This guarantees that the circle does not overlap either box.
    """

    left_box_right = (
        left_box.x
        + left_box.width
    )

    right_box_left = (
        right_box.x
    )

    circle_left = circle.x

    circle_right = (
        circle.x
        + circle.width
    )

    return (
        circle_left >= left_box_right
        and circle_right <= right_box_left
    )


# ---------------------------------------------------------------------------
# Check whether a circle is within vertical bounds
# ---------------------------------------------------------------------------

def circle_within_vertical_bounds(
    circle,
    top_box,
    bottom_box,
) -> bool:
    """
    Return True when the entire circle remains within the vertical
    span shared by the two adjacent category boxes.

    This prevents the circle from being placed above or below
    the category boxes.
    """

    top_boundary = max(
        top_box.y,
        bottom_box.y,
    )

    bottom_boundary = min(
        top_box.y + top_box.height,
        bottom_box.y + bottom_box.height,
    )

    circle_top = circle.y

    circle_bottom = (
        circle.y
        + circle.height
    )

    return (
        circle_top >= top_boundary
        and circle_bottom <= bottom_boundary
    )


# ---------------------------------------------------------------------------
# Find circle in a specific gap
# ---------------------------------------------------------------------------

def find_circles_in_gap(
    circles,
    left_box,
    right_box,
) -> list[object]:
    """
    Return all circles that are fully positioned inside the
    horizontal gap between two adjacent category boxes.
    """

    return [
        circle
        for circle in circles
        if circle_in_horizontal_gap(
            circle,
            left_box,
            right_box,
        )
    ]


# ---------------------------------------------------------------------------
# Main rubric grader
# ---------------------------------------------------------------------------

@rubricgrader
def grader(input: GraderInput):

    project = ExcalidrawProject(
        input["snapshots"]["excalidraw"]
    )

    text_elements = project.get_texts()

    rectangle_elements = project.get_rectangles()

    # -----------------------------------------------------------------------
    # 1. Find category labels
    # -----------------------------------------------------------------------

    category_labels = find_category_labels(
        text_elements
    )

    missing_categories = [
        category
        for category in CATEGORY_LABELS.values()
        if category not in category_labels
    ]

    rubrics.assertTrue(
        "category_labels_preserved",
        len(missing_categories) == 0,
        success=(
            "All 4 required category labels are present: "
            "SYNTHESIS, DECOMPOSITION, SINGLE DISPLACEMENT, "
            "and DOUBLE DISPLACEMENT."
        ),
        failure=(
            "Missing category label(s): "
            + ", ".join(missing_categories)
        ),
    )

    # -----------------------------------------------------------------------
    # 2. Find category boxes
    # -----------------------------------------------------------------------

    category_boxes = find_category_boxes(
        rectangle_elements,
        category_labels,
    )

    missing_boxes = [
        category
        for category in CATEGORY_LABELS.values()
        if category not in category_boxes
    ]

    rubrics.assertTrue(
        "category_boxes_present",
        len(missing_boxes) == 0,
        success=(
            "All 4 category labels are associated with "
            "grouping rectangles."
        ),
        failure=(
            "Could not find a grouping rectangle for category(s): "
            + ", ".join(missing_boxes)
        ),
    )

    # -----------------------------------------------------------------------
    # 3. Find expected chemical equations
    # -----------------------------------------------------------------------

    equation_elements = [
        element
        for element in text_elements
        if element.text.strip() in EXPECTED_GROUPS
    ]

    rubrics.assertTrue(
        "all_equations_present",
        len(equation_elements) == 12,
        success=(
            "All 12 expected chemical equations are present."
        ),
        failure=(
            f"Expected 12 chemical equations, "
            f"but found {len(equation_elements)}."
        ),
    )

    # -----------------------------------------------------------------------
    # 4. Check duplicate equations
    # -----------------------------------------------------------------------

    equation_texts = [
        element.text.strip()
        for element in equation_elements
    ]

    duplicate_equations = [
        equation
        for equation in set(equation_texts)
        if equation_texts.count(equation) > 1
    ]

    rubrics.assertTrue(
        "no_duplicate_equations",
        len(duplicate_equations) == 0,
        success=(
            "All 12 chemical equations are unique."
        ),
        failure=(
            "Duplicate chemical equation(s) detected: "
            + ", ".join(duplicate_equations)
        ),
    )

    # -----------------------------------------------------------------------
    # 5. Check all expected equations exist
    # -----------------------------------------------------------------------

    found_equations = set(
        equation_texts
    )

    expected_equations = set(
        EXPECTED_GROUPS.keys()
    )

    missing_equations = (
        expected_equations
        - found_equations
    )

    rubrics.assertTrue(
        "expected_equations_present",
        len(missing_equations) == 0,
        success=(
            "All expected chemical equations are present."
        ),
        failure=(
            "Missing chemical equation(s): "
            + ", ".join(
                sorted(missing_equations)
            )
        ),
    )

    # -----------------------------------------------------------------------
    # 6. Determine equation containment results
    # -----------------------------------------------------------------------

    containment_failures = []

    multiple_containment = []

    grouping_failures = []

    if len(category_boxes) == 4:

        for equation_element in equation_elements:

            equation = equation_element.text.strip()

            expected_group = EXPECTED_GROUPS.get(
                equation
            )

            if expected_group is None:
                continue

            # Find all category boxes containing this equation.
            containing_groups = [
                category
                for category, box in category_boxes.items()
                if contains_element(
                    box,
                    equation_element,
                )
            ]

            # Equation must be fully contained in a category box.
            if not containing_groups:

                containment_failures.append(
                    equation
                )

                continue

            # Equation must not be contained by multiple boxes.
            if len(containing_groups) > 1:

                multiple_containment.append(
                    f"{equation} "
                    f"({', '.join(containing_groups)})"
                )

                continue

            actual_group = containing_groups[0]

            # Verify correct category.
            if actual_group != expected_group:

                grouping_failures.append(
                    f"{equation} "
                    f"(found in {actual_group}, "
                    f"expected {expected_group})"
                )

    # -----------------------------------------------------------------------
    # 7. Rubric: full equation containment
    # -----------------------------------------------------------------------

    rubrics.assertTrue(
        "equations_fully_contained",
        len(containment_failures) == 0,
        success=(
            "All chemical equations are fully contained "
            "within a grouping box."
        ),
        failure=(
            "The following equation(s) are not fully "
            "contained within any grouping box: "
            + "; ".join(
                containment_failures
            )
        ),
    )

    # -----------------------------------------------------------------------
    # 8. Rubric: no overlapping group membership
    # -----------------------------------------------------------------------

    rubrics.assertTrue(
        "equations_not_cross_grouped",
        len(multiple_containment) == 0,
        success=(
            "No chemical equation is contained "
            "by multiple category boxes."
        ),
        failure=(
            "The following equation(s) are contained "
            "by multiple category boxes: "
            + "; ".join(
                multiple_containment
            )
        ),
    )

    # -----------------------------------------------------------------------
    # 9. Rubric: correct grouping
    # -----------------------------------------------------------------------

    rubrics.assertTrue(
        "equations_correctly_grouped",
        len(grouping_failures) == 0,
        success=(
            "All chemical equations are placed "
            "in their correct reaction-type category."
        ),
        failure=(
            "Incorrect chemical equation grouping detected: "
            + "; ".join(
                grouping_failures
            )
        ),
    )

    # -----------------------------------------------------------------------
    # 10. Find circles
    # -----------------------------------------------------------------------

    circles = find_circles(
        project
    )

    # -----------------------------------------------------------------------
    # 11. Require exactly 3 circles
    # -----------------------------------------------------------------------

    rubrics.assertTrue(
        "three_circles_present",
        len(circles) == 3,
        success=(
            "Exactly 3 circles are present."
        ),
        failure=(
            f"Expected exactly 3 circles, "
            f"but found {len(circles)}. "
            f"There must be one circle in each gap between "
            f"the four category boxes."
        ),
    )

    # -----------------------------------------------------------------------
    # Initialize circle placement checks
    # -----------------------------------------------------------------------

    circle_between_synthesis_decomposition = False

    circle_between_decomposition_single = False

    circle_between_single_double = False

    circles_vertical_bounds_valid = False

    # -----------------------------------------------------------------------
    # 12. Check circle placement
    # -----------------------------------------------------------------------

    if (
        len(circles) == 3
        and len(category_boxes) == 4
    ):

        synthesis_box = category_boxes[
            "synthesis"
        ]

        decomposition_box = category_boxes[
            "decomposition"
        ]

        single_displacement_box = category_boxes[
            "single_displacement"
        ]

        double_displacement_box = category_boxes[
            "double_displacement"
        ]

        # ---------------------------------------------------------------
        # Find circles in each required gap.
        # ---------------------------------------------------------------

        synthesis_decomposition_circles = (
            find_circles_in_gap(
                circles,
                synthesis_box,
                decomposition_box,
            )
        )

        decomposition_single_circles = (
            find_circles_in_gap(
                circles,
                decomposition_box,
                single_displacement_box,
            )
        )

        single_double_circles = (
            find_circles_in_gap(
                circles,
                single_displacement_box,
                double_displacement_box,
            )
        )

        # ---------------------------------------------------------------
        # Each gap must contain exactly one circle.
        # ---------------------------------------------------------------

        circle_between_synthesis_decomposition = (
            len(
                synthesis_decomposition_circles
            ) == 1
        )

        circle_between_decomposition_single = (
            len(
                decomposition_single_circles
            ) == 1
        )

        circle_between_single_double = (
            len(
                single_double_circles
            ) == 1
        )

        # ---------------------------------------------------------------
        # Verify all three circles stay within vertical bounds.
        # ---------------------------------------------------------------

        circles_vertical_bounds_valid = True

        # Circle between SYNTHESIS and DECOMPOSITION.
        if (
            len(
                synthesis_decomposition_circles
            ) == 1
        ):

            circle = (
                synthesis_decomposition_circles[0]
            )

            if not circle_within_vertical_bounds(
                circle,
                synthesis_box,
                decomposition_box,
            ):

                circles_vertical_bounds_valid = False

        # Circle between DECOMPOSITION and
        # SINGLE DISPLACEMENT.
        if (
            len(
                decomposition_single_circles
            ) == 1
        ):

            circle = (
                decomposition_single_circles[0]
            )

            if not circle_within_vertical_bounds(
                circle,
                decomposition_box,
                single_displacement_box,
            ):

                circles_vertical_bounds_valid = False

        # Circle between SINGLE DISPLACEMENT
        # and DOUBLE DISPLACEMENT.
        if (
            len(
                single_double_circles
            ) == 1
        ):

            circle = (
                single_double_circles[0]
            )

            if not circle_within_vertical_bounds(
                circle,
                single_displacement_box,
                double_displacement_box,
            ):

                circles_vertical_bounds_valid = False

    # -----------------------------------------------------------------------
    # 13. Circle between SYNTHESIS and DECOMPOSITION
    # -----------------------------------------------------------------------

    rubrics.assertTrue(
        "circle_between_synthesis_decomposition",
        circle_between_synthesis_decomposition,
        success=(
            "Exactly one circle is fully positioned "
            "in the horizontal gap between SYNTHESIS "
            "and DECOMPOSITION."
        ),
        failure=(
            "There must be exactly one circle fully positioned "
            "between the SYNTHESIS and DECOMPOSITION boxes. "
            "The circle must not overlap either box."
        ),
    )

    # -----------------------------------------------------------------------
    # 14. Circle between DECOMPOSITION and SINGLE DISPLACEMENT
    # -----------------------------------------------------------------------

    rubrics.assertTrue(
        "circle_between_decomposition_single",
        circle_between_decomposition_single,
        success=(
            "Exactly one circle is fully positioned "
            "in the horizontal gap between DECOMPOSITION "
            "and SINGLE DISPLACEMENT."
        ),
        failure=(
            "There must be exactly one circle fully positioned "
            "between the DECOMPOSITION and SINGLE DISPLACEMENT "
            "boxes. The circle must not overlap either box."
        ),
    )

    # -----------------------------------------------------------------------
    # 15. Circle between SINGLE DISPLACEMENT and DOUBLE DISPLACEMENT
    # -----------------------------------------------------------------------

    rubrics.assertTrue(
        "circle_between_single_double",
        circle_between_single_double,
        success=(
            "Exactly one circle is fully positioned "
            "in the horizontal gap between SINGLE DISPLACEMENT "
            "and DOUBLE DISPLACEMENT."
        ),
        failure=(
            "There must be exactly one circle fully positioned "
            "between the SINGLE DISPLACEMENT and DOUBLE DISPLACEMENT "
            "boxes. The circle must not overlap either box."
        ),
    )

    # -----------------------------------------------------------------------
    # 16. Circle vertical bounds
    # -----------------------------------------------------------------------

    rubrics.assertTrue(
        "circles_within_vertical_bounds",
        circles_vertical_bounds_valid,
        success=(
            "All three circles remain fully within "
            "the vertical bounds of their adjacent "
            "category boxes."
        ),
        failure=(
            "At least one circle extends above or below "
            "the vertical bounds of its adjacent category boxes."
        ),
    )


# ---------------------------------------------------------------------------
# Local test runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    import json

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
    ][
        "rubrics"
    ].items():

        print(
            f"  "
            f"{'PASS' if value['pass'] else 'FAIL'} "
            f"{key}: "
            f"{value.get('message') or value.get('description', '')}"
        )