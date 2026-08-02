import json
import random
import uuid
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_FILE = Path(__file__).parent / "seed.json"


# ============================================================
# HELPERS
# ============================================================

def new_id():
    return str(uuid.uuid4()).replace("-", "")[:20]


def base_element(
    element_type,
    x,
    y,
    width,
    height,
    stroke="#1e1e1e",
    background="transparent",
):
    return {
        "id": new_id(),
        "type": element_type,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "angle": 0,
        "strokeColor": stroke,
        "backgroundColor": background,
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": None,
        "seed": random.randint(1, 999999),
        "version": 1,
        "versionNonce": random.randint(1, 999999),
        "isDeleted": False,
        "boundElements": [],
        "updated": 1,
        "link": None,
        "locked": False,
    }


# ============================================================
# LARGE CIRCLE
# ============================================================

def create_large_circle():

    return base_element(
        element_type="ellipse",
        x=400,
        y=150,
        width=600,
        height=600,
    )


# ============================================================
# TRIANGLE
# ============================================================

def create_triangle(
    x,
    y,
    width,
    height,
):

    element = base_element(
        element_type="line",
        x=x,
        y=y,
        width=width,
        height=height,
    )

    # Three-point triangle.
    #
    # Initial orientation:
    #
    #          /\
    #         /  \
    #        /    \
    #       /______\
    #
    # The task requires the model to rotate it upside down.
    #
    # The final target should therefore be:
    #
    #       \______/
    #        \    /
    #         \  /
    #          \/
    #

    element["points"] = [
        [0, height],
        [width / 2, 0],
        [width, height],
        [0, height],
    ]

    element["lastCommittedPoint"] = [
        width,
        height,
    ]

    return element


# ============================================================
# LINE
# ============================================================

def create_line(
    x,
    y,
    x2,
    y2,
):

    width = x2 - x
    height = y2 - y

    element = base_element(
        element_type="line",
        x=x,
        y=y,
        width=width,
        height=height,
    )

    element["points"] = [
        [0, 0],
        [width, height],
    ]

    element["lastCommittedPoint"] = [
        width,
        height,
    ]

    return element


# ============================================================
# ELLIPSE
# ============================================================

def create_ellipse(
    x,
    y,
    width,
    height,
):

    return base_element(
        element_type="ellipse",
        x=x,
        y=y,
        width=width,
        height=height,
    )


# ============================================================
# RECTANGLE
# ============================================================

def create_rectangle(
    x,
    y,
    width,
    height,
):

    return base_element(
        element_type="rectangle",
        x=x,
        y=y,
        width=width,
        height=height,
    )


# ============================================================
# BUILD INITIAL ELEMENTS
# ============================================================

elements = []


# ============================================================
# 1. LARGE CENTRAL CIRCLE
# ============================================================

elements.append(
    create_large_circle()
)


# ============================================================
# 2. FOUR LONG LOOSE LINES
# ============================================================
#
# The main circle has a diameter of 600px.
#
# Each line is approximately 900px long, making them
# substantially longer than the circle's diameter.
#
# The model must reorganize the lines so that two of them
# form a horizontal and vertical cross through the center
# of the large circle.
#
# The remaining two lines act as distractors.
# ============================================================


# Long horizontal line #1
elements.append(
    create_line(
        x=100,
        y=80,
        x2=1000,
        y2=80,
    )
)


# Long vertical line #1
elements.append(
    create_line(
        x=1100,
        y=50,
        x2=1100,
        y2=950,
    )
)


# Long horizontal line #2
elements.append(
    create_line(
        x=100,
        y=850,
        x2=1000,
        y2=850,
    )
)


# Long vertical line #2
elements.append(
    create_line(
        x=1200,
        y=50,
        x2=1200,
        y2=950,
    )
)


# ============================================================
# 3. TRIANGLE
# ============================================================
#
# Initially outside the large circle.
#
# The model must:
#
# 1. Move it into the upper-left quadrant.
# 2. Rotate it 180 degrees.
# 3. Keep it completely inside the large circle.
# ============================================================

elements.append(
    create_triangle(
        x=100,
        y=150,
        width=140,
        height=120,
    )
)


# ============================================================
# 4. SINGLE CIRCLE
# ============================================================
#
# This circle must eventually be placed completely inside
# the upper-right quadrant of the large circle.
# ============================================================

elements.append(
    create_ellipse(
        x=1080,
        y=120,
        width=120,
        height=120,
    )
)


# ============================================================
# 5. LARGE CIRCLE FOR NESTED PAIR
# ============================================================
#
# This is one of the two differently-sized circles.
#
# It must eventually be moved into the lower-left quadrant.
# ============================================================

elements.append(
    create_ellipse(
        x=100,
        y=550,
        width=200,
        height=200,
    )
)


# ============================================================
# 6. SMALL CIRCLE FOR NESTED PAIR
# ============================================================
#
# This is the second differently-sized circle.
#
# The model must place it concentrically inside the larger
# circle in the lower-left quadrant.
# ============================================================

elements.append(
    create_ellipse(
        x=320,
        y=650,
        width=90,
        height=90,
    )
)


# ============================================================
# 7. RECTANGLE
# ============================================================
#
# Initially outside the large circle.
#
# The model must move it to the lower-right quadrant so that:
#
# - Most of the rectangle is inside the large circle.
# - A portion extends outside the large circle.
# - The rectangle crosses the circle boundary.
# ============================================================

elements.append(
    create_rectangle(
        x=1080,
        y=650,
        width=240,
        height=150,
    )
)


# ============================================================
# EXCALIDRAW DOCUMENT
# ============================================================

document = {
    "type": "excalidraw",
    "version": 2,
    "source": "https://excalidraw.com",
    "elements": elements,
    "appState": {
        "gridSize": None,
        "viewBackgroundColor": "#ffffff",
        "zoom": {
            "value": 1
        },
        "scrollX": 0,
        "scrollY": 0,
    },
    "files": {},
}


# ============================================================
# WRITE SEED.JSON
# ============================================================

OUTPUT_FILE.write_text(
    json.dumps(
        document,
        indent=2,
    ),
    encoding="utf-8",
)


# ============================================================
# OUTPUT
# ============================================================

print("=" * 60)
print("SEED GENERATED SUCCESSFULLY")
print("=" * 60)
print(f"Output file: {OUTPUT_FILE}")
print(f"Total elements: {len(elements)}")
print()
print("Initial elements:")
print("  1 × Large circle")
print("  4 × Long lines (900px)")
print("  1 × Triangle")
print("  1 × Circle")
print("  2 × Different-sized circles")
print("  1 × Rectangle")
print()
print("Total: 10 elements")
print("=" * 60)