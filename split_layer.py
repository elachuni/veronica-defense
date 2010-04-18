from cocos.layer import Layer, ColorLayer
from cocos.rect import Rect

"""
SplitLayer
"""


class SplitLayer(Layer):
    """
    they form scenes with non-overlaping layers

    split_rect: the rect that sets the position and size of the layer
    
    """
    def __init__(self, split_rect, color=None):
        super (SplitLayer, self).__init__()
        self.split_rect = split_rect
        
        self.position = split_rect.position
        
        if color is not None:
            size = split_rect.size
            kwargs = {'width': size[0], 'height': size[1]}
            self.area = ColorLayer(*color, **kwargs)
            self.add(self.area)


def _split(rect, distance, horiz_vert):
    position = rect.position
    size = rect.size
    
    if horiz_vert == 'horiz':
        rect_a_pos = position
        rect_b_pos = position[0] + distance, position[1]
        
        rect_a_size = distance, size[1]
        rect_b_size = size[0] - distance, size[1]
    
    else:
        rect_a_pos = position
        rect_b_pos = position[0], position[1] + distance
        
        rect_a_size = size[0], distance
        rect_b_size = size[0], size[1] - distance
    
    rect_a = Rect(rect_a_pos[0], rect_a_pos[1], *rect_a_size)
    rect_b = Rect(rect_b_pos[0], rect_b_pos[1], *rect_b_size)
    
    return (rect_a, rect_b)


def split_horizontal(rect, distance):
    """
    get two new rects, by spliting the rect horizontally at distance
    """
    return _split(rect, distance, 'horiz')

def split_vertical(rect, distance):
    """
    get two new rects, by spliting the rect verticaally at distance
    """
    return _split(rect, distance, 'vert')


def main():
    """
    test split layers
    """
    from cocos.scene import Scene
    from cocos.director import director
    
    director.init()
    
    window_size = director.get_window_size()
    window_rect = Rect(0, 0, *window_size)
    
    distance = window_size[0] * 3/4
    main_rect, rest_rect = split_horizontal(window_rect, distance)
    
    status_height = 80
    status_rect, menu_rect = split_vertical(rest_rect, status_height)
    
    main_layer = SplitLayer(main_rect)
    menu_layer = SplitLayer(menu_rect, color=(255, 255, 0, 255))
    status_layer = SplitLayer(status_rect, color=(255, 0, 255, 255))
    
    scene = Scene()
    scene.add(main_layer, z=0)
    scene.add(menu_layer, z=1)
    scene.add(status_layer, z=2)
    
    director.run(scene)

if __name__ == '__main__':
    main()
