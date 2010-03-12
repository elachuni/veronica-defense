#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, time

# magia de import
sys.path.insert(0, 
    os.path.join(os.path.dirname(os.path.realpath(__file__)), 'deps'))

# si las librerias no existen no mostrar un error demasiado extraño
try:
    import cocos
    import pyglet
except ImportError:
    print """Verónica Defense
Necesitás instalar las librerías cocos2d y pyglet para jugar Veronica Defense.
Para ello hay que ejecutar el script 'install-deps.sh' o descargarlas desde:"""
    print "  http://cocos2d.org/"
    print "  http://pyglet.org/"
    sys.exit(1)

from cocos.director import director
from cocos.layer import MultiplexLayer
from pyglet.window import key

pyglet.resource.path.append("images")
pyglet.resource.reindex()

import const
from gamemenu import GameMenu

if __name__ == "__main__":
    director.init(vsync=True)
    director.show_FPS = True
    # set globals:
    const.WINDOW_W, const.WINDOW_H = director.get_window_size()
    #set_window_size(WINDOW_W, WINDOW_H)
    const.GRID_LEN_X = len(range(0, const.WINDOW_W, const.GRID))
    const.GRID_LEN_Y = len(range(0, const.WINDOW_H, const.GRID))

    # desconectado temporariamente
    #main_menu = Scene(MultiplexLayer(GameMenu(start_game)))
    #director.run(main_menu)

    # temporario, despues esto se mueve a la opcion 'play' del main menu
    import play_scene
    scene = play_scene.get_play_scene()
    director.run(scene)
