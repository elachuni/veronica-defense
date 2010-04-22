import sys
import os

from pyglet.gl import *

from cocos.scene import Scene
from cocos.layer import Layer, ColorLayer
from cocos.sprite import Sprite
from cocos.director import director

from cocos.menu import Menu, ImageMenuItem, LEFT, CENTER, \
     zoom_in, zoom_out

from veronica_logic import CommonTower, HardTower

from utils import get_cell_from_point
from settings import GRID_CELL, GRID_SIZE

# FIXME silly images until we get some graphics:
images_for_sprites = {
    CommonTower: 'common_tower_head.png',
    HardTower: 'hard_tower_head.png',
    }


class HudLayer(Menu):
    def __init__(self, level):
        super(HudLayer, self).__init__()
        self.level = level
        
        # configure the menu:
        self.menu_halign = LEFT
        self.menu_valign = CENTER
        self.selected = None
        self.mouse_x, self.mouse_y = None, None
        
        items = []
        towers = [CommonTower, HardTower]
        for tower in towers:
            item = ImageMenuItem(images_for_sprites[tower], 
                                 getattr(self, 'on_tower_callback'),
                                 tower)
            items.append(item)
        
        self.create_menu(items, selected_effect=zoom_in(),
                         unselected_effect=zoom_out())
    
    def on_quit(self):
        pass
    
    def on_tower_callback(self, tower_class):
        # check if the operation can be done
        if not self.level.resources.can_be_done("add tower"):
            return
        
        # mark this tower as selected and drag a sprite:
        if self.selected == tower_class or self.mouse_x is None:
            return
        self.drag_object = TowerCreationLayer(tower_class,
                                              self,
                                              self.mouse_x,
                                              self.mouse_y)
        
        self.get_ancestor(Scene).add(self.drag_object, z=10)
        self.selected = tower_class        
    
    def on_mouse_motion(self, x, y, dx, dy):
        Menu.on_mouse_motion(self, x, y, dx, dy)
        self.mouse_x, self.mouse_y = director.get_virtual_coordinates(x,y)
    
    def end_drag(self):
        self.get_ancestor(Scene).remove(self.drag_object)
        self.selected = None

class TowerCreationLayer(Layer):
    is_event_handler = True
    
    def __init__(self, tower_class, menu, x=0, y=0):
        super(TowerCreationLayer, self).__init__()
        self.tower_class = tower_class
        self.menu = menu
        self.draging = (x,y)

        # a rect to indicate the object's possible position:
        self.rect_size_w = self.tower_class.size[0] * GRID_CELL
        self.rect_size_h = self.tower_class.size[1] * GRID_CELL
        self.rect_layer = ColorLayer(0,250,0,55,
                                self.rect_size_w, self.rect_size_h)
        
        grid_pos = get_cell_from_point(self.draging[0], self.draging[1])
        self.rect_layer.position = (grid_pos[0]*GRID_CELL,
                                    grid_pos[1]*GRID_CELL)
        self.add(self.rect_layer)
        
        # dragging sprite of the map object:
        self.sprite = Sprite(images_for_sprites[tower_class])
        self.sprite.scale = 0.5
        self.sprite.position = self.draging
        self.add(self.sprite)
    
    def on_mouse_motion(self, x, y, dx, dy):
        self.draging = director.get_virtual_coordinates(x,y)
        grid_pos = get_cell_from_point(self.draging[0], self.draging[1])
        
        # TODO this call is ugly, so loong:
        is_out = self.menu.level.world.grid.is_out_at(self.tower_class, grid_pos)
        if is_out:
            self.rect_layer.visible = False
        else:
            self.rect_layer.visible = True
        
        # TODO this call is ugly, so loong:
        can_fit = self.menu.level.world.grid.can_fit_at(self.tower_class, grid_pos)
        self.rect_layer.position = (grid_pos[0]*GRID_CELL,
                                    grid_pos[1]*GRID_CELL)
        if can_fit:
            self.rect_layer.color = 0, 255, 0
        else:
            self.rect_layer.color = 255, 0, 0
            
        self.sprite.position = self.draging
    
    def on_mouse_press (self, x, y, buttons, modifiers):
        if buttons == pyglet.window.mouse.LEFT:
            grid_pos = get_cell_from_point(self.draging[0], self.draging[1])
            can_fit = self.menu.level.world.grid.can_fit_at(self.tower_class,
                                                            grid_pos)
            if can_fit:
                self.menu.level.add_tower(self.tower_class, grid_pos)
                self.menu.end_drag()


if __name__ == "__main__":
    import pyglet
    pyglet.resource.path.append("images")
    pyglet.resource.reindex()
    
    import settings
    from logic import World
    
    class DummyWorldLayer(Layer):
        def __init__(self, world):
            super(DummyWorldLayer, self).__init__()
            hud_layer = HudLayer(world)
            self.add(hud_layer)

    world = World(grid_size=settings.GRID_SIZE)
    
    director.init( resizable=False)
    bg = ColorLayer(255,255,255,255)
    world_layer = DummyWorldLayer(world)
    director.run(Scene(bg, world_layer))
