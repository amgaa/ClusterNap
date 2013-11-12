#! /bin/bash

# Generates eps image in the current folder and png image in /var/www/digraph folder

GENIMG=${PWD}/gen_img.sh
WHILE=10

while true
do
	${GENIMG}
	sleep ${WHILE}
done
