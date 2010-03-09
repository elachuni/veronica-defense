#!/bin/sh

cd $(dirname $0)

if [ ! -d deps ]; then
    mkdir deps
fi

cd deps

if [ ! -d cocos2d-svn ]; then
    svn checkout http://los-cocos.googlecode.com/svn/trunk/ cocos2d-svn
else
    cd cocos2d-svn
    svn up
    cd ..
fi

ln -s cocos2d-svn/cocos cocos 2>&1 1>/dev/null

if [ ! -d pyglet-svn ]; then
    svn checkout http://pyglet.googlecode.com/svn/trunk/ pyglet-svn
else
    cd pyglet-svn
    svn up
    cd ..
fi

ln -s pyglet-svn/pyglet pyglet 2>&1 1>/dev/null

echo
echo "Listo. Para jugar hay que ejecutar: ./main.py"

