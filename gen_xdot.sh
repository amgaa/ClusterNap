#! /bin/bash

# Generates CN.xdot file from CN.dot file

DOT_FILE=${PWD}/CN.dot
OUT_FILE=${PWD}/CN.xdot

dot -Txdot $DOT_FILE -o $OUT_FILE;
