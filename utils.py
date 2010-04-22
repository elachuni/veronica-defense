
from settings import GRID_CELL


def angle_difference(alpha, beta):
    return abs(alpha % 360 - beta % 360)


def get_cell_from_point(x, y):
    """
    return the grid cell at the given point
    
    this is relative to the WorldLayer
    """
    return int(x / GRID_CELL), int(y / GRID_CELL)
