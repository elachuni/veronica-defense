
from cocos.director import director
from cocos.menu import Menu, MenuItem, CENTER, zoom_in, zoom_out

class GameMenu(Menu):
    """Initial game menu"""
    def __init__(self, start):
        super(GameMenu, self).__init__("Veronica Defender")

        self.start = start

        self.menu_valign = CENTER
        self.menu_halign = CENTER
#        self.font_title['font_size'] = 32

        items = []

        items.append(MenuItem('Nuevo Juego', self.on_new_game))
        items.append(MenuItem('Lalalala', self.on_new_game))
        items.append(MenuItem('Salir', self.on_quit))

        self.create_menu(items, zoom_in(), zoom_out())

    def on_new_game(self):
        """When a new game is open"""
        self.start()

    def on_quit(self):
        """When the game is exited"""
        director.pop()

