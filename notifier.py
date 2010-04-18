
class Notifier(object):
    """
    notifies to the listeners after the decorated methods are called.
    
    >>> class Tower(Notifier):
    ...    def __init__(self, name):
    ...        self.name = name
    ...        self.pos = (0, 0)
    ...        super(Tower, self).__init__()
    ...
    ...    @notify
    ...    def move(self, pos):
    ...        self.pos = pos
    ...
    ...    @notify
    ...    def reset(self):
    ...        self.pos = (0, 0)
    ...
    ...    def change_name(self, new_name):
    ...        self.name = new_name
    ...        self.notify('change_name')
    ...

    >>> class TowerSprite(object):
    ...    def on_move(self, tower, pos):
    ...        print '%s moved to' % tower.name, pos
    ...
    ...    def on_reset(self, tower):
    ...        print '%s resetted' % tower.name
    ...
    
    >>> tower = Tower('little tower')
    >>> tower_sprite = TowerSprite()
    >>> tower.add_listener(tower_sprite)
    >>> tower.move((8, 6))
    little tower moved to (8, 6)
    
    >>> tower.reset()
    little tower resetted
    
    """
    def __init__(self):
        self.listeners = set()
    
    def add_listener(self, listener):
        self.listeners.add(listener)
    
    def remove_listener(self, listener):
        self.listeners.remove(listener)
    
    def notify(self, event_name, *args, **kwargs):
        for listener in self.listeners:
            callback = getattr(listener, 'on_' + event_name, None)
            if callback is not None:
                callback(self, *args, **kwargs)


def notify(func):
    """
    decorator to notify methods
    """
    def inner(notifier, *args, **kwargs):
        func(notifier, *args, **kwargs)
        notifier.notify(func.__name__, *args, **kwargs)
    return inner


if __name__ == '__main__':
    import doctest
    doctest.testmod()

