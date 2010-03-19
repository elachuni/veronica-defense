import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyglet import image
from pyglet.gl import *
from pyglet import font

import cocos
from cocos.director import *
from cocos.menu import *
from cocos.scene import *
from cocos.layer import *

import actors
import const

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
        if self.selected == actors.Tower or self.mouse_x is None:
            return
        self.drag_object = TowerCreationLayer(actors.Tower, self, self.world, self.mouse_x, self.mouse_y)
        self.get_ancestor(cocos.scene.Scene).add(self.drag_object, z=10)
        self.selected = actors.Tower        

    def on_mouse_motion(self, x, y, dx, dy):
        Menu.on_mouse_motion(self, x, y, dx, dy)
        self.mouse_x, self.mouse_y = director.get_virtual_coordinates(x,y)

class TowerCreationLayer(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self, type, menu, world, x=0, y=0):
        super(TowerCreationLayer, self).__init__()
        self.type = type
        self.sprite = cocos.sprite.Sprite(self.type.__name__+'.png')
        self.sprite.scale = 0.5
        self.draging = (x,y)
        self.world = world
        self.menu = menu
        
        self.valid_layer = cocos.layer.ColorLayer(0,250,0,180, self.type.size*const.GRID, self.type.size*const.GRID)        
        self.invalid_layer = cocos.layer.ColorLayer(250,0,0,180, self.type.size*const.GRID, self.type.size*const.GRID)        
        self.add(self.valid_layer)
        self.valid_layer.visible = False
        self.add(self.invalid_layer)
        self.add(self.sprite)
        self.valid_layer.position = (self.draging[0]-self.type.size*const.GRID/2, self.draging[1]-self.type.size*const.GRID/2)
        self.invalid_layer.position = (self.draging[0]-self.type.size*const.GRID/2, self.draging[1]-self.type.size*const.GRID/2)
        self.sprite.position = self.draging

    def on_mouse_motion(self, x, y, dx, dy):
        self.draging = director.get_virtual_coordinates(x,y)
        valid_zone = self.world.is_space_free(self.draging)
        if valid_zone:
            self.valid_layer.visible = True
            self.invalid_layer.visible = False
            self.valid_layer.position = (self.draging[0]-self.type.size*const.GRID/2, self.draging[1]-self.type.size*const.GRID/2)
        else:
            self.invalid_layer.visible = True
            self.valid_layer.visible = False
            self.invalid_layer.position = (self.draging[0]-self.type.size*const.GRID/2, self.draging[1]-self.type.size*const.GRID/2)
        self.sprite.position = self.draging

    def on_mouse_press (self, x, y, buttons, modifiers):
        if buttons == pyglet.window.mouse.LEFT:
            added = self.world.add_tower_from_menu(x, y, self.type)
#            if added:
#                self.get_ancestor(cocos.scene.Scene).remove(self)
#                self.menu.selected = None

if __name__ == "__main__":
    pyglet.font.add_directory('.')

    class DummyWorld(cocos.layer.Layer):
        def __init__(self):
            super(DummyWorld, self).__init__()
        def is_space_free(self, pos):
            return True
        def add_tower_from_menu(self, *args, **kwargs):
            pass

    director.init( resizable=False)
    bg = cocos.layer.ColorLayer(255,255,255,255)
    world = DummyWorld()
    director.run(Scene(bg, HudLayer(world)))
