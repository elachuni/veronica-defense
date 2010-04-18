from cocos.layer import Layer, ColorLayer

"""
SplitLayer
"""


class SplitLayer(Layer):
    """
    they form scenes with non-overlaping layers
    """
    def __init__(self, split_data, color=None):
        super (SplitLayer, self).__init__()
        self.position = split_data['position']
        size = split_data['size']
        
        kwargs = {'width': size[0], 'height': size[1]}
        
        if color is None:
            color = (0, 0, 0, 0)
        
        self.area = ColorLayer(*color, **kwargs)
        self.add(self.area)


def _split(split_data, split, horiz_vert):
    position = split_data['position']
    size = split_data['size']
    
    if horiz_vert == 'horiz':
        split_pos_a = position
        split_pos_b = position[0] + split, position[1]
        
        split_size_a = split, size[1]
        split_size_b = size[0] - split, size[1]
    
    else:
        split_pos_a = position
        split_pos_b = position[0], position[1] + split
        
        split_size_a = size[0], split
        split_size_b = size[0], size[1] - split
    
    split_data_a = {'position': split_pos_a, 'size': split_size_a}
    split_data_b = {'position': split_pos_b, 'size': split_size_b}
    
    return (split_data_a, split_data_b)


def split_horizontal(split_data, split):
    """
    split the rect horizontally
    """
    return _split(split_data, split, 'horiz')

def split_vertical(split_data, split):
    """
    split the rect vertically
    """
    return _split(split_data, split, 'vert')


def main():
    """
    test split layers
    """
    from cocos.scene import Scene
    from cocos.director import director
    
    director.init()
    
    window_size = director.get_window_size()
    status_height = 80
    
    window_data = {'position': (0, 0), 'size': window_size}
    main_data, rest_data = split_horizontal(window_data, window_size[0] * 3/4)
    status_data, menu_data = split_vertical(rest_data, status_height)
    
    main_layer = SplitLayer(main_data)
    menu_layer = SplitLayer(menu_data, color=(255, 255, 0, 255))
    status_layer = SplitLayer(status_data, color=(255, 0, 255, 255))
    
    scene = Scene()
    scene.add(main_layer, z=0)
    scene.add(menu_layer, z=1)
    scene.add(status_layer, z=2)
    
    director.run(scene)

if __name__ == '__main__':
    main()
