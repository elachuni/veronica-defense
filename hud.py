import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyglet import image
from pyglet.gl import *
from pyglet import font

import cocos
from cocos.director import director
from cocos.menu import Menu, ImageMenuItem, RIGHT, CENTER, \
     zoom_in, zoom_out

import actors
import const
from mapa import get_grid_from_point
from config import ADD_TOWER

pyglet.resource.path.append("images")
pyglet.resource.reindex()

class HudLayer(Menu):
    def __init__(self, world):
        super( HudLayer, self ).__init__()
        self.menu_halign = RIGHT
        self.menu_valign = CENTER
        self.selected = None
        self.world = world
        self.mouse_x, self.mouse_y = None, None

        items = []
        enemies = [actors.Tower]
        for i in enemies:
            item = ImageMenuItem('button'+i.__name__+'.png', 
                getattr(self, 'on_'+i.__name__+'_callback'))
            items.append(item)
        item = ImageMenuItem('button.png', self.on_Tower_callback)
        items.append(item)
        self.create_menu( items, selected_effect=zoom_in(), unselected_effect=zoom_out())

    def on_quit(self):
        pass

    def on_Tower_callback(self):
        if not self.world.resources.can_i_spend(ADD_TOWER):
            return
        
        if self.selected == actors.Tower or self.mouse_x is None:
            return
        self.drag_object = TowerCreationLayer(actors.Tower, self, self.world, self.mouse_x, self.mouse_y)
        self.get_ancestor(cocos.scene.Scene).add(self.drag_object, z=10)
        self.selected = actors.Tower        

    def on_mouse_motion(self, x, y, dx, dy):
        Menu.on_mouse_motion(self, x, y, dx, dy)
        self.mouse_x, self.mouse_y = director.get_virtual_coordinates(x,y)

    def end_drag(self):
        self.get_ancestor(cocos.scene.Scene).remove(self.drag_object)
        self.selected = None

class TowerCreationLayer(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self, object_class, menu, world, x=0, y=0):
        super(TowerCreationLayer, self).__init__()
        self.object_class = object_class
        self.draging = (x,y)
        self.world = world
        self.menu = menu

        # a rect to indicate the object's possible position:
        self.rect_size_w = self.object_class.size * const.GRID
        self.rect_size_h = self.object_class.size * const.GRID
        self.rect_layer = cocos.layer.ColorLayer(0,250,0,55,
                                self.rect_size_w, self.rect_size_h)
        
        grid_pos = get_grid_from_point(self.draging[0], self.draging[1])
        self.rect_layer.position = (grid_pos[0]*const.GRID,
                                    grid_pos[1]*const.GRID)
        self.add(self.rect_layer)

        # dragging sprite of the map object:
        self.sprite = cocos.sprite.Sprite(self.object_class.__name__+'.png')
        self.sprite.scale = 0.5
        self.sprite.position = self.draging
        self.add(self.sprite)

    def on_mouse_motion(self, x, y, dx, dy):
        self.draging = director.get_virtual_coordinates(x,y)
        grid_pos = get_grid_from_point(self.draging[0], self.draging[1])
        can_fit = self.world.mapa.can_fit_at(grid_pos, self.object_class)
        self.rect_layer.position = grid_pos[0]*const.GRID, grid_pos[1]*const.GRID
        if can_fit:
            self.rect_layer.color = 0, 255, 0
        else:
            self.rect_layer.color = 255, 0, 0
            
        self.sprite.position = self.draging

    def on_mouse_press (self, x, y, buttons, modifiers):
        if buttons == pyglet.window.mouse.LEFT:
            grid_pos = get_grid_from_point(self.draging[0], self.draging[1])
            can_fit = self.world.mapa.can_fit_at(grid_pos, self.object_class)
            if can_fit:
                self.world.add_object(grid_pos[0], grid_pos[1],
                                      self.object_class)
                self.menu.end_drag()


if __name__ == "__main__":
    pyglet.font.add_directory('.')
    from mapa import Mapa

    class DummyWorld(cocos.layer.Layer):
        def __init__(self):
            super(DummyWorld, self).__init__()
            self.mapa = Mapa()
        def add_object(self, *args, **kwargs):
            pass

    director.init( resizable=False)
    bg = cocos.layer.ColorLayer(255,255,255,255)
    world = DummyWorld()
    director.run(cocos.scene.Scene(bg, HudLayer(world)))
