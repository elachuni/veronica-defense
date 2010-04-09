from logic import *

class CommonTower(Tower):
    size = (2, 2)
    shoot_reload = 0.8
    shot_speed = 8
    sight_radius = 3
    resources_to_add = 50
    resources_to_remove = -30

class HardTower(Tower):
    size = (2, 2)
    shoot_reload = 1.2
    shot_speed = 8
    sight_radius = 5
    resources_to_add = 80
    resources_to_remove = -50

class CommonEnemy(Enemy):
    initial_lives = 4
    speed = 1.2

class FastEnemy(Enemy):
    initial_lives = 2
    speed = 1.8

class BossEnemy(Enemy):
    initial_lives = 20
    speed = 5.0

    
