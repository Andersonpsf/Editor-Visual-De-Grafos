class Vertex:
    def __init__(self, v_id, label, x, y, radius=20):
        self.id = v_id
        self.label = label
        self.x = x
        self.y = y
        self.radius = radius

class Edge:
    def __init__(self, source, target, weight="1", directed=False):
        self.source = source
        self.target = target
        self.weight = str(weight)
        self.directed = directed