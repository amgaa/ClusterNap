#! /bin/bash

# Generates eps image in the current folder and png image in /var/www/digraph folder

XDOT_FILE=${PWD}/CN_updated.xdot
OUT_IMG=${PWD}/CN.eps
OUT_WEB_IMG=/var/www/digraph/CN.png

#./gen_dot.py > /dev/null;
./update_xdot.py
dot -Teps $XDOT_FILE -o $OUT_IMG;
sudo dot -Tpng $XDOT_FILE -o $OUT_WEB_IMG;
