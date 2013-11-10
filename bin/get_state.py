#! /usr/bin/python


'''
Returns: A hash table of {node: State}


This programs gets nodes' state information from "state/" folder and returns their values. 
'''

import os, sys, re

class get_state:
    def __init__ (self):
        self.STATE_DIR             = os.path.dirname(os.path.abspath(__file__))
        self.STATE_DIR            += "/../state/"
        self.SERV_STATE_DIR        = self.STATE_DIR + "nodes/"
        self.NODES_SERV_STATE_DIR  = os.listdir(self.SERV_STATE_DIR)
        self.STATES                = {}

    #Returns a dictionary of  node:state pairs
    def all_service_states(self):
        for node in self.NODES_SERV_STATE_DIR:
            self.STATES[node] = self.service_state(node)

    # Returns: 
    #  1 if ON, 
    #  0 if OFF, 
    # -1 if unknown, 
    def service_state(self, name):

        if name not in self.NODES_SERV_STATE_DIR:
            print "Node name \"" + name + "\" is not in the folder \"" + self.SERV_STATE_DIR + "\""
            return -1

        f = open( self.SERV_STATE_DIR + name, "r" )
        state = f.readline()
        state = state.strip()

        if state == "1":
            return 1
        elif state == "0":
            return 0
        else:
            print "Node \"" + name + "\" has unknown state: \"" + state + "\""
            return -1


    # Returns statuses of physical nodes and service nodes independently. 
    # Output: 
    #             (States_phys, States_serv)
    def main(self):
#        self.all_physical_states() 
        self.all_service_states()
        return self.STATES
#       return get_state().all_physical_states() + get_state().all_service_states()


if __name__ == "__main__":
    sys.exit(get_state().main())
#    sys.exit(get_state().main(sys.argv))
