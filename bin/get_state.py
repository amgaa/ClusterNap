#! /usr/bin/env python


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
        for node in self.NODES_IN_STATE_DIR:
            self.STATES[node] = self.node_state(node)
#	self.check()
    # Returns: 
    #  1 if ON, 
    #  0 if OFF, 
    # -1 if unknown, 
    def node_state(self, name):

        if name not in self.NODES_IN_STATE_DIR:
            print "Node state file \"" + name + "\" is not in the folder \"" + self.STATE_DIR + "\""
            self.errorlog.error("Node state file \"" + name + "\" is not in the folder \"" + self.STATE_DIR + "\"")
            return 1

        f = open( self.STATE_DIR + name, "r" )
        state = f.readline()
        state = state.strip()
        f.close()

        if state == "1":
            return 1
        elif state == "0":
            return 0
        else:
#            print "Node \"" + name + "\" has unknown state: \"" + state + "\""
#            self.log.warn("Node \"" + name + "\" has unknown state: \"" + state + "\"")
            return -1

    def set_state(self, nodename, state):

        if nodename not in self.NODES_IN_STATE_DIR:
            print "Node state file \"" + nodename + "\" is not in the folder \"" + self.STATE_DIR + "\""
            self.errorlog.error("Node state file \"" + nodename + "\" is not in the folder \"" + self.STATE_DIR + "\"")
            return -1

        on  = ['ON', 'on', 'On', '1', 1]
        off = ['OFF', 'off', 'Off', '0', 0]
        un  = ['UNKNOWN', 'Unknown', 'unknown', '-1', -1]

        if state in on:
            val = '1'
        elif state in off:
            val = '0'
        elif state in un:
            val = '-1'
        else:
            msg = "Unknown state given: " + str(state)
            print msg
            self.errorlog.error(msg)
            return 1

        try:
            f = open( self.STATE_DIR + nodename, "w" )
            f.write(val + '\n')
            f.close()

        except:
            print "Unknown error occured setting node state!"
            return -1

    def check(self):
        for name in self.STATES:
            if self.STATES[name] == -1:
                print "Node \"" + name + "\"\'s state is UNKNOWN."
                self.log.warn("Node \"" + name + "\"\'s state is UNKNOWN.")
        return
        
    # Returns statuses of nodes
    # Output: 
    def main(self):
#        return self.STATES
	return

if __name__ == "__main__":
    sys.exit(get_state().main())
