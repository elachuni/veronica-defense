from cocos.cocosnode import CocosNode

from pyglet.gl import *

class LifeBarSprite(CocosNode):
    """Dinamic Lifebar, using gl primitives""" 
    max_width = 30
    max_height = 50
    back_color = (0,0,0,100)
    top_color = (255, 0, 0, 100)
    back_height = 5
    top_height = 3
    
    container_vertex = [(-2, -2, 0),
                        (max_width+2,-2, 0),
                        (max_width+2, back_height, 0),
                        (-2, back_height, 0 )]
    
    def __init__(self, enemy):
        super(LifeBarSprite, self).__init__()

        # the lifebar will listen to the enemy:
        enemy.add_listener(self)
        
        self.max_length = enemy.initial_lives
        self.x_offset = -(self.max_width / 2) 
        self.y_offset = self.max_height / 2 + 5
        
        self.x = self.x_offset
        self.y = self.y_offset
        
        self.on_get_hurt(enemy)
    
    def draw(self):
        """
        this is used by cocos, to draw the primitives
        """
        self.gl_draw([(self.container_vertex, self.back_color),
                      (self.bar_vertex, self.top_color)])
    
    def on_get_hurt(self, enemy, *args):
        """
        updates position and lives of the target, and re-define te
        vertex points
        """
        self.width = (enemy.lives*self.max_width)/self.max_length
        self.bar_vertex = [(0,0,0),
                           (self.width, 0, 0),
                           (self.width, self.top_height, 0),
                           (0,self.top_height,0)]
     
    def gl_draw(self, vertexes):
        """
        takes a List of tuples like (vertexList, color) and draw them
        """
        glPushMatrix()
        for draw in vertexes:
            glBegin(GL_QUADS)
            glColor4ub(*draw[1])
            for v in draw[0]:
                vertex = (v[0]+self.x, v[1]+self.y, v[2])
                glVertex3f(*vertex)
            glEnd()
        glPopMatrix()
