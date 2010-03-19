#! -*- coding: utf-8 -*-
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
    """Dinamic Lifebar, using gl primitives""" 
    max_width = 30 
    back_color = (0,0,0,100)
    top_color = (255, 0, 0, 100)
    back_height = 5
    top_height = 3
    container_vertex = [(-2, -2, 0), (max_width+2,-2, 0), (max_width+2, back_height, 0), (-2, back_height, 0 )]
    
    def __init__(self, target):
        super(LifeBar, self).__init__()
        self.target = target
        self.world = self.target.world
        self.max_length = self.target.lives
        self.world.fx_layer.add(self)
        self.x_offset = -(self.max_width / 2) 
        self.y_offset = self.target.sprite.image.height / 2 + 5

    def draw(self):
        """this is used by cocos, to draw te primitives"""
        self.update()    
        self.gl_draw([(self.container_vertex, self.back_color), (self.bar_vertex, self.top_color)])
        

    def remove(self):
        """remove the lifebar from fx layer"""
        self.world.fx_layer.remove(self)

    def update(self):
        """updates position and lives of the target, and re-define te vertex points"""
        self.width = (self.target.lives*self.max_width)/self.max_length
        self.x = self.target.sprite.x + self.x_offset
        self.y = self.target.sprite.y + self.y_offset
        self.bar_vertex = [(0,0,0), (self.width, 0, 0), (self.width, self.top_height, 0), (0,self.top_height,0)]
     
    def gl_draw(self, vertexes):
        """Takes a List of tuples like (vertexList, color) and draw them"""
        glPushMatrix()
        for draw in vertexes:
            glBegin(GL_QUADS)
            glColor4ub(*draw[1])
            for v in draw[0]:
                vertex = (v[0]+self.x, v[1]+self.y, v[2])
                glVertex3f(*vertex)
            glEnd()
        glPopMatrix()
        
        


       
