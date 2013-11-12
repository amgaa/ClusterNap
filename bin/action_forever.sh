#! /bin/bash

# Runs action_on_off.py every $WHILE seconds

ACTION=${PWD}/action_on_off.py
WHILE=10

while true
do
	${ACTION}
	sleep ${WHILE}
done
