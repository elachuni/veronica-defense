#! -*- coding: utf8 -*-
"""Parent class for fx"""
import cocos
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

#class LifeBar(Fx)              
        
       
