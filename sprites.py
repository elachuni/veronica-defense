import math

from cocos.cocosnode import CocosNode
from cocos.sprite import Sprite
from cocos.actions import MoveBy, RotateBy, RotateTo, CallFunc, \
    FadeOut, ScaleTo, ScaleBy, FadeTo, Delay

from cocos.text import Label

from pyglet.resource import ResourceNotFoundException

from lifebar_sprite import LifeBarSprite

from settings import GRID_CELL
from veronica_logic import *


def sight_function(tower, enemy):
    dx = enemy.sprite.position[0] - tower.sprite.position[0]
    dy = enemy.sprite.position[1] - tower.sprite.position[1]
    
    distance = math.sqrt(dx**2 + dy**2)
    ang_radians = math.atan2(dx, dy)
    angle = math.degrees(ang_radians)
    
    sight_px = tower.sight_radius * GRID_CELL
    
    return distance < sight_px, distance, angle

Tower.calc_sight = sight_function

def get_angle(tower):
    return tower.sprite.head.rotation
Tower.get_angle = get_angle
Tower.angle = property(get_angle)


class WorldSprite(CocosNode):
    """
    the representation of a world object, is a composition of coco's
    sprites.
    """
    name = 'no image'
    world_object_class = WorldObject
    
    def __init__(self, world_object):
        super(WorldSprite, self).__init__()
        assert(world_object.__class__ == self.world_object_class)
        
        # links between logic and representation:
        world_object.add_listener(self)
        
        # needed to get data from the world representation, position
        # in pixels, actual rotation of the sprite, etc.
        world_object.sprite = self
        
        self.setup(world_object)
    
    def setup(self, world_obj):
        """
        do the sprite composition and place it in the grid
        """
        filename = self.name.replace(' ', '_') + '.png'
        try:
            self.sprite = Sprite(filename)
            self.sprite.scale = 0.5 # sprites at double scale
            self.add(self.sprite, z=10)
        except ResourceNotFoundException:
            pass

        # place the sprite in the location given by the grid.
        x, y = world_obj.grid_pos
        width, height = world_obj.size
        self.position = ((x + width / 2.0) * GRID_CELL,
                         (y + height / 2.0) * GRID_CELL)
    
    def remove_me(self):
        """
        removes this sprite from its layer
        """
        self.parent.remove(self)
    


class EnemySprite(WorldSprite):
    def __init__(self, enemy):
        super(EnemySprite, self).__init__(enemy)
        
        self.move_vel = 1.0 / enemy.speed
        self.rotate_vel = 0.5 / enemy.speed
    
    def setup(self, enemy):
        """
        the enemies have a body that can be rotated and lifebar above
        them
        """
        super(EnemySprite, self).setup(enemy)
        
        # add body:
        body_filename = self.name.replace(' ', '_') + '_body.png'
        self.body = Sprite(body_filename)
        self.body.scale = 0.5
        self.add(self.body, z=20)
        
        # add lifebar:
        self.lifebar = LifeBarSprite(enemy)
        self.add(self.lifebar)
    
    def get_rotation_angle(self, direction, new_direction):
        """
        return the angle to rotate the enemy based on the current
        direction and the next one.
        """
        if direction == new_direction:
            return 0
        
        is_oposite_dir = (direction[0] - new_direction[0] == 0
                          or direction[1] - new_direction[1] == 0)
        if is_oposite_dir:
            return 180
        
        turn_left = (direction[0] - new_direction[0] == 1
                     or direction[1] - new_direction[1] == -1)
        if turn_left:
            return -90
        else:
            return 90
    
    def on_start_move(self, enemy):
        """
        do a smooth move of the enemy and update the enemy when done
        """
        move_px = (enemy.next_direction[0] * GRID_CELL,
                   enemy.next_direction[1] * GRID_CELL)
        
        # rotate if needed
        angle = self.get_rotation_angle(enemy.direction,
                                        enemy.next_direction)
        if angle != 0:
            self.body.do(RotateBy(angle, self.rotate_vel))
        
        self.do(MoveBy(move_px, self.move_vel) +
                CallFunc(enemy.move, enemy.next_direction))
    
    def on_get_hurt(self, enemy, damage):
        self.body.color = (255, 100, 100)
        
        def restore_color():
            self.body.color = (255, 255, 255)
        
        self.do(Delay(0.1) + CallFunc(restore_color))
    
    def on_die(self, enemy):
        self.stop()
        self.remove(self.lifebar)
        
        self.do(RotateBy(360, 0.5) * 3 + CallFunc(self.remove_me))
        self.body.do(FadeTo(20, 1.5))
    
    def on_success(self, enemy):
        self.stop()
        self.remove(self.lifebar)
        
        self.do(ScaleTo(0.01, 1.5) + CallFunc(self.remove_me))
        self.body.do(FadeTo(20, 1.5))


class TowerSprite(WorldSprite):
    
    def __init__(self, tower, shots_layer):
        super(TowerSprite, self).__init__(tower)

        self.shots_layer = shots_layer
        self.shot_speed_px = tower.shot_speed * GRID_CELL
    
    def setup(self, tower):
        """
        the towers have a head that can be rotated and a sight circle
        """
        super(TowerSprite, self).setup(tower)
        
        # add head sprite:
        head_filename = self.name.replace(' ', '_') + '_head.png'
        self.head = Sprite(head_filename)
        self.head.scale = 0.42
        self.head.position = self.head_position
        self.head.transform_anchor = self.head_anchor
        self.add(self.head, z=20)
        
        # add sight sprite:
        self.sight = Sprite('tower_sight.png')
        sight_radius_px = tower.sight_radius * 1.0 * GRID_CELL
        self.sight.scale = sight_radius_px / 300
        self.sight.visible = False
        self.sight.opacity = 90
        self.add(self.sight, z=0)
    
    def on_update(self, tower):
        """
        called each frame
        """
        if tower.is_shooting:
            self.sight.opacity = 90
        else:
            self.sight.opacity = 30
        self.head.do(RotateTo(tower.target_angle, 0.08))
    
    def on_activate(self, tower):
        self.sight.visible = True
    
    def on_deactivate(self, tower):
        self.sight.visible = False
    
    def on_shoot(self, tower):
        """
        when the tower shoots, add a shot sprite
        """
        shot_sprite = Sprite('shot.png')
        self.shots_layer.add(shot_sprite, z=30)
        
        ang_radians = math.radians(tower.angle)
        x = math.sin(ang_radians)
        y = math.cos(ang_radians)
        shot_sprite.position = (self.x + self.shot_position * x,
                                 self.y + self.shot_position * y)
        
        shot_distance = tower.target_distance - self.shot_position
        dx = (shot_distance) * x
        dy = (shot_distance) * y
        
        def remove_shot(shot):
            self.shots_layer.remove(shot)
        
        t = shot_distance / self.shot_speed_px
        shot_sprite.do(MoveBy((dx, dy), t) +
                        CallFunc(remove_shot, shot_sprite))
    
    def on_leave_world(self, tower):
        self.remove(self.sight)
        
        self.do(ScaleTo(1.5, 0.9) + CallFunc(self.remove_me))
        self.sprite.do(FadeTo(20, 0.9))
        self.head.do(FadeTo(20, 0.9))


class CommonTowerSprite(TowerSprite):
    name = 'common tower'
    world_object_class = CommonTower
    head_position = (0, 25)
    head_anchor = (0, -22)
    
    # distance to the point of the head
    shot_position = 50


class HardTowerSprite(TowerSprite):
    name = 'hard tower'
    world_object_class = HardTower
    head_position = (0, 25)
    head_anchor = (0, -22)
    
    # distance to the point of the head
    shot_position = 50


class CommonEnemySprite(EnemySprite):
    name = 'common enemy'
    world_object_class = CommonEnemy


class FastEnemySprite(EnemySprite):
    name = 'fast enemy'
    world_object_class = FastEnemy

    
class HqSprite(WorldSprite):
    name = 'hq'
    world_object_class = Hq

all_sprites = [CommonTowerSprite, HardTowerSprite, 
               CommonEnemySprite, FastEnemySprite, 
               HqSprite, WorldSprite]


class InfoSprite(CocosNode):
    def __init__(self, hq, resources):
        super(InfoSprite, self).__init__()
        hq.add_listener(self)
        resources.add_listener(self)

        # label to display hq lives:
        self.lives_label = Label("", font_size=20,
                                     color=(200,200,200,255))
        self.lives_label.position = 10, 35
        self.add(self.lives_label)
        
        # label to display resources:
        self.resources_label = Label("", font_size=20,
                                     color=(200,200,200,255))
        self.resources_label.position = 10, 10
        self.add(self.resources_label)
        
        self.on_loose_energy(hq)
        self.on_operate(resources)
    
    def on_loose_energy(self, hq, *args):
        self.lives_label.element.text = \
            "vidas: %s" % hq._energy
    
    def on_operate(self, resources, *args):
        self.resources_label.element.text = \
            "recursos: %s" % resources._resources

        
