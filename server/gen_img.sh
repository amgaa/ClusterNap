#! /bin/bash

# Generates eps image in the current folder and png image in /var/www/digraph folder

DOT_FILE=${PWD}/CN.dot
OUT_IMG=${PWD}/CN.eps
OUT_WEB_IMG=/var/www/digraph/CN.png

./gen_dot.py > /dev/null;
dot -Teps $DOT_FILE -o $OUT_IMG;
sudo dot -Tpng $DOT_FILE -o $OUT_WEB_IMG;
