from cocos.cocosnode import CocosNode

from pyglet.gl import *

class LifeBarSprite(CocosNode):
    """Dinamic Lifebar, using gl primitives""" 
    container_width = 25
    max_height = 50
    container_color = (0, 0, 0, 50)
    bar_color = (255, 0, 0, 100)
    container_height = 2
    bar_height = 2
    
    container_vertex = [(0, 0, 0),
                        (container_width, 0, 0),
                        (container_width, container_height, 0),
                        (0, container_height, 0 )]
    
    def __init__(self, enemy):
        super(LifeBarSprite, self).__init__()
        
        # the lifebar will listen to the enemy:
        enemy.add_listener(self)
        
        self.max_lives = enemy.initial_lives
        self.x = -(self.container_width / 2) 
        self.y = self.max_height / 2 + 5
        
        self.on_get_hurt(enemy)
    
    def draw(self):
        """
        this is used by cocos, to draw the primitives
        """
        self.gl_draw([(self.container_vertex, self.container_color),
                      (self.bar_vertex, self.bar_color)])
    
    def on_get_hurt(self, enemy, *args):
        """
        updates position and lives of the target, and re-define te
        vertex points
        """
        self.bar_width = (enemy.lives*self.container_width)/self.max_lives
        
        self.bar_vertex = [(0, 0, 0),
                           (self.bar_width, 0, 0),
                           (self.bar_width, self.bar_height, 0),
                           (0, self.bar_height, 0)]
    
    def gl_draw(self, draw_list):
        """
        takes a List of tuples like (vertexList, color) and draw them
        """
        glPushMatrix()
        for vertexes, color in draw_list:
            glBegin(GL_QUADS)
            glColor4ub(*color)
            for v in vertexes:
                vertex = (v[0]+self.x, v[1]+self.y, v[2])
                glVertex3f(*vertex)
            glEnd()
        glPopMatrix()
