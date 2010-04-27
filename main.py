#!/usr/bin/env python

import pyglet.resource
from cocos.director import director
from cocos.scenes import FadeTransition

import settings
from logic import Level
from levels_data import levels_data
from level_scene import LevelScene

class LevelSelector(object):
    def __init__(self, levels_data):
        self.levels_data = levels_data
        self.current_scene = None
    
    def next(self, previous_resources=None):
        """
        display the next level
        """
        if len(self.levels_data) == 0:
            self.game_over(user_success=True)
            return
        
        level_data = self.levels_data.pop(0)
        level = Level(level_data, previous_resources)
    
        # the level is shown as a cocos scene:
        new_scene = LevelScene(level, self)
        if self.current_scene is not None:
            self.current_scene = new_scene
            director.replace(FadeTransition(new_scene, duration=2))
        else:
            self.current_scene = new_scene
            director.run(new_scene)
    
    def game_over(self, user_success):
        if user_success == True:
            print "you win the game :)"
        else:
            print "you loose :("


def main():
    pyglet.resource.path.append("images")
    pyglet.resource.reindex()
    
    director.init()
    
    # store window size in settings:
    settings.WINDOW_SIZE = director.get_window_size()

    level_sel = LevelSelector(levels_data)
    level_sel.next()


if __name__ == '__main__':
    main()
