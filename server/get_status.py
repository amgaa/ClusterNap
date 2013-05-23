#! /usr/bin/python
#
# This program should keeps track of power status of all physical nodes
# and running status of service nodes. 

import os, sys, re

class get_status:
    def __init__ (self):
        self.STATE_DIR             = os.path.dirname(os.path.abspath(__file__))
        self.STATE_DIR            += "/state/"
        self.PHYS_STATE_DIR        = self.STATE_DIR + "physical/"
        self.SERV_STATE_DIR        = self.STATE_DIR + "service/"
        self.NODES_PHYS_STATE_DIR  = os.listdir(self.PHYS_STATE_DIR)
        self.NODES_SERV_STATE_DIR  = os.listdir(self.SERV_STATE_DIR)

    #Returns a list of  node:state pairs
    def all_physical_states(self):
        physical = list()
        for node in self.NODES_PHYS_STATE_DIR:
            pair = list()
            pair.append(node)
            pair.append(self.physical_state(node))
            physical.append(pair)
        return physical

    def all_service_states(self):
        service = list()
        for node in self.NODES_SERV_STATE_DIR:
            pair = list()
            pair.append(node)
            pair.append(self.service_state(node))
            service.append(pair)
        return service

    # Returns: 
    #  1 if ON, 
    #  0 if OFF, 
    # -1 if unknown, 
    def physical_state(self, name):

        if name not in self.NODES_PHYS_STATE_DIR:
            print "Node name \"" + name + "\" is not in the folder \"" + self.PHYS_STATE_DIR + "\""
            return -1

        f = open( self.PHYS_STATE_DIR + name, "r" )
        state = f.readline()
        state = state.strip()

        if state == "1":
            return 1
        elif state == "0":
            return 0
        else:
            print "Node \"" + name + "\" has unknown state: \"" + state + "\""
            return -1

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
    def main(self, argv):
        return get_status().all_physical_states(), get_status().all_service_states()


if __name__ == "__main__":
    sys.exit(get_status().main(sys.argv))
