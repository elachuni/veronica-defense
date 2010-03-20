
"""
Mapa that stores the grid positions of the objects
"""

import cocos
from cocos.director import director
import pyglet

import const


pyglet.resource.path.append("images")
pyglet.resource.reindex()


class Mapa(object):
    def __init__(self):
        # stores the grid positions for every object in the mapa:
        self._mapa = {}

    def add(self, map_object):
        for i in range(map_object.size):
            for j in range(map_object.size):
                grid_pos = map_object.grid_x+i, map_object.grid_y+j
                self._mapa[grid_pos] = map_object

    def is_empty_at(self, grid_pos):
        return grid_pos not in self._mapa

    def can_fit_at(self, grid_pos, size):
        for i in range(size):
            for j in range(size):
                test_grid_pos = grid_pos[0]+i, grid_pos[1]+j
                if not self.is_empty_at(test_grid_pos):
                    return False
        return True


def get_grid_from_point(x, y):
    return int(x / const.GRID), int(y / const.GRID)


if __name__ == "__main__":
    from play_scene import GridLayer
    from actors import Tower
    
    class WorldLayer(cocos.layer.Layer):
        is_event_handler = True

        def __init__(self):
            super(WorldLayer, self).__init__()
            self.mapa = Mapa()

            self.towers_layer = cocos.layer.Layer()
            self.add(self.towers_layer)

            t = Tower(self, 5, 5)
            t2 = Tower(self, 3, 2)

            test_size = Tower.size * const.GRID
            self.test_layer = cocos.layer.ColorLayer(255, 255, 255, 55,
                                width=test_size, height=test_size)
            self.add(self.test_layer)

        def on_mouse_motion(self, x, y, dx, dy):
            grid_pos = get_grid_from_point(x, y)
            is_empty = self.mapa.is_empty_at(grid_pos)
            can_fit_tower = self.mapa.can_fit_at(grid_pos, Tower.size)
            self.test_layer.position = grid_pos[0]*const.GRID, grid_pos[1]*const.GRID
            if not can_fit_tower:
                self.test_layer.color = 255, 0, 0
            else:
                self.test_layer.color = 0, 255, 0

        def on_mouse_press(self, x, y, buttons, modifiers):
            if buttons == pyglet.window.mouse.LEFT:
                grid_pos = get_grid_from_point(x, y)
                can_fit_tower = self.mapa.can_fit_at(grid_pos, Tower.size)
                if can_fit_tower:
                    t = Tower(self, grid_pos[0], grid_pos[1])
                    self.mapa.add(t)

    
    director.init()
    const.WINDOW_W, const.WINDOW_H = director.get_window_size()
    sc = cocos.scene.Scene(GridLayer(), WorldLayer())
    director.run(sc)
