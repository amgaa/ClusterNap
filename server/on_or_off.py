#! /usr/bin/python
#

import os, sys, re
import get_min_graph, get_status

class on_or_off:
    def __init__ (self):
        self.MIN_GRAPH      = get_min_graph.get_min_graph().necc_nodes()
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
        for pair in self.STATUSES:
            if pair[0] not in self.MIN_GRAPH:
                if self.is_ON(pair[0]):
                    tmp_min_graph.append(pair[0])
        return tmp_min_graph

    # 
    def is_ON(self, node):
        for pair in self.STATUSES:
#            print pair[1]
            if pair[0] == node:
                if pair[1] == 1:
                    return 1
                else: 
                    return 0
        print "Node \"" + node + "\"'s status could not be find in status folder" 
        return 0

    def main(self):
        print "nodes2ON: "
        print self.nodes2on()
        print "nodes2OFF: "
        print self.nodes2off()
        return

if __name__ == "__main__":
    sys.exit(on_or_off().main())
