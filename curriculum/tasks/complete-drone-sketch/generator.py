import json
import uuid
from pathlib import Path


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def make_id():
    """Generate a unique Excalidraw element ID."""
    return str(uuid.uuid4()).replace("-", "")[:20]


def base_element(
    element_type,
    x,
    y,
    width,
    height,
    stroke_color="#1e1e1e",
    background_color="transparent",
):
    """Create common Excalidraw element properties."""

    return {
        "id": make_id(),
        "type": element_type,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "angle": 0,
        "strokeColor": stroke_color,
        "backgroundColor": background_color,
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "index": None,
        "roundness": None,
        "seed": 1,
        "version": 1,
        "versionNonce": 1,
        "isDeleted": False,
        "boundElements": [],
        "updated": 1,
        "link": None,
        "locked": False,
    }


# ---------------------------------------------------------
# Rectangle
# ---------------------------------------------------------

def rectangle(
    x,
    y,
    width,
    height,
    background_color="transparent",
    stroke_color="#1e1e1e",
    roundness=True,
):
    element = base_element(
        "rectangle",
        x,
        y,
        width,
        height,
        stroke_color,
        background_color,
    )

    if roundness:
        element["roundness"] = {
            "type": 3,
        }

    return element


# ---------------------------------------------------------
# Ellipse
# ---------------------------------------------------------

def ellipse(
    x,
    y,
    width,
    height,
    background_color="#d3d3d3",
    stroke_color="#1e1e1e",
):
    return base_element(
        "ellipse",
        x,
        y,
        width,
        height,
        stroke_color,
        background_color,
    )


# ---------------------------------------------------------
# Line
# ---------------------------------------------------------

def line(
    x,
    y,
    points,
    stroke_color="#1e1e1e",
    stroke_width=2,
):
    """
    Create an Excalidraw line.

    x/y are the line origin.
    points contain coordinates relative to x/y.
    """

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]

    width = max(xs) - min(xs)
    height = max(ys) - min(ys)

    element = base_element(
        "line",
        x,
        y,
        width,
        height,
        stroke_color,
        "transparent",
    )

    element["points"] = points
    element["strokeWidth"] = stroke_width
    element["roundness"] = {
        "type": 2,
    }

    return element


# ---------------------------------------------------------
# Create drone seed
# ---------------------------------------------------------

def create_seed():
    elements = []

    # =====================================================
    # 1. CENTRAL DRONE BODY
    # =====================================================

    body = rectangle(
        x=600,
        y=300,
        width=220,
        height=110,
        background_color="#f8f9fa",
        stroke_color="#1e1e1e",
        roundness=True,
    )

    elements.append(body)


    # =====================================================
    # 2. FOUR DRONE ARMS
    # =====================================================

    # Top-left arm
    elements.append(
        line(
            x=620,
            y=320,
            points=[
                [0, 0],
                [-220, -130],
            ],
        )
    )

    # Top-right arm
    elements.append(
        line(
            x=800,
            y=320,
            points=[
                [0, 0],
                [220, -130],
            ]
        )
    )

    # Bottom-left arm
    elements.append(
        line(
            x=620,
            y=390,
            points=[
                [0, 0],
                [-220, 130],
            ]
        )
    )

    # Bottom-right arm
    elements.append(
        line(
            x=800,
            y=390,
            points=[
                [0, 0],
                [220, 130],
            ]
        )
    )


    # =====================================================
    # 3. FOUR MOTORS
    # =====================================================

    motor_size = 32

    # Top-left motor
    elements.append(
        ellipse(
            x=384,
            y=174,
            width=motor_size,
            height=motor_size,
            background_color="#d3d3d3",
        )
    )

    # Top-right motor
    elements.append(
        ellipse(
            x=1000,
            y=174,
            width=motor_size,
            height=motor_size,
            background_color="#d3d3d3",
        )
    )

    # Bottom-left motor
    elements.append(
        ellipse(
            x=384,
            y=504,
            width=motor_size,
            height=motor_size,
            background_color="#d3d3d3",
        )
    )

    # Bottom-right motor
    elements.append(
        ellipse(
            x=1000,
            y=504,
            width=motor_size,
            height=motor_size,
            background_color="#d3d3d3",
        )
    )


    # =====================================================
    # 4. YELLOW LANDING PAD
    # =====================================================

    landing_pad = rectangle(
        x=560,
        y=700,
        width=300,
        height=120,
        background_color="#ffec99",
        stroke_color="#f08c00",
        roundness=True,
    )

    elements.append(landing_pad)


    # =====================================================
    # CREATE EXCALIDRAW DOCUMENT
    # =====================================================

    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {
            "gridSize": None,
            "viewBackgroundColor": "#ffffff",
        },
        "files": {},
    }


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    seed = create_seed()

    output_path = Path(__file__).parent / "seed.json"

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            seed,
            f,
            indent=2,
        )

    print(f"Seed generated successfully: {output_path}")
    print(f"Total elements: {len(seed['elements'])}")

    print("\nElement summary:")

    for element in seed["elements"]:
        print(
            f"  {element['type']:10} "
            f"id={element['id']}"
        )