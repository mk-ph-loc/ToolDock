"""Γεωμετρία παραθύρου σε συντεταγμένες Qt, χωρίς εξάρτηση από GUI."""

def place(bounds: tuple[int, int, int, int], size: tuple[int, int],
          position: tuple[int, int], dock: str) -> tuple[int, int, int, int]:
    """Περιορισμός ολόκληρου του πλαισίου σε μία οθόνη."""
    left, top, width, height = bounds
    w, h = min(size[0], width), min(size[1], height)
    x, y = position
    if dock == "left": x = left
    elif dock == "right": x = left + width - w
    elif dock == "top": y = top
    elif dock == "bottom": y = top + height - h
    x = max(left, min(x, left + width - w))
    y = max(top, min(y, top + height - h))
    return x, y, w, h
