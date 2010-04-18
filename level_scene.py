
import random

from cocos.layer import ColorLayer, Layer
from cocos.scene import Scene
from cocos.sprite import Sprite
from cocos.director import director

from pyglet.window import mouse, key

from veronica_logic import Tower
from sprites import WorldSprite, TowerSprite, CommonTowerSprite, \
     HardTowerSprite, EnemySprite, CommonEnemySprite, FastEnemySprite, \
     HqSprite, all_sprites, InfoSprite

from split_layer import SplitLayer, split_horizontal, split_vertical

import settings


# which sprite represents which world object
sprite_per_object = {}
for sprite in all_sprites:
    sprite_per_object[sprite.world_object_class] = sprite


def get_cell_from_point(x, y):
    """
    return the grid cell at the given point
    """
    return int(x / settings.GRID_CELL), int(y / settings.GRID_CELL)


class BackgroundLayer(ColorLayer):
    def __init__(self):
        super(BackgroundLayer, self).__init__(255, 255, 255, 255)
        
        # wall tile (120 x 120 px):
        for i in range(0, settings.WINDOW_SIZE[0], 120):
            for j in range(0, settings.WINDOW_SIZE[1], 120):
                wall_tile = Sprite('wall.png')
                wall_tile.x = wall_tile.image.width / 2 + i
                wall_tile.y = wall_tile.image.height / 2 + j
                self.add(wall_tile)


class ControlLayer(Layer):
    is_event_handler = True
    
    def __init__(self, level):
        super(ControlLayer, self).__init__()
        self.level = level
    
    def on_mouse_press(self, x, y, buttons, modifiers):
        grid_cell = get_cell_from_point(x, y)
        
        if buttons == mouse.RIGHT:
            world_obj = self.level.world.grid.get_at(grid_cell)
            # remove tower:
            if world_obj is not None and isinstance(world_obj, Tower):
                self.level.remove_tower(world_obj)
        
        elif buttons == mouse.LEFT:
            world_obj = self.level.world.grid.get_at(grid_cell)
            # activate or deactivate tower:
            if world_obj is not None and isinstance(world_obj, Tower):
                self.level.world.activate_tower(world_obj)
            else:
                self.level.world.deactivate_tower()


class WorldLayer(SplitLayer):
    """
    the objects in the world
    """
    def __init__(self, split_data, world):
        super(WorldLayer, self).__init__(split_data)
        
        self.world = world
        world.add_listener(self)
        
        self.towers_layer = Layer()
        self.enemies_layer = Layer()
        self.shots_layer = Layer()
        self.add(self.towers_layer, z=0)
        self.add(self.enemies_layer, z=1)
        self.add(self.shots_layer, z=2)
        
        self.layers_per_sprites = {
            TowerSprite: self.towers_layer,
            EnemySprite: self.enemies_layer,
            }
        
        self.schedule_interval(world.update, 1.0/settings.FPS)
    
    def make_sprite(self, sprite_class, world_obj, *args, **kwargs):
        """
        make a sprite that represents the world object and add it to
        the corresponding layer.
        """
        sprite = sprite_class(world_obj, *args, **kwargs)
        
        layer = self
        for sp_class, sp_layer in self.layers_per_sprites.items():
            if isinstance(sprite, sp_class):
                layer = sp_layer
                break
        
        layer.add(sprite)
    
    def on_add(self, world, world_obj, grid_pos):
        """
        when an object is added to the world, a sprite is generated
        for it.
        """
        sprite_class = sprite_per_object[world_obj.__class__]
        
        kwargs = {}
        if isinstance(world_obj, Tower):
            kwargs['shots_layer'] = self.shots_layer
        
        self.make_sprite(sprite_class, world_obj, **kwargs)
    
    def on_remove(self, world, *args):
        pass #print "remove!"


class InfoLayer(SplitLayer):
    """
    information on screen
    """
    def __init__(self, split_data):
        super(InfoLayer, self).__init__(split_data, color=(0, 0, 0, 200))

    def setup(self, hq, resources):
        info_sprite = InfoSprite(hq, resources)
        self.add(info_sprite)


class LevelScene(Scene):
    def __init__(self, level):
        super(LevelScene, self).__init__()
        
        # the scene will listen to the level:
        level.add_listener(self)

        # split the window in three areas:
        #  world, hud, and info
        
        window_split = {'position': (0, 0), 'size': settings.WINDOW_SIZE}
        
        split = settings.WINDOW_SIZE[0] * 3/4
        world_split, rest_split = split_horizontal(window_split, split)
        
        split = settings.INFO_HEIGHT
        info_split, hud_split = split_vertical(rest_split, split)
        
        bg_layer = BackgroundLayer()
        
        world_layer = WorldLayer(world_split, level.world)
        hud_layer = SplitLayer(hud_split, color=(0, 0, 0, 100)) # TODO
        info_layer = InfoLayer(info_split)
        
        control_layer = ControlLayer(level)
        
        self.add(bg_layer, z=0)
        self.add(world_layer, z=1)
        self.add(hud_layer, z=2)
        self.add(info_layer, z=3)
        self.add(control_layer, z=4)
        
        self.schedule_interval(level.spawn_enemy, settings.SPAWN_SECS)
        level.start()
        
        info_layer.setup(level.world.hq, level.resources)
    
    def on_stop_spawning(self, level, *args):
        self.unschedule(level.spawn_enemy)

