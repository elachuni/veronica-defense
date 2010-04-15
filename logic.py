"""

general tower defense logic

"""

import math
import time

from notifier import Notifier, notify
from utils import angle_difference


class Grid(object):
    """
    the world's grid
    """
    possible_dirs = ((-1, 0), (0, -1), (1, 0), (0, 1))
    
    def __init__(self, size):
        """
        Arguments:
        
        - `size`: the grid's width and height measured in ammount
                  of cells
        """
        # grid position -> world objects:
        self.grid = {}
        self.solids = {}
        
        self.size = size
    
    def is_empty_at(self, grid_cell):
        """
        True if the grid cell is empty
        """
        return grid_cell not in self.grid
    
    def is_solid_at(self, grid_cell):
        """
        True if the grid cell has a solid
        """
        return grid_cell in self.solids
    
    def get_at(self, grid_cell):
        """
        return a set of world objects in the given grid cell, one
        world object if there is only one, or None if the cell is
        empty.
        """
        result = self.grid.get(grid_cell)
        if result is not None and len(result) == 1:
            return list(result)[0]
        return result
    
    def get_filled_cells(self):
        return self.grid.keys()
    
    def get_solid_cells(self):
        return self.solids.keys()
    
    def can_fit_at(self, world_object_class, grid_pos):
        """
        True if a world object of class world_object_class can fit at the
        given grid position
        """
        for x in range(world_object_class.size[0]):
            for y in range(world_object_class.size[1]):
                grid_cell = grid_pos[0] + x, grid_pos[1] + y
                if self.is_solid_at(grid_cell):
                    return False
                    break
        return True
    
    def add(self, world_obj, grid_pos):
        """
        add world_object filling the grid positions.
        
        Arguments:
        - `world_obj`: the world object to add
        
        - `grid_pos`: the position that the object's top left corner
                      will be in the world.
        
        """
        assert(self.can_fit_at(world_obj.__class__, grid_pos))
        
        is_solid = False
        for solid_class in solid_classes:
            if isinstance(world_obj, solid_class):
                is_solid = True
        
        for x in range(world_obj.size[0]):
            for y in range(world_obj.size[1]):
                cell = grid_pos[0] + x, grid_pos[1] + y
                if self.grid.get(cell) is None:
                    self.grid[cell] = set([world_obj])
                else:
                    self.grid[cell].add(world_obj)
                if is_solid:
                    self.solids[cell] = world_obj
        
        world_obj.grid_pos = grid_pos
    
    def remove(self, world_obj):
        """
        remove world_obj emptying the grid.
        """
        is_solid = False
        for solid_class in solid_classes:
            if isinstance(world_obj, solid_class):
                is_solid = True
        
        world_obj.grid_pos = None
        for grid_cell, world_objs_set in self.grid.items():
            if world_obj in world_objs_set:
                self.grid[grid_cell].remove(world_obj)
                if len(world_objs_set) == 0:
                    del self.grid[grid_cell]
                if is_solid:
                    del self.solids[grid_cell]
    
    def move(self, world_object, new_pos):
        """
        move world_object to another position in the grid.
        """
        self.remove(world_object)
        self.add(world_object, new_pos)


class World():
    """
    the world where the battle occurs.
    """
    def __init__(self, grid_size):
        """
        """
        self.grid = Grid(grid_size)
        
        self.towers = set()
        self.enemies = set()

        self.hq = None
        self.active_tower = None
    
    def move_enemies(self):
        for enemy in self.enemies:
            enemy.start_move()
    
    def add(self, world_obj, grid_pos):
        if isinstance(world_obj, Tower):
            self.towers.add(world_obj)
        elif isinstance(world_obj, Enemy):
            self.enemies.add(world_obj)
        elif isinstance(world_obj, Hq):
            self.hq = world_obj
        
        self.grid.add(world_obj, grid_pos)
        world_obj.enter_world(self)
    
    def remove(self, world_obj):
        if isinstance(world_obj, Tower):
            self.towers.remove(world_obj)
        elif isinstance(world_obj, Enemy):
            self.enemies.remove(world_obj)
        
        self.grid.remove(world_obj)
        world_obj.leave_world()
    
    def update(self):
        for tower in self.towers:
            tower.update()
    
    def activate_tower(self, tower):
        self.deactivate_tower()
        self.active_tower = tower
        tower.activate()
    
    def deactivate_tower(self):
        if self.active_tower is not None:
            self.active_tower.deactivate()
    
    def calculate_paths(self):
        """
        calculate the paths to the HG (for the enemies)
        """
        self.paths = {}
        
        target = self.hq.grid_pos
        solid_cells = self.grid.get_solid_cells()
        q = [target]
        while len(q):
            cell = q.pop(0)
            if cell in solid_cells:
                continue
            for dire in Grid.possible_dirs:
                new_cell = (cell[0] - dire[0], cell[1] - dire[1])
                if not ((0 <= new_cell[0] < self.grid.size[0]) and 
                        (0 <= new_cell[1] < self.grid.size[1])):
                    continue
                if new_cell not in self.paths:
                    self.paths[new_cell] = dire
                    q.append(new_cell)


class WorldObject(Notifier):
    """
    any object in the world.
    
    it notifies changes so the GUI can be updated.
    """
    
    # the object's width and height measured in grid cells
    size = (1, 1)
    
    def __init__(self):
        """
        """
        super(WorldObject, self).__init__()
        
        # the object knows the world
        self.world = None
        
        # the position of the object's top left corner in the grid
        self.grid_pos = None
    
    @notify
    def enter_world(self, world):
        self.world = world

    @notify
    def leave_world(self):
        self.world = None


class Tower(WorldObject):
    """
    the tower that destroys enemies shooting them.
    """
    size = (2, 2)
    
    # how fast does the tower produce shoots, in seconds
    shoot_reload = 0.8
    
    # how fast goes the shot in grid cells per second
    shot_speed = 8
    
    # the radius where the tower can see enemies
    sight_radius = 3
    
    # how much it cost to add this tower to the world
    resources_to_add = 50
    
    # how much is gained if this tower is removed from the wold
    resources_to_remove = -30
    
    def __init__(self):
        super(Tower, self).__init__()
        
        # the desired angle to shoot
        self.target_angle = 0
        
        self.last_shot = time.time()
    
    def calc_sight(self, enemy):
        # provided by the GUI
        return 0
    
    def get_enemies_at_sight(self):
        enemies_at_sight = []
        for enemy in self.world.enemies:
            at_sight, distance, angle = self.calc_sight(enemy)
            if at_sight:
                enemies_at_sight.append((enemy, distance, angle))
        return enemies_at_sight
    
    def is_shooting_time(self):
        return time.time() - self.last_shot > self.shoot_reload
    
    @notify
    def shoot(self):
        # TODO: only to test!
        self.target_enemy.get_hurt(1)
            
        self.last_shot = time.time()
    
    @notify
    def update(self):
        """
        called in each iteration of the world
        """
        is_shooting = False
        enemies_at_sight = self.get_enemies_at_sight()
        if len(enemies_at_sight) > 0:
            enemy, distance, angle = enemies_at_sight[0]
            self.target_distance = distance
            self.target_angle = angle
            
            # TODO: only to test!
            self.target_enemy = enemy
            
            if angle_difference(self.target_angle, self.angle) < 10:
                is_shooting = True
        
        self.is_shooting = is_shooting
        
        if self.is_shooting and self.is_shooting_time():
            self.shoot()
    
    def get_angle(self):
        # provided by the GUI
        return 0
    angle = property(get_angle)
    
    @notify
    def activate(self):
        # does nothing but the GUI gets notified
        pass

    @notify
    def deactivate(self):
        # does nothing but the GUI gets notified
        pass


class Enemy(WorldObject):
    """
    an enemy that tries to reach the hq before the towers kill him.
    """
    
    # how many lives this enemy has when born
    initial_lives = 3
    
    # where does the enemy point to when born
    initial_direction = (0, 1)

    # how fast does the enemy move, in grid cells per seconds
    speed = 1.4
    
    def __init__(self):
        super(Enemy, self).__init__()
        
        self.lives = self.initial_lives
        
        # directions to move:
        self.direction = self.initial_direction
        self.next_direction = None
    
    def enter_world(self, world):
        super(Enemy, self).enter_world(world)
        self.start_move()
    
    @notify
    def start_move(self):
        """
        called recursively until the directions are traversed
        """
        self.next_direction = self.world.paths[self.grid_pos]
    
    def move(self, direction):
        """
        move enemy to another direction in the grid.
        """
        self.direction = direction
        
        new_pos = (self.grid_pos[0] + direction[0],
                   self.grid_pos[1] + direction[1])
        self.world.grid.move(self, new_pos)
        
        if self.grid_pos == self.world.hq.grid_pos:
            self.success()
        else:
            self.start_move()
    
    @notify
    def get_hurt(self, damage):
        self.lives -= damage
        if self.lives == 0:
            self.die()
    
    @notify
    def success(self):
        self.world.remove(self)
    
    @notify
    def die(self):
        self.world.remove(self)


class Hq(WorldObject):
    """
    the place to defend with towers
    """
    initial_energy = 100
    
    def __init__(self):
        super(Hq, self).__init__()
        self._energy = self.initial_energy
    
    def loose_energy(self, damage):
        self._energy -= damage


class ResourceManager(object):
    """
    the resources that the player has.
    """
    # operation > resources obtained (or left if negative)
    resources_for_operation = {
        'add tower': Tower.resources_to_add,
        'remove tower': Tower.resources_to_remove,
        'huge buy': 5000,
    }
    def __init__(self, initial_resources):
        self._resources = initial_resources
    
    def can_be_done(self, operation):
        """
        True if operation can be done
        """
        res = self.resources_for_operation[operation]
        return self._resources - res > 0
    
    def operate(self, operation):
        assert(self.can_be_done(operation))
        res = self.resources_for_operation[operation]
        self._resources -= res


# solid world classes:
solid_classes = [Tower]


def test():
    """
    >>> world = World(grid_size=(30, 30))
    >>> resource_manager = ResourceManager(80)
    
    >>> print world.grid.is_empty_at((6, 6))
    True
    
    >>> print resource_manager.can_be_done('huge buy')
    False
    
    >>> tower = Tower()
    >>> print tower.grid_pos
    None
    
    >>> pos = (5, 5)
    >>> print world.grid.can_fit_at(Tower, pos)
    True
    
    >>> print resource_manager.can_be_done('add tower')
    True
    
    >>> print len(world.towers)
    0
    
    >>> world.add(tower, pos)
    >>> resource_manager.operate('add tower')
    >>> print tower.grid_pos
    (5, 5)
    
    >>> print len(world.towers)
    1
    
    >>> print world.grid.can_fit_at(Tower, pos)
    False
    
    >>> print resource_manager._resources
    30
    
    >>> print resource_manager.can_be_done('add tower')
    False
    
    >>> print world.grid.is_empty_at((6, 6))
    False

    >>> world.remove(tower)
    >>> resource_manager.operate('remove tower')
    >>> print world.grid.is_empty_at((6, 6))
    True

    >>> print resource_manager._resources
    60

    >>> world.add(tower, pos)
    >>> resource_manager.operate('add tower')
    
    >>> print resource_manager._resources
    10
    
    """
    
    import doctest
    doctest.testmod()

        
if __name__ == '__main__':
    test()
