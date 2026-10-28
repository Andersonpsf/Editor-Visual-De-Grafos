import math

def calculate_distance(x1, y1, x2, y2):
    """Esse método calcula a distância entre dois pontos no plano cartesiano (Teorema de Pitágoras)."""
    return math.hypot(x2 - x1, y2 - y1)

def point_to_segment_distance(px, py, x1, y1, x2, y2):
    """Calcula o quão perto o clique do mouse(px, py) está da aresta (x1, y1) - (x2, y2)."""
    if (x1 == x2) and (y1 == y2):
        return calculate_distance(px, py, x1, y1)

    # Calcula o comprimento da aresta ao quadrado
    lenght_squared = (x2-x1) ** 2 + (y2 - y1) ** 2

    projection = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / lenght_squared

    projection = max(0, min(1, projection))

    nearest_x = x1 + projection * (x2 - x1)
    nearest_y = y1 + projection * (y2 - y1)

    return calculate_distance(px, py, nearest_x, nearest_y)