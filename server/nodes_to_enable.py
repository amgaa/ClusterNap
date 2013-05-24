#! /usr/bin/python
#

import os, sys, re
import get_min_graph, get_status

class nodes_to_enable:
    def __init__ (self):
        self.MIN_GRAPH      = get_min_graph.get_min_graph().necc_nodes()
        self.STATUSES       = get_status.get_status().main() 

    # Returns nodes that are required to be turned-ON. (REQUESTED && NOT ON)
    def nodes(self):
        tmp_min_graph = list()
        tmp_min_graph = self.MIN_GRAPH[:]
        for node in self.MIN_GRAPH:
            if self.is_ON(node):
                tmp_min_graph.remove(node)
        return tmp_min_graph


    def is_ON(self, node):
        for pair in self.STATUSES:
#            print pair[1]
            if pair[0] == node:
                if pair[1] == 1:
                    return 1
                else: 
                    return 0
        print "Node \"" + node + "\"s status could not find" 
        return 0

    def main(self):
        return self.nodes()

if __name__ == "__main__":
    sys.exit(nodes_to_enable().main())
