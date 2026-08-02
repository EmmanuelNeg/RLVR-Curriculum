"""Regenerate seed.json for yellow-circle-in-blue-box.

The seed shows a blue rectangle on the left and a yellow circle to the right,
outside the rectangle. The agent task is to move the circle inside the box.

Run:
    python3 curriculum/tasks/yellow-circle-in-blue-box/generator.py
"""

from pathlib import Path
import sys


# ============================================================
# Import curriculum helpers
# ============================================================

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))

from curriculum.seed_generator import SeedBuilder, rectangle, text


b = SeedBuilder()


# ============================================================
# 1. Define grouping boxes
# ============================================================

# The boxes are fixed in these positions.
# The grader should use these coordinates to identify them.
#
# Box 1: Synthesis
# Box 2: Decomposition
# Box 3: Single Displacement
# Box 4: Double Displacement

BOX_Y = 700
BOX_WIDTH = 350
BOX_HEIGHT = 250

BOXES = [
    {
        "x": 100,
        "label": "SYNTHESIS",
        "color": "#dbeafe",
    },
    {
        "x": 500,
        "label": "DECOMPOSITION",
        "color": "#dcfce7",
    },
    {
        "x": 900,
        "label": "SINGLE DISPLACEMENT",
        "color": "#fef3c7",
    },
    {
        "x": 1300,
        "label": "DOUBLE DISPLACEMENT",
        "color": "#f3e8ff",
    },
]


# ============================================================
# 2. Create the four grouping boxes
# ============================================================

for box in BOXES:

    # Create the colored grouping rectangle
    b.add(
        rectangle(
            box["x"],
            BOX_Y,
            BOX_WIDTH,
            BOX_HEIGHT,
            background_color=box["color"],
        )
    )

    # Add the category label above/inside the box
    b.add(
        text(
            box["x"] + 20,
            BOX_Y + 20,
            box["label"],
        )
    )


# ============================================================
# 3. Define the 12 chemical equations
# ============================================================

equations = [

    # --------------------------------------------------------
    # Synthesis
    # --------------------------------------------------------

    "2H₂ + O₂ → 2H₂O",
    "CaO + H₂O → Ca(OH)₂",
    "2Na + Cl₂ → 2NaCl",


    # --------------------------------------------------------
    # Decomposition
    # --------------------------------------------------------

    "CaCO₃ → CaO + CO₂",
    "2H₂O₂ → 2H₂O + O₂",
    "2KClO₃ → 2KCl + 3O₂",


    # --------------------------------------------------------
    # Single Displacement
    # --------------------------------------------------------

    "Zn + 2HCl → ZnCl₂ + H₂",
    "Fe + CuSO₄ → FeSO₄ + Cu",
    "2Al + 3CuCl₂ → 2AlCl₃ + 3Cu",


    # --------------------------------------------------------
    # Double Displacement
    # --------------------------------------------------------

    "AgNO₃ + NaCl → AgCl + NaNO₃",
    "BaCl₂ + Na₂SO₄ → BaSO₄ + 2NaCl",
    "HCl + NaOH → NaCl + H₂O",
]


# ============================================================
# 4. Initial positions of chemical equations
# ============================================================
#
# Equations are deliberately placed OUTSIDE the grouping
# boxes so that the initial seed fails the grader.
#
# The equations are scattered across the upper part
# of the canvas.
# ============================================================

positions = [
    (100, 100),
    (500, 100),
    (900, 100),
    (1300, 100),

    (100, 250),
    (500, 250),
    (900, 250),
    (1300, 250),

    (100, 400),
    (500, 400),
    (900, 400),
    (1300, 400),
]


# ============================================================
# 5. Add equations to the canvas
# ============================================================

for equation, (x, y) in zip(equations, positions):

    b.add(
        text(
            x,
            y,
            equation,
        )
    )


# ============================================================
# 6. Save the initial seed
# ============================================================

b.save(
    Path(__file__).parent / "seed.json"
)