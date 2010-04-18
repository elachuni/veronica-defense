#!/usr/bin/env python

import pyglet.resource
from cocos.director import director

import settings
from logic import World
from levels_data import levels_data
from level_scene import LevelScene

def main():
    pyglet.resource.path.append("images")
    pyglet.resource.reindex()
    
    director.init(vsync=True)
    
    settings.WINDOW_SIZE = director.get_window_size()
    settings.GRID_SIZE = (settings.WINDOW_SIZE[0] / settings.GRID_CELL,
                          settings.WINDOW_SIZE[1] / settings.GRID_CELL)
    
    world = World(grid_size=settings.GRID_SIZE)
    level_data = levels_data[0]
    scene = LevelScene(world, level_data)
    director.run(scene)
    

if __name__ == '__main__':
    main()
