#! /bin/bash

# Runs action_on_off.py every $WHILE seconds

ACTION=${PWD}/action_on_off.py
WHILE=30

while true
do
	${ACTION}
	sleep ${WHILE}
done
