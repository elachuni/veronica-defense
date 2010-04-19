#!/usr/bin/env python

import pyglet.resource
from cocos.director import director

import settings
from logic import World, Level, ResourceManager
from levels_data import levels_data
from level_scene import LevelScene

def main():
    pyglet.resource.path.append("images")
    pyglet.resource.reindex()
    
    director.init(vsync=True)

    # store window size in settings:
    settings.WINDOW_SIZE = director.get_window_size()

    # just a test level for now:
    level_data = levels_data[0]
    level = Level(level_data)

    # the level is shown as a cocos scene:
    level_scene = LevelScene(level)
    director.run(level_scene)
    

if __name__ == '__main__':
    main()
