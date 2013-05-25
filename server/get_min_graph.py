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
        requested  = self.NODES_PHYS_REQUESTED + self.NODES_SERV_REQUESTED
        print requested
        print "Dependencies: "
        print self.DEP
        print "Necessary nodes: "
        return self.necc_nodes( requested)


    # Necessary nodes to be ON to make requested nodes ON
    def necc_nodes(self, requested ):

        tmp_necc   = list()
        childs     = list()
        tmp_necc   = requested[:] # <- This list should be sorted such that one with least OR dependencies has higher priority. 
        
        # The main algorithmic part
        # This part has some logical flaw. It does not traverce through the child of child and so. 
        # Depth first or width first traverce-r uzeh ? Whats their time complexity? (for length of at most 10 layer? )
        while tmp_necc != [] :
            for node in tmp_necc:
                childs   = self.get_childs(self.DEP, node)
#                print "childs before remove: "
#                print childs
                if childs: 
                    self.NECC += tmp_necc
                    tmp_necc   = []
                    childs     = self.remove_nodes(childs, self.NECC)
                    tmp_necc   = self.best_childs(childs)
                    self.necc_nodes(tmp_necc) # <- Eniig daraa ni sain bodoh 
#                    print "tmp_necc: "
#                    print tmp_necc
#                    print "childs after remove: "
#                    print childs
#                    print "necc at this moment: "
                    print self.NECC
                else:
                    tmp_necc = []

        return self.NECC

    # Chooses best childs from CNForm childs  (childsA OR childsB OR childsC ...)
    def best_childs(self, childs):
        if len(childs) == 0:
            return
        return min(childs, key=len)
    

    # remove nodes, which are already in a list "necc", from CNF form lists
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
