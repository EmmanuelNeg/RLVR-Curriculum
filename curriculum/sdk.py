"""sdk.py — Excalidraw grading helpers."""

from __future__ import annotations

from typing import Any


class ExcalidrawElement:
    """Wrapper around an Excalidraw element."""

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def type(self) -> str:
        return self._data.get("type", "")

    @property
    def id(self) -> str:
        return self._data.get("id", "")

    @property
    def x(self) -> float:
        return self._data.get("x", 0)

    @property
    def y(self) -> float:
        return self._data.get("y", 0)

    @property
    def width(self) -> float:
        return self._data.get("width", 0)

    @property
    def height(self) -> float:
        return self._data.get("height", 0)

    @property
    def background_color(self) -> str:
        return self._data.get("backgroundColor", "")

    @property
    def stroke_color(self) -> str:
        return self._data.get("strokeColor", "")
    
    # Here, I added a text property to be useind in the grader.py
    @property
    def text(self) -> str:
        return self._data.get("text", "")
    
    # Here I extended the sdk to read precise points for lines.
    @property
    def points(self) -> list[list[float]]:
        return self._data.get("points", [])
    
    # Here i extended the sdk to have a center property 
    @property
    def center(self) -> tuple[float, float]:
        return (
            self.x + self.width / 2,
            self.y + self.height / 2,
        )
        
     # distance to...    
    def distance_to(self, other: "ExcalidrawElement") -> float:
        x1, y1 = self.center
        x2, y2 = other.center
        
        return (
            (x2 - x1) ** 2 +
            (y2 - y1) ** 2
        ) ** 0.5
        
   # sdk Extension... is_near
    def is_near(
        self, 
        other:"ExcalidrawElement",
        tolerance: float = 100,
    ) -> bool: 
        return self.distance_to(other) <= tolerance

    def is_rectangle(self) -> bool:
        return self.type == "rectangle"

    def is_ellipse(self) -> bool:
        return self.type == "ellipse"
    
    # Here i added the function to teach the sdk text basically is...
    def is_text(self) -> bool:
        return self.type == "text"
    
    # extending the sdk to read lines ******
    def is_line(self) -> bool:
        return self.type == "line"
    
    # extending the sdk to read freedraw
    def is_freedraw(self) -> bool:
        return self.type == "freedraw"

    def has_background_color(self, hex_color: str) -> bool:
        return self.background_color.lower() == hex_color.lower()

    def is_within(self, other: "ExcalidrawElement") -> bool:
        """Return True if this element is fully contained within other."""
        return (
            self.x >= other.x
            and self.y >= other.y
            and self.x + self.width <= other.x + other.width
            and self.y + self.height <= other.y + other.height
        )


class ExcalidrawProject:
    """Wrapper for an Excalidraw project snapshot."""

    def __init__(self, data: dict[str, Any]):
        self._elements = [
            ExcalidrawElement(el)
            for el in data.get("elements", [])
            if not el.get("isDeleted", False)
        ]

    def get_rectangles(self) -> list[ExcalidrawElement]:
        return [el for el in self._elements if el.is_rectangle()]

    def get_ellipses(self) -> list[ExcalidrawElement]:
        return [el for el in self._elements if el.is_ellipse()]
    
    #Added this function to enable get_texts()
    def get_texts(self) -> list[ExcalidrawElement]:
        #basically returns all text elements in the project
        return [el for el in self._elements if el.is_text()]
    
    # Added this function to enable get_lines()
    def get_lines(self) -> list[ExcalidrawElement]:
        return [el for el in self._elements if el.is_line()]
       
    # Added this function to enable get_freedraws()
    # This will give the grader access to everthing drawn with the pen tool
    def get_freedraws(self) -> list[ExcalidrawElement]:
        return [el for el in self._elements if el.is_freedraw()]
