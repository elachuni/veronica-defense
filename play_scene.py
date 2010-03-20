
"""
The in-game scene
"""

import random
import time

import pyglet
import cocos
from cocos.director import director

from pyglet.window import key

import const

import levels
import enemies
from mapa import Mapa

import hud
from actors import Tower, HQ, Enemy
from config import prices_table, ADD_TOWER, INITIAL_BALANCE

class GridLayer(cocos.layer.Layer):
    """
    a layer with the grid drawn, for testing purpouses
    """
    is_event_handler = True     #: enable pyglet's events
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


class WorldLayer(cocos.layer.Layer):
    """World"""
    is_event_handler = True
    def __init__(self):
        super(WorldLayer, self).__init__()
        
        self.mapa = Mapa()
        
        self.sights_layer = cocos.layer.Layer()
        self.enemies_layer = cocos.layer.Layer()
        self.towers_layer = cocos.layer.Layer()
        self.shots_layer = cocos.layer.Layer()
        self.fx_layer = cocos.layer.Layer()
        
        self.add(self.sights_layer, z = 0)
        self.add(self.enemies_layer, z = 1)
        self.add(self.towers_layer, z = 2)
        self.add(self.shots_layer, z = 3)
        self.add(self.fx_layer, z = 4)
        
        # one HQ:
        self.hq = HQ(self, const.GRID_LEN_X / 2, const.GRID_LEN_Y - 2)
        
        # one resource manager
        self.resources = ResourceManager(self, INITIAL_BALANCE)
        
        self.towers = []
        
        # some towers:
        tower_init_data = ((const.GRID_LEN_X/2, 2),
                      (const.GRID_LEN_X/2, 6),
                      (const.GRID_LEN_X/2, 10),)
        for grid_x, grid_y in tower_init_data:
            tower = Tower(self, grid_x, grid_y)
            self.towers.append(tower)
            self.mapa.add(tower)
        
        # Everything collideable on the map, calculate paths
        self.calculate_paths()
        
        self.enemies = []
        #still no shots
        self.shots = []
        self.impacts = []
        self.schedule(self.update_world)
        self.schedule_interval(self.enemy_spawner, 1)
        
        self.level_loader()
    
    def calculate_paths(self):
        """Calculate the paths to the HG (for the enemies)"""
        self.paths = [[None] * const.GRID_LEN_X
                      for x in range(const.GRID_LEN_Y)]
        dirs = [(-1, 0), (0, -1), (1, 0), (0, 1),]
        target = (self.hq.grid_x, self.hq.grid_y)
        collideable = self.mapa.get_filled_positions()
        q = [target]
        while len(q):
            pos = q.pop(0)
            if pos in collideable:
                continue
            for d in dirs:
                newx = pos[0] - d[0]
                newy = pos[1] - d[1]
                if not ((0 <= newx < const.GRID_LEN_X) and (0 <= newy < const.GRID_LEN_Y)):
                    continue
                if self.paths[newy][newx] is None:
                    self.paths[newy][newx] = d
                    q.append((newx, newy))
    
    def update_world(self, dt):
        """Update the game state"""
        updatables = self.towers + self.enemies + \
                     self.shots + self.impacts
        
        for obj in updatables:
            obj.update()

    def on_mouse_press (self, x, y, buttons, modifiers):
        """This function is called when any mouse button is pressed

        (x, y) are the physical coordinates of the mouse
        'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
        'modifiers' is a bitwise or of pyglet.window.key modifier constants
            (values like 'SHIFT', 'OPTION', 'ALT')
        """
        # lets calculate grid x, y
        gx,gy = map(lambda i:int(round(float(i)/const.GRID))-1,(x,y))
        if buttons == pyglet.window.mouse.RIGHT:
            if (gx, gy) in self.towers:
                tower = self.towers.pop((gx, gy))
                tower.remove()
                self.resources.save(ADD_TOWER, 0.5)
                self.calculate_paths()
    
    def on_key_press(self, k, m):
        """When the user press a key"""
        if k == key.ESCAPE:
            director.pop()
    
    def add_object(self, grid_x, grid_y, object_class):
        """Add an object to the world of class object_class"""
        obj = object_class(self, grid_x, grid_y)
        self.towers.append(obj) # TODO assumming tower but can change
                                # in the future
        self.mapa.add(obj)
        
        # calculate resources:
        self.resources.spend(ADD_TOWER) # TODO assumming tower but can
                                        # change in the future
        self.resources.update_counter()
        self.calculate_paths()
        
        if not self.resources.can_i_spend(ADD_TOWER):
            # TODO: deactivate menu and cancel object dragging
            pass
    
    def level_loader(self, level='1'):
        """Load a level from a template"""
        self.level = levels.level[level]

        self.level_enemies = []
        for wave in self.level['enemies']:
            self.wave_enemies = []
            for key in wave:
                self.wave_enemies += [key] * wave[key]
            random.shuffle(self.wave_enemies)
            self.level_enemies += self.wave_enemies
    
    def enemy_spawner(self, dt):
        """Spawn an enemy"""
        if self.level_enemies:
            enemy = self.level_enemies.pop(0)
            template = enemies.enemy[enemy]
        else:
            return
        y = 0
        x = (const.GRID_LEN_X/2 + random.randint(-10, 10))
        enemy = Enemy(self, x, y, template=template)
    
    def game_over(self, dt):
        """Handles game over"""
        self.unschedule(self.update_world)
        self.unschedule(self.enemy_spawner)
        game_over_text = cocos.text.Label("Game Over",
                                          font_size=40,
                                          color=(255,0,0,255))
        game_over_text.position = 200, 200
        self.add(game_over_text, z=0)
        self.game_over_t = time.time()
        self.schedule(self.exit)
    
    def exit(self, dt):
        """Exit the game"""
        if time.time() - self.game_over_t > 3:
            director.pop()
    
    def is_space_free(self, pos):
        return True

class ResourceManager(object):
    """Player's resource manager"""
    def __init__(self, world, balance=0):
        self.balance = balance
        self.world = world
        self.prices_table = prices_table
        
        # resource counter on screen
        self.resource_counter = cocos.text.Label("",
                                                 font_size=20,
                                                 color=(0,200,0,255))
        self.resource_counter.position = 10, 10
        self.world.add(self.resource_counter, z=0)
        self.update_counter()
    
    def can_i_spend(self, action):
        """Determine if player can spend resources"""
        return (action in self.prices_table and
                self.prices_table[action] <= self.balance)
    
    def spend(self, action):
        """Spend resources"""
        assert(self.can_i_spend(action))
        self.balance -= self.prices_table[action]
        self.update_counter()
    
    def save(self, action, mult):
        """Earn resources FIXME"""
        self.balance += int(round(self.prices_table[action] * mult))
        self.update_counter()
    
    def update_counter(self):
        """Update grafic resources counter"""
        self.resource_counter.element.text = "recursos: %s" % self.balance
    
    def process_reward(self, reward):
        """Earn resources FIXME"""
        self.balance += reward
        self.update_counter()

class PlayScene(cocos.scene.Scene):
    def __init__(self):
        super(PlayScene, self).__init__()
        bg_layer = cocos.layer.ColorLayer(255, 255, 255, 255)
#        grid_layer = GridLayer()
        world_layer = WorldLayer()
        hud_layer = hud.HudLayer(world_layer)

        # wall tile (120 x 120 px):
        for i in range(0, const.WINDOW_W, 120):
            for j in range(0, const.WINDOW_H, 120):
                wall_tile = cocos.sprite.Sprite('wall.png')
                wall_tile.x = wall_tile.image.width / 2 + i
                wall_tile.y = wall_tile.image.height / 2 + j
                bg_layer.add(wall_tile, z=0)
            
        self.add(bg_layer, z=0)
#        self.add(grid_layer, z=1)
        self.add(world_layer, z=2)
        self.add(hud_layer, z=3)


def get_play_scene():
    """builds up the play scene"""
    # todo: receive params to allow continue saved game
    scene = PlayScene()
    return scene
