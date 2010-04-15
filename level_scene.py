
import random

from cocos.layer import ColorLayer, Layer
from cocos.scene import Scene
from cocos.sprite import Sprite
from cocos.director import director

from pyglet.window import mouse, key

from veronica_logic import *
from sprites import WorldSprite, TowerSprite, CommonTowerSprite, \
     HardTowerSprite, EnemySprite, CommonEnemySprite, FastEnemySprite, \
     HqSprite, all_sprites

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


class WorldLayer(Layer):
    """
    the objects in the world
    """
    is_event_handler = True
    
    def __init__(self, level_data):
        super(WorldLayer, self).__init__()
        
        self.world = World(grid_size=settings.GRID_SIZE)
        
        self.resource_manager = ResourceManager(1000)
        
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
        
        # test world object:
        grid_pos = (settings.GRID_SIZE[0]/2 - 2, 5)
        self.add_world_object(WorldObject, grid_pos)
        
        # the hq:
        grid_pos = (10, 14)
        self.add_world_object(Hq, grid_pos)
        
        # some towers:
        for tower_class, positions in level_data['initial towers'].items():
            for pos in positions:
                sprite_class = sprite_per_object[tower_class]
                self.add_tower(tower_class, pos)
        
        # some enemies:
        self.enemies_to_spawn = []
        for enemy_class, number in level_data['enemies'].items():
            self.enemies_to_spawn.append((enemy_class, number))
        self.enemies_to_spawn.reverse()
        
        self.world.calculate_paths()
        
        self.schedule_interval(self.update, 1.0/settings.FPS)
        self.schedule_interval(self.spawn_enemy, settings.SPAWN_SECS)
    
    def update(self, dt):
        self.world.update()
    
    def spawn_enemy(self, dt):
        enemy_class, num = self.enemies_to_spawn[0]
        num -= 1
        if num == 0:
            self.enemies_to_spawn.pop(0)
            if len(self.enemies_to_spawn) == 0:
                self.unschedule(self.spawn_enemy)
        else:
            self.enemies_to_spawn[0] = enemy_class, num
        
        pos = (10 + random.randint(-8, 8), 0)
        self.add_world_object(enemy_class, pos)
        
        #enemy.start_move()
    
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
    
    def add_world_object(self, world_object_class, grid_pos,
                         *args, **kwargs):
        """
        glue method to make a world object, make a sprite for it, and add
        it to the world.
        """
        sprite_class = sprite_per_object[world_object_class]
        world_obj = world_object_class()
        self.make_sprite(sprite_class, world_obj, *args, **kwargs)
        self.world.add(world_obj, grid_pos)
    
    def add_tower(self, tower_class, grid_pos):
        assert issubclass(tower_class, Tower)
        
        self.add_world_object(tower_class, grid_pos,
                              shots_layer=self.shots_layer)
        self.resource_manager.operate('add tower')
    
    def on_mouse_press(self, x, y, buttons, modifiers):
        grid_cell = get_cell_from_point(x, y)
        
        if buttons == mouse.RIGHT:
            # remove tower:
            world_obj = self.world.grid.get_at(grid_cell)
            if world_obj is not None and isinstance(world_obj, Tower):
                self.world.remove(world_obj)
                #resource_manager.operate('remove tower')
        
        elif buttons == mouse.LEFT:
            # select tower:
            world_obj = self.world.grid.get_at(grid_cell)
            if world_obj is not None and isinstance(world_obj, Tower):
                self.world.activate_tower(world_obj)
            else:
                self.world.deactivate_tower()
    
#     def on_key_press(self, k, m):
#         if k == key.ESCAPE:
#             director.pop()


class LevelScene(Scene):
    def __init__(self, level_data):
        super(LevelScene, self).__init__()
        bg_layer = BackgroundLayer()
        world_layer = WorldLayer(level_data)
        
        self.add(bg_layer, z=0)
        self.add(world_layer, z=1)
