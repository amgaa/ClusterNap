#! /usr/bin/python
#
# This program should keeps track of power status of all physical nodes
# and running status of service nodes. 

import os, sys, re

class status_monitor:
    def __init__ (self):
        self.STATE_DIR      = os.path.dirname(os.path.abspath(__file__))
        self.STATE_DIR     += "/state/"
        self.PHYS_STATE_DIR = self.STATE_DIR + "physical/"
        self.SERV_STATE_DIR = self.STATE_DIR + "service/"

    #Returns a list of  node:state pairs
    def all_physical_states(self):
        return 0

    def all_service_states(self):
        return 0

    # Returns: 
    #  1 if ON, 
    #  0 if OFF, 
    # -1 if unknown, 
    def physical_state(self, name):
        # Error handler should used here!
        f = open( self.PHYS_STATE_DIR + name, "r" )
        if not f:
            return -1

        for state in f:
            state = state.strip()
            if state == "1":
                return 1
            elif sate == "0":
                return 0
            else:
                return -1

    def service_state(self, name):
        return 0

    def main(self, argv):
        print "argv: "
        print argv
        print status_monitor().physical_state(argv[1])
        return 0



if __name__ == "__main__":
    sys.exit(status_monitor().main(sys.argv))
