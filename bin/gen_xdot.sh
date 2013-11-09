#! /bin/bash

# Generates CN.xdot file from CN.dot file

DOT_FILE=${PWD}/../graphs/CN.dot
OUT_FILE=${PWD}/../graphs/CN.xdot

dot -Txdot $DOT_FILE -o $OUT_FILE;
