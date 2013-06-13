#! /usr/bin/python

''' 
 Tries to change states of nodes according to the information (what nodes should be ON and which ones should be off)
 from get_on_off.py by checking their dependencies and their childs' states. 

 Tries to make all necessary nodes ON 
 Tries to make all unnecessary nodes OFF
'''

import sys, os, re
import get_on_off
import get_dependency
import get_state
import change_state

class try_on_off:
    def __init__(self):
        self.NODES_TO_ON  = list()
        self.NODES_TO_OFF = list()
        self.STATES       = {}
        self.DEP_RUN      = {}
        self.DEP_RUN_ON   = {}
        self.DEP_OFF      = {}
        # Dependency-g get config-s avah
        self.NODES_TO_ON,      \
            self.NODES_TO_OFF = get_on_off.get_on_off().main()
#            self.STATES 
#            self.DEP_RUN_ON,   \
#            self.DEP_OFF       \
        self.tmp_nodestoon = self.NODES_TO_ON[:]
        self.tmp_nodestooff = self.NODES_TO_OFF[:]
        print "NODES TO ON:"
        print self.NODES_TO_ON 
        print "NODES TO OFF:"
        print self.NODES_TO_OFF 

        self.STATES = dict(get_state.get_state().main())

        self.DEP_RUN = get_dependency.get_dependency().get_phys_run_dep()
        self.DEP_RUN.update(get_dependency.get_dependency().get_serv_run_dep())

        self.DEP_RUN_ON = get_dependency.get_dependency().get_phys_run_on_dep()
        self.DEP_RUN_ON.update(get_dependency.get_dependency().get_serv_run_on_dep())

        self.DEP_OFF    = get_dependency.get_dependency().get_phys_off_dep()
        self.DEP_OFF.update(get_dependency.get_dependency().get_serv_off_dep())  
 
#        print self.DEP_RUN_ON
#        self.tr_run_on = get_dependency.get_dependency().get_phys_run_on_dep()
#        print "from get congif: "
#        print self.tr_run_on

#        self.STATES     = dict(self.STATES)
#        self.DEP_RUN_ON = dict(self.DEP_RUN_ON)
#        self.DEP_OFF    = dict(self.DEP_OFF)
#        print self.STATES


        # Leave only OFF nodes in  self.NODES_TO_ON. 
        # Here we also leave Unknown state nodes untouched.
        tmp_list = list()
        tmp_list = self.NODES_TO_ON[:]
        for node in tmp_list:
            if self.STATES.has_key(node):
                if self.STATES[node] != 0:
                    self.NODES_TO_ON.remove(node)

        # Leave only ON nodes in self.NODES_TO_OFF
        # Here we also leave Unknown state nodes untouched.
        tmp_list = self.NODES_TO_OFF[:]
        for node in tmp_list:
            if self.STATES.has_key(node):
                if self.STATES[node] != 1:
                    self.NODES_TO_OFF.remove(node)

        return


    # Turns on ON-able OFF nodes
    def try_on(self, nodes_to_on):
        for node in nodes_to_on:
            if self.STATES[node] == 1: # Already ON
                continue
            if self.on_able(node):
                change_state.change_state().change_state(node, 'ON')
                print "Turn-On command sent (Turned-ON) " + node
            else:
                print "Cannot turn on " + node + " for now"


    # Turns off OFF-able ON nodes
    def try_off(self, nodes_to_off):
        for node in nodes_to_off:
            if self.STATES[node] == 0: # Already OFF
                continue
            if self.off_able(node):
                change_state.change_state().change_state(node, 'OFF')
                print "Turn off command sent (Turned off) " + node
            else:
                print "Cannot turn off " + node + " for now"


    # Checks if an OFF node is ON-able (necessary childs are ON)
    def on_able(self, node):

        if not self.DEP_RUN_ON.has_key(node):
            print "No RUN-ON-dependency found for node " + node
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
#                print childs
                return 1
 #       print childs
        return 0

    

    # Checks if an ON node is OFF-able (necessary childs are ON)
    def off_able(self, node):
        if not self.DEP_OFF.has_key(node):
            print "No OFF-dependency found for node " + node
            return 0
        
        # When the first occurence of all nodes in any of clause os ON, return 1
        # We also need to check if given "node" is parent of any other ON node by "RUN_DEP". 
        # In this case, we cannot turn off the given node. 
        childs = self.DEP_OFF[node]
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

    
    
    def main(self):

#        print self.DEP_RUN_ON
        print "NODES TO ON and their states: "
        for node in self.tmp_nodestoon:
            if self.STATES.has_key(node):
                print node + ": " + str(self.STATES[node])
            else:
                print node + ": state unwritten"
        print "\n\n"

        print "NODES TO OFF and their states: "
        for node in self.tmp_nodestooff:
            if self.STATES.has_key(node):
                print node + ": " + str(self.STATES[node])
            else:
                print node + ": state unwritten"
        print "\n\n"

        self.try_on(self.NODES_TO_ON)
        self.try_off(self.NODES_TO_OFF)

        return


if __name__ == "__main__":
    sys.exit(try_on_off().main())
