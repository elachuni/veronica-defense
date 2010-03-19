#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cocos
from cocos.director import director
import pyglet

pyglet.resource.path.append("images")
pyglet.resource.reindex()


class const(object):
    GRID = 30


class GridLayer(cocos.layer.Layer):
    """
    a layer with the grid drawn, for testing purpouses
    """
    def __init__(self):
        super(GridLayer, self).__init__()
        grid = Grid(0, 0, const.WINDOW_W, const.WINDOW_H, (180, 180, 180, 50))
        self.add(grid)


class Grid(cocos.draw.Canvas):
    """Grid drawer"""
    def __init__(self, x, y, w, h, color=(0,0,0,255)):
        super(Grid, self).__init__()
        self.x = x
        self.y = y
        self.width = (w/const.GRID)*const.GRID
        self.height = (h/const.GRID)*const.GRID
        self.color = color

    def render(self):
        """Draw the grid on the map"""
        self.set_color(self.color)
        for h in range(self.y, self.height+const.GRID, const.GRID):
            self.move_to((self.x, h))
            self.line_to((self.width+self.x, h))

        self.set_color(self.color)
        for w in range(self.x, self.width+const.GRID, const.GRID):
            self.move_to((w, self.y))
            self.line_to((w, self.height+self.y))


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


class WorldLayer(cocos.layer.Layer):
    is_event_handler = True
    
    def __init__(self):
        super(WorldLayer, self).__init__()
        self.mapa = Mapa()

        t = Tower(self, 5, 5)
        self.mapa.add(t)
        
        t2 = Tower(self, 3, 2)
        self.mapa.add(t2)

        test_size = Tower.size * const.GRID
        self.test_layer = cocos.layer.ColorLayer(255, 255, 255, 55,
                            width=test_size, height=test_size)
        self.add(self.test_layer)
    
    def get_grid_from_point(self, x, y):
        return int(x / const.GRID), int(y / const.GRID)

    def on_mouse_motion(self, x, y, dx, dy):
        grid_pos = self.get_grid_from_point(x, y)
        is_empty = self.mapa.is_empty_at(grid_pos)
        can_fit_tower = self.mapa.can_fit_at(grid_pos, Tower.size)
        self.test_layer.position = grid_pos[0]*const.GRID, grid_pos[1]*const.GRID
        if not can_fit_tower:
            self.test_layer.color = 255, 0, 0
        else:
            self.test_layer.color = 0, 255, 0

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == pyglet.window.mouse.LEFT:
            grid_pos = self.get_grid_from_point(x, y)
            can_fit_tower = self.mapa.can_fit_at(grid_pos, Tower.size)
            if can_fit_tower:
                t = Tower(self, grid_pos[0], grid_pos[1])
                self.mapa.add(t)


class MapObject(object):
    """Object placed on the game map"""
    sprite_file = 'nothing.png'
    size = 1

    def __init__(self, world, grid_x, grid_y):
        self.world = world
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.deleted = False

    def remove(self):
        """Remove the object from the layer it belongs"""
        self.__class__.batch.remove(self.sprite)

    def get_layer(self):
        """Returns the layer this object's sprite should be added to"""
        return self.world

    def create_sprite(self):
        """Create the object's sprite"""
        # we create a batch for this type of map object
        if not hasattr(self.__class__, 'batch'):
            self.__class__.batch = cocos.batch.BatchNode()
            self.get_layer().add(self.__class__.batch)

        self.sprite = cocos.sprite.Sprite(self.sprite_file)
        self.sprite.x = (self.grid_x + self.size / 2.0) * const.GRID
        self.sprite.y = (self.grid_y + self.size / 2.0) * const.GRID
        # we add the sprite to the batch
        self.__class__.batch.add(self.sprite)


class Tower(MapObject):
    """Defender tower"""
    sprite_file = 'tower_base.png'
    size = 2

    def __init__(self, world, grid_x, grid_y):
        super(Tower, self).__init__(world, grid_x, grid_y)
        self.create_sprite()
        self.sprite.scale = 0.5
    

if __name__ == "__main__":
    director.init()
    const.WINDOW_W, const.WINDOW_H = director.get_window_size()
    sc = cocos.scene.Scene(GridLayer(), WorldLayer())
    director.run(sc)
