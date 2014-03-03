#! /usr/bin/env python

''' 
Returns OFF nodes those should be turned-ON and ON nodes those should be turned-OFF.
'''

import sys, os, re
import get_on_off
import get_state


class action_on_off:
    def __init__(self):
        self.NODES_TO_ON  = list()
        self.NODES_TO_OFF = list()
        self.STATES       = {}
        self.NODES_TO_ON, self.NODES_TO_OFF = get_on_off.get_on_off().main()
        self.tmp_nodestoon = self.NODES_TO_ON[:]
        self.tmp_nodestooff = self.NODES_TO_OFF[:]
#        self.STATES = dict(get_state.get_state().main())
        self.STATES = get_state.get_state().STATES.copy()
#        self.STATES = get_on_off.get_on_off().STATES.copy()
        self.OFF_NODES_TO_CHECK = list()
        self.ON_NODES_TO_CHECK = list()

        for node in self.NODES_TO_ON:
            if self.STATES[node] == 0: #OFF node to ON
                self.OFF_NODES_TO_CHECK.append(node)
        
        for node in self.NODES_TO_OFF:
            if self.STATES[node] == 1: #ON node to OFF
                self.ON_NODES_TO_CHECK.append(node)

    
    def main(self):
        print "ON nodes to check :"
        print self.ON_NODES_TO_CHECK
        print "OFF nodes to check :"
        print self.OFF_NODES_TO_CHECK
        
        return self.ON_NODES_TO_CHECK + self.ON_NODES_TO_CHECK


if __name__ == "__main__":
    sys.exit(action_on_off().main())
