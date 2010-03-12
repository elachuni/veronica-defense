#! -*- coding: utf8 -*-
"""Parent class for fx"""

import cocos
import pyglet
from pyglet.gl import *


class Fx(object):
    sprite_file = None
    def __init__(self, target):
        self.target = target
        self.deleted = False
        self.world = self.target.world
        self.create_sprite()


    def remove(self):
        self.__class__.batch.remove(self.sprite)

    def layer(self):
        return self.world.fx_layer
    
    def create_sprite(self):
        # we create a batch for this type of enemy
        if not hasattr(self.__class__, 'batch'):
            self.__class__.batch = cocos.batch.BatchNode()
            self.layer().add(self.__class__.batch)
        self.sprite = cocos.sprite.Sprite(self.sprite_file)
        self.sprite.opacity = 128
        self.sprite.x = self.target.sprite.x
        self.sprite.y = self.target.sprite.y
        # we add the enemy sprite to the batch
        self.__class__.batch.add(self.sprite)

class LifeBar(cocos.cocosnode.CocosNode):
    
    def __init__(self, target):
        super(LifeBar, self).__init__()
        self.target = target
        self.world = self.target.world
        self.max_length = self.target.lives
        self.x = self.target.sprite.x
        self.y = self.target.sprite.y
        self.max_width = 30
        self.bar_vertex = [(2, 2, 0), (18, 2, 0), (18, 6, 0), (2, 6, 0 )]
        self.world.fx_layer.add(self)

    def draw(self):
        self.update()    
        glPushMatrix()
        glBegin(GL_QUADS)
        glColor4ub(255, 0, 0, 255)
        for v in self.container_vertex:
            vertex = (v[0]+self.x, v[1]+self.y, v[2])
            glVertex3f(*vertex)
        glEnd()
        glPopMatrix()
    
    def remove(self):
        self.world.fx_layer.remove(self)

    def update(self):
        self.width = (self.target.lives*self.max_width)/self.max_length
        self.x = self.target.sprite.x - 15
        self.y = self.target.sprite.y + 10
        self.container_vertex = [(0,0,0), (self.width, 0, 0), (self.width, 8, 0), (0,8,0)]
    


       
