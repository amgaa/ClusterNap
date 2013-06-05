#! /usr/bin/python
#
# This program gets minimum number of nodes which are required for requested nodes. 

import os, sys, re
import itertools
import get_config

class get_min_graph:
    def __init__ (self):
        self.REQUEST_DIR             = os.path.dirname(os.path.abspath(__file__))
        self.REQUEST_DIR            += "/requested/"
        self.PHYS_REQUEST_DIR        = self.REQUEST_DIR + "physical/"
        self.SERV_REQUEST_DIR        = self.REQUEST_DIR + "service/"

        self.NODES_PHYS_REQUESTED    = os.listdir(self.PHYS_REQUEST_DIR)
        self.NODES_SERV_REQUESTED    = os.listdir(self.SERV_REQUEST_DIR)

        self.PHYS_RUN_ON_DEP = list()
        self.PHYS_RUN_DEP    = list()
        self.PHYS_OFF_DEP    = list()

        self.SERV_RUN_ON_DEP = list()
        self.SERV_RUN_DEP    = list()
        self.SERV_OFF_DEP    = list()

        self.PHYS_RUN_ON_DEP = get_config.get_config().get_phys_run_on_dep().items()
        self.PHYS_RUN_DEP    = get_config.get_config().get_phys_run_dep().items()
        self.PHYS_OFF_DEP    = get_config.get_config().get_phys_off_dep().items()

        self.SERV_RUN_ON_DEP = get_config.get_config().get_serv_run_on_dep().items()
        self.SERV_RUN_DEP    = get_config.get_config().get_serv_run_dep().items()
        self.SERV_OFF_DEP    = get_config.get_config().get_serv_off_dep().items()


#        self.PHYS_DEP = list()
#        self.SERV_DEP = list()
#        self.PHYS_DEP = ( get_config.get_config().get_phys_nodes().items())
#        self.PHYS_DEP = (sorted(self.PHYS_DEP, key=lambda item: len(item[1]) ) ) #Sort by the length of OR clauses a node has
#        self.SERV_DEP = ( get_config.get_config().get_serv_nodes().items())
#        self.SERV_DEP = (sorted(self.SERV_DEP, key=lambda item: len(item[1]) ))  #Sort by the length of OR clauses a node has
        self.DEP                     = list()
        self.DEP = self.PHYS_RUN_ON_DEP + self.SERV_RUN_ON_DEP
        print "MERGED DEP:"
        for dep in self.DEP:
            print dep
        self.NECC                    = list()


    def main(self):
        requested = list()
        necc = list()
        requested  = self.NODES_PHYS_REQUESTED + self.NODES_SERV_REQUESTED

        print "Dependencies: "
        for dep in  self.DEP:
            print dep

        print "Requested nodes: "
        for node in requested:
            print node

        necc = self.necc_nodes(requested)
        necc.sort()

        print "Necessary nodes: "
        for node in necc:
            print node

        return necc


    # Necessary nodes to be ON to make requested nodes ON
    def necc_nodes(self, requested):
        
        # Here we should sort items in "requested" by the number of OR clauses they have.
        self.NECC += requested
        tmp_necc   = list()
        childs     = list()

        # The main algorithmic part
        # Depth first or width first traverce-r uzeh ? Whats their time complexity? (for length of at most 10 layer? )
        for node in requested:
#            if self.DEP.has_key(node):
            childs = self.get_childs(self.DEP, node)
            if childs: 
                childs     = self.remove_nodes(childs, self.NECC)
                tmp_necc   = self.best_childs(childs)
                self.necc_nodes(tmp_necc) 

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
