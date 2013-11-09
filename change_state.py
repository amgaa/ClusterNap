#! /usr/bin/python

"""  
 Changes state of a node. 
 OFF -> ON
 ON  -> OFF
 For now just change the value of nodes in the folder "state/{service, physical}/"
 If node does not exists, just create it. 
"""

import os, sys, re
import get_dependency

# Temporary state changing functions. 
# In reality, they should really change the state of real nodes 
# by getting necessary information from corresponding config folders.

class change_state:
    def __init__(self):
        self.CUR_DIR        = os.path.dirname(os.path.abspath(__file__))
        self.STATE_DIR_PHYS = self.CUR_DIR + "/state/physical/"
        self.STATE_DIR_SERV = self.CUR_DIR + "/state/service/"
        self.TYPE           = {}
        self.TYPE           = get_dependency.get_dependency().get_type()
        
    def change_state(self, name, to_state):
        
        if  to_state != 'ON' and to_state != 'OFF':
            print "Error: Unknown to_state: " + to_state
            return -1

        if not self.TYPE.has_key(name):
            print "Error: Cannot change state. Node " + name + " is not defined in config folder! "
            return -1
        
        if  self.TYPE[name] == "physical":
            return self.change_physical(name, to_state)
        elif self.TYPE[name] == "service":
            return self.change_service(name, to_state)
        else:
            print "Unknown type of node: " + kind
            return -1

        
    def change_physical(self, name, to_state):
        f = open( self.STATE_DIR_PHYS + name, "w")
        if to_state == "ON":
            f.write("1\n")
        elif to_state == "OFF":
            f.write("0\n")
        else:
            f.write("-1\n")


    def change_service(self, name, to_state):
        f = open( self.STATE_DIR_SERV + name, "w")
        if to_state == "ON":
            f.write("1\n")
        elif to_state == "OFF":
            f.write("0\n")
        else:
            f.write("-1\n")


    def main(self, argv):
        if len(argv) != 3:
            print "Usage of change_state.py: "
            print "./change_state.py <Node_name> <to_state>"
            return
        
        args     = argv
        node     = argv[1]
        to_state = argv[2]
        self.change_state(node, to_state)



if __name__ == "__main__":
    sys.exit(change_state().main(sys.argv))
