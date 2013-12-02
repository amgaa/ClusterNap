#! /usr/bin/python


'''
Returns: A hash table of {node: State}


This programs gets nodes' state information from "state/" folder and returns their values. 
'''

import os, sys, re
import logset

class get_state:
    def __init__ (self):
        # Get logger
        self.log      = logset.get("get_state_event", "event.log")
        self.errorlog = logset.get("get_state_error", "error.log")
        self.STATE_DIR             = os.path.dirname(os.path.abspath(__file__))
        self.STATE_DIR            += "/../state/nodes/"
        self.NODES_IN_STATE_DIR  = os.listdir(self.STATE_DIR)
        self.STATES                = {}

    #Returns a dictionary of  node:state pairs
    def all_node_states(self):
        for node in self.NODES_IN_STATE_DIR:
            self.STATES[node] = self.node_state(node)

    # Returns: 
    #  1 if ON, 
    #  0 if OFF, 
    # -1 if unknown, 
    def node_state(self, name):

        if name not in self.NODES_IN_STATE_DIR:
            print "Node state file \"" + name + "\" is not in the folder \"" + self.STATE_DIR + "\""
            self.errorlog.error("Node state file \"" + name + "\" is not in the folder \"" + self.STATE_DIR + "\"")
            return -1

        f = open( self.STATE_DIR + name, "r" )
        state = f.readline()
        state = state.strip()

        if state == "1":
            return 1
        elif state == "0":
            return 0
        else:
            print "Node \"" + name + "\" has unknown state: \"" + state + "\""
            self.log.warn("Node \"" + name + "\" has unknown state: \"" + state + "\"")
            return -1


    # Returns statuses of nodes
    # Output: 
    def main(self):
        self.all_node_states()
        return self.STATES


if __name__ == "__main__":
    sys.exit(get_state().main())
