#! /usr/bin/python
#

import os, sys, re
import get_min_graph, get_status

class on_or_off:
    def __init__ (self):
        self.MIN_GRAPH      = get_min_graph.get_min_graph().main()
        self.STATUSES       = get_status.get_status().main() 

    # Returns nodes that are required to be turned-ON. (REQUESTED && NOT ON)
    def nodes2on(self):
        tmp_min_graph = list()
        tmp_min_graph = self.MIN_GRAPH[:]
        for node in self.MIN_GRAPH:
            if self.is_ON(node):
                tmp_min_graph.remove(node)
        return tmp_min_graph

    # Returns nodes that are unnecessary to be ON. (NOT-REQUESTED && ON)
    def nodes2off(self):
        tmp_min_graph = list()
        for node in self.STATUSES.keys():
            if node not in self.MIN_GRAPH:
                if self.is_ON(node):
                    tmp_min_graph.append(node)
        return tmp_min_graph

    # Checks if a node is ON. 
    def is_ON(self, node):
        if not self.STATUSES.has_key(node):
            print "Node \"" + node + "\"'s status could not be found in the status folder" 
            return 0
        if self.STATUSES[node] == 1:
            return 1
        elif self.STATUSES[node] == 0:
            return 0
        else:
            return -1


    def main(self):
        print "nodes2ON: "
        print self.nodes2on()
        print "nodes2OFF: "
        print self.nodes2off()
        return

if __name__ == "__main__":
    sys.exit(on_or_off().main())
