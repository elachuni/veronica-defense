#! -*- coding: utf-8 -*-

import math
import datetime
import time

import cocos
from cocos.actions import RotateTo, MoveBy, CallFunc, FadeOut, ScaleTo
from cocos.director import director
from cocos.menu import CENTER
import const
import fx_parent


def distance(a, b):
    """Measure distance between two points"""
    return math.hypot((a.grid_x - b.grid_x), (a.grid_y - b.grid_y))

def angle_difference(a, b):
    """Measure difference between two angles"""
    return  min(abs(b - a), 360 - b + a, 360 - a + b)

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

    def layer(self):
        """Returns the layer this object's sprite should be added to"""
        return self.world

    def create_sprite(self):
        """Create the object's sprite"""
        # we create a batch for this type of enemy
        if not hasattr(self.__class__, 'batch'):
            self.__class__.batch = cocos.batch.BatchNode()
            self.layer().add(self.__class__.batch)

        self.sprite = cocos.sprite.Sprite(self.sprite_file)
        self.sprite.x = (self.grid_x + self.size / 2.0) * const.GRID
        self.sprite.y = (self.grid_y + self.size / 2.0) * const.GRID
        # we add the enemy sprite to the batch
        self.__class__.batch.add(self.sprite)


class Shot(MapObject):
    """Shot fired from a tower"""
    speed = 1000
    sprite_file = 'shot.png'
    size = 1

    def __init__(self, world, grid_x, grid_y, ang_degrees):
        super(Shot, self).__init__(world, grid_x, grid_y)
        ang_radians = math.radians(ang_degrees)
        x = math.sin(ang_radians)
        y = math.cos(ang_radians)
        self.world.shots.append(self)
        self.create_sprite()
        self.sprite.do(MoveBy((self.speed * x, self.speed * y), 1.0) * 3
                       + CallFunc(self.remove))

    def layer(self):
        """Layer where shots are placed"""
        return self.world.shots_layer

    def update(self):
        """Shot logic on each frame"""
        # remove if shot goes out of the window:
        if (self.sprite.x > const.WINDOW_W or self.sprite.y > const.WINDOW_H
                or self.sprite.x < 0 or self.sprite.y < 0):
            self.remove()
            return

        # collision between shots and enemies:
        shot_rect = self.sprite.get_rect()
        for enemy in self.world.enemies:
            enemy_rect = enemy.sprite.get_rect()
            if shot_rect.intersects(enemy_rect):
                enemy.take_damage(damage = 1)
                self.world.resources.process_reward(enemy.reward)
                self.remove()
                break

    def remove(self):
        """Remove the shot from the game"""
        super(Shot, self).remove()
        # Avoid removing twice:
        if self in self.world.shots:
            self.world.shots.remove(self)


class Tower(MapObject):
    """Defender tower"""
    shot_class = Shot
    sprite_file = 'Tower.png'
    size = 2

    def __init__(self, world, grid_x, grid_y, sight=100):
        super(Tower, self).__init__(world, grid_x, grid_y)
        self.sight = sight
        self.is_shooting = False

        self.create_sprite()
        # the tower sprite:
        self.sprite.rotation = -30

        # a circle sprite to show the sight:
        self.sight_sprite = cocos.sprite.Sprite('circle.png')
        self.sight_sprite.x = self.sprite.x
        self.sight_sprite.y = self.sprite.y
        self.sight_sprite.scale = self.sight / 300.0
        self.sight_sprite.opacity = 90
        # TODO poner un self.world.sight_layer ?
        self.world.add(self.sight_sprite)
        self.last_shot = time.time()

    def update(self):
        """Tower logic on each frame"""
        # change sight color for testing:
        enemies_at_sight = self.check_enemies()

        if len(enemies_at_sight) == 0:
            self.sight_sprite.opacity = 50
        else:
            self.sight_sprite.opacity = 100

            enemy = self.choose_enemy(enemies_at_sight)
            self.aim_at(enemy)

            ang = angle_difference(self.get_angle_to(enemy),
                                   self.sprite.rotation)

            if self.can_shoot() and ang < 15:
                shot = self.shot_class(self.world, self.grid_x +
                                       self.size / 4.0, self.grid_y +
                                       self.size / 4.0,
                                       self.sprite.rotation)
                self.last_shot = time.time()

    def layer(self):
        """Layer where towers are placed"""
        return self.world.towers_layer

    def choose_enemy(self, enemies_at_sight):
        """Chose an enemy from the enemies at sight to shot at"""
        #choose the most dangerous enemy (closest to the tower)
        return min(enemies_at_sight, key=lambda x:distance(x, self.world.hq))

    def can_shoot(self):
        """See if tower is ready to shoot"""
        return time.time() - self.last_shot >= 1

    def get_angle_to(self, enemy):
        """Get angle to aim to an enemy"""
        ang_radians = math.atan2(enemy.sprite.x - self.sprite.x,
                                    enemy.sprite.y - self.sprite.y)
        return math.degrees(ang_radians)

    def aim_at(self, enemy):
        """Aim the cannon to an enemy"""
        self.sprite.do(RotateTo(self.get_angle_to(enemy), 0.1))

    def check_enemies(self):
        """List the enemies at sight"""
        enemies_at_sight = []
        # check for enemies that enter in the tower sight:
        for enemy in self.world.enemies:
            dx = self.sprite.x - enemy.sprite.x
            dy = self.sprite.y - enemy.sprite.y
            distance = math.sqrt(dx**2 + dy**2)
            if self.sight + enemy.radio > distance:
                enemies_at_sight.append(enemy)
        return enemies_at_sight

class HQ(MapObject):
    """Head Quarters to defend"""
    size = 2
    sprite_file = 'hq.png'

    def __init__(self, world, grid_x, grid_y):
        super(HQ, self).__init__(world, grid_x, grid_y)
        self.life = 10
        self.create_sprite()

        # life counter on screen
        self.life_counter = cocos.text.Label("",
                                             font_size=20,
                                             color=(255,0,0,255))
        self.life_counter.position = 10, 40
        self.world.add(self.life_counter, z=0)
        self.update_counter()

    def take_damage(self, damage):
        """Take damage from an enemy"""
        self.life -= damage
        self.update_counter()
        if self.life <= 0:
            self.world.schedule_interval(self.world.game_over, 0)

    def update_counter(self):
        """Update on-screen life counter"""
        self.life_counter.element.text = "vidas: %s" % self.life

class Impact(fx_parent.Fx):
    """Impact of a shot"""
    sprite_file = 'impact.png'

    def __init__(self,  enemy):
        super(Impact, self).__init__(enemy)
        self.enemy = enemy
        self.world.impacts.append(self)

    def update(self):
        """Impact logic on each frame"""
        if self.enemy.lives:
            self.sprite.x = self.enemy.sprite.x
            self.sprite.y = self.enemy.sprite.y

    def remove(self):
        """Remove the impact from the world"""
        self.world.impacts.remove(self)
        super(Impact, self).remove()

class Enemy(MapObject):
    """Kill them!!"""
    size = 1
    sprite_file = 'enemy.png'

    def __init__(self, world, grid_x, grid_y, lives=3, template=None):
        super(Enemy, self).__init__(world, grid_x, grid_y)
        self.lives = lives
        self.speed = 1.4
        self.world.enemies.append(self)
        self.template_loader(template)
        self.create_sprite()
        # add radio from sprite
        self.radio = self.sprite.width / 2
        self.reward = 1
        self.damage = 1

        # start moving
        self.next_move()

    def layer(self):
        """Layer where the enemies are placed"""
        return self.world.enemies_layer

    def template_loader(self, template):
        """Load enemy information from a template"""
        if template is None:
            return
        self.__dict__.update(template)

    def update(self):
        """Enemy logic on each frame"""
        # if enemy go out of the window:
        if (self.sprite.x > const.WINDOW_W or
            self.sprite.y > const.WINDOW_H or
            self.sprite.y < 0):
            self.remove()
            return

        if self.arrived():
            self.remove()
            self.world.hq.take_damage(self.damage)
            return

    def take_damage(self, damage):
        """Take damage from a shot"""
        self.lives -= damage
        impact = Impact(self)
        impact.sprite.scale = 0.1
        impact.sprite.do(ScaleTo(5, 1) | FadeOut(1) +
                         CallFunc(impact.remove))
        if self.lives <= 0:
            self.die()

    def arrived(self):
        """Determine if the enemy has arrivet to the HQ"""
        return distance(self, self.world.hq) < 1

    def die(self):
        """Yeah!"""
        self.remove()

    def remove(self):
        """Remove the enemy from the game"""
        super(Enemy, self).remove()
        self.world.enemies.remove(self)

    def next_move(self):
        """Next move, finding the path to the HQ"""
        if self.grid_x < 0:
            d = (1, 0)
        elif self.grid_y < 0:
            d = (0, 1)
        else:
            d = self.world.paths[self.grid_y][self.grid_x]
        self.grid_x += d[0]
        self.grid_y += d[1]
        move = (d[0] * const.GRID, d[1] * const.GRID)
        if d[0] == 1 and d[1] == 0:
            self.sprite.do(RotateTo(00, 0.2))
        elif d[0] == -1 and d[1] == 0:
            self.sprite.do(RotateTo(180, 0.2))
        elif d[0] == 0 and d[1] == 1:
            self.sprite.do(RotateTo(-90, 0.2))
        elif d[0] == 0 and d[1] == -1:
            self.sprite.do(RotateTo(90, 0.2))

        self.sprite.do(MoveBy(move, 1/self.speed) +
                             CallFunc(self.next_move))

