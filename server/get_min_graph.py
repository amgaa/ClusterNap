#! /usr/bin/python
#
# This program gets minimum number of nodes which are required for requested nodes. 

import os, sys, re
import get_config

class get_min_graph:
    def __init__ (self):
        self.REQUEST_DIR             = os.path.dirname(os.path.abspath(__file__))
        self.REQUEST_DIR            += "/requested/"
        self.PHYS_REQUEST_DIR        = self.REQUEST_DIR + "physical/"
        self.SERV_REQUEST_DIR        = self.REQUEST_DIR + "service/"
        self.NODES_PHYS_REQUESTED    = os.listdir(self.PHYS_REQUEST_DIR)
        self.NODES_SERV_REQUESTED    = os.listdir(self.SERV_REQUEST_DIR)
        self.PHYS_DEP                = get_config.get_config().get_phys_nodes()
        self.SERV_DEP                = get_config.get_config().get_serv_nodes()
        self.DEP                     = self.PHYS_DEP + self.SERV_DEP
        self.NECC                    = list()

    # Returns statuses of physical nodes and service nodes independently. 
    # Output: 
    #             (States_phys, States_serv)
    def main(self):
        print "Requested nodes: "
        requested = list()
        necc = list()
        requested  = self.NODES_PHYS_REQUESTED + self.NODES_SERV_REQUESTED
        print requested
        print "Dependencies: "
        print self.DEP
        print "Necessary nodes: "
        necc = self.necc_nodes(requested)
        necc.sort()
        return necc


    # Necessary nodes to be ON to make requested nodes ON
    def necc_nodes(self, requested):
        
        # Here we should sort items in "requested" by the number of OR clauses they have.
        tmp_necc   = list()
        childs     = list()
        self.NECC += requested

        # The main algorithmic part
        # Depth first or width first traverce-r uzeh ? Whats their time complexity? (for length of at most 10 layer? )
        for node in requested:
            childs   = self.get_childs(self.DEP, node)
            if childs: 
                childs     = self.remove_nodes(childs, self.NECC)
                tmp_necc   = self.best_childs(childs)
                self.necc_nodes(tmp_necc) # <- Eniig daraa ni sain bodoh 

        return self.NECC



    # Chooses best childs from CNForm childs  (childsA OR childsB OR childsC ...)
    def best_childs(self, childs):
        if len(childs) == 0:
            return
        return min(childs, key=len)


    
    # remove nodes, which are already in a list "self.NECC", from CNF form lists
    def remove_nodes(self, CNF, necc):
        if len(CNF) == 0:
            return 
        for clause in CNF:
            for node in necc:
                if node in clause:
                    clause.remove(node)
        return CNF

        
    # Gets childs from dependency lists
    # This should be optimized by using hash table. 
    def get_childs(self, dep_list, parent):
        for dep in dep_list:
            if parent == dep[0]:
                return dep[1] # childs in CNForm


if __name__ == "__main__":
    sys.exit(get_min_graph().main())
