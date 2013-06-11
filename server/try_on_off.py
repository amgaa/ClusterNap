#! /usr/bin/python

""" 
 Tries to change states of nodes according to the information from 
 get_on_off.py by checking their dependencies and their childs' states. 

 Tries to make all necessary nodes ON 
 Tries to make all unnecessary nodes OFF
"""

import sys, os, re
import get_on_off



class try_on_off:
    def __init__(self):
        self.NODES_TO_ON  = list()
        self.NODES_TO_OFF = list()
        self.STATES       = {}
        self.DEP_RUN_ON   = {}
        self.DEP_OFF      = {}

        self.NODES_TO_ON,      \
            self.NODES_TO_OFF, \
            self.STATES,       \
            self.DEP_RUN_ON,   \
            self.DEP_OFF        = get_on_off.get_on_off().main()

        self.STATES     = dict(self.STATES)
        self.DEP_RUN_ON = dict(self.DEP_RUN_ON)
        self.DEP_OFF    = dict(self.DEP_OFF)

        # Leave only OFF nodes in  self.NODES_TO_ON. 
        # Here we also leave Unknown state nodes untouched.
        for node in self.NODES_TO_ON:
            if self.STATES.has_key(node):
                if self.STATES[node] != -1:
                    self.NODES_TO_ON.remove(node)

        # Leave only ON nodes in self.NODES_TO_OFF
        # Here we also leave Unknown state nodes untouched.
        for node in self.NODES_TO_OFF:
            if self.STATES.has_key(node):
                if self.STATES[node] != 1:
                    self.NODES_TO_OFF.remove(node)

        return


    # Turns on ON-able OFF nodes
    def try_on(self, nodes_to_on):
        for node in nodes_to_on:
            if self.on_able(node):
                print "Can turn on " + node
            else:
                print "Cannot turn on " + node + " for now"


    # Turns off OFF-able ON nodes
    def try_off(self, nodes_to_off):
        for node in nodes_to_off:
            if self.off_able(node):
                print "Can turn off " + node
            else:
                print "Cannot turn off " + node + " for now"


    # Checks if an OFF node is ON-able (necessary childs are ON)
    def on_able(self, node):

        if not self.DEP_RUN_ON.has_key(node):
            print "No dependency found for node " + node
            return 0

        # When the first occurence of all nodes in any of clause os ON, return 1
        childs = self.DEP_RUN_ON[node]
        for clause in childs:
            flag = 0
            for node in clause:
                if self.STATES.has_key(node) and self.STATES[node] != 1:
                    flag = 1
                if not self.STATES.has_key(node):
                    flag = 1
            if flag == 0:
                return 1
            
        return 0

    

    # Checks if an ON node is OFF-able (necessary childs are ON)
    def off_able(self, node):
        if not self.DEP_OFF.has_key(node):
            print "No dependency found for node " + node
            return 0
        
        # When the first occurence of all nodes in any of clause os ON, return 1
        childs = self.DEP_OFF[node]
        for clause in childs:
            flag = 0
            for node in clause:
                if self.STATES.has_key(node) and self.STATES[key] != 1:
                    flag = 1
                if not self.STATES.has_key(node):
                    flag = 1
            if flag == 0:
                return 1

        return 0

    
    
    def main(self):

#        print self.DEP_RUN_ON
        print "NODES TO ON and their states: "
        for node in self.NODES_TO_ON:
            if self.STATES.has_key(node):
                print node + ": " + str(self.STATES[node])
            else:
                print node + ": state unwritten"

        self.try_on(self.NODES_TO_ON)
        self.try_off(self.NODES_TO_OFF)

        return


if __name__ == "__main__":
    sys.exit(try_on_off().main())
