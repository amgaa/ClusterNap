#! /usr/bin/python
#
# This program gets minimum number of nodes which are required for requested nodes. 

import os, sys, re
import itertools
import get_config
import get_status

class get_on_off:
    def __init__ (self):
        self.REQUEST_DIR             = os.path.dirname(os.path.abspath(__file__))
        self.REQUEST_DIR            += "/requested/"
        self.PHYS_REQUEST_DIR        = self.REQUEST_DIR + "physical/"
        self.SERV_REQUEST_DIR        = self.REQUEST_DIR + "service/"

        self.NODES_PHYS_REQUESTED    = os.listdir(self.PHYS_REQUEST_DIR)
        self.NODES_SERV_REQUESTED    = os.listdir(self.SERV_REQUEST_DIR)

        self.STATES                  = {}
        self.STATES                  = get_status.get_status().main()

        self.NODES_PHYS_REQUESTED_ON = list()
        self.NODES_SERV_REQUESTED_ON = list()
        self.NODES_PHYS_REQUESTED_OFF= list()
        self.NODES_SERV_REQUESTED_OFF= list()

        self.PHYS_RUN_ON_DEP = list()
        self.PHYS_RUN_DEP    = list()
        self.PHYS_OFF_DEP    = list()

        self.SERV_RUN_ON_DEP = list()
        self.SERV_RUN_DEP    = list()
        self.SERV_OFF_DEP    = list()

        self.DEP_RUN_O       = list()
        self.DEP_RUN         = list()
        self.DEP_OFF         = list()
        
        self.ON_NODES        = list()

#       self.NECC            = list()
        
        # Get the names of ON nodes
        for node in self.STATES.keys():
            if self.STATES[node] == 1:
                self.ON_NODES.append(node)

        # Get the states of requested nodes
        for node in self.NODES_PHYS_REQUESTED:
            if self.STATES.has_key(node):
                if self.STATES[node] == 1:
                    self.NODES_PHYS_REQUESTED_ON.append(node)
            else:
                # Here we take OFF or UNKNOWN state as only OFF. later need to reconsider this. 
                self.NODES_PHYS_REQUESTED_OFF.append(node)
        
        for node in self.NODES_SERV_REQUESTED:
            if self.STATES.has_key(node):
                if self.STATES[node] == 1:
                    self.NODES_SERV_REQUESTED_ON.append(node)
            else:
                # Here we take OFF or UNKNOWN state as only OFF. later need to reconsider this. 
                self.NODES_SERV_REQUESTED_OFF.append(node)
                
#        print "PHYS REQ ON: "
#        print self.NODES_PHYS_REQUESTED_ON
#        print "SERV REQ ON:"
#        print self.NODES_SERV_REQUESTED_ON
#        print "PHYS REQ OFF: "
#        print self.NODES_PHYS_REQUESTED_OFF
#        print "SERV REQ OFF: "
#        print self.NODES_SERV_REQUESTED_OFF

        self.PHYS_RUN_ON_DEP = get_config.get_config().get_phys_run_on_dep().items()
        self.PHYS_RUN_DEP    = get_config.get_config().get_phys_run_dep().items()
        self.PHYS_OFF_DEP    = get_config.get_config().get_phys_off_dep().items()

        self.SERV_RUN_ON_DEP = get_config.get_config().get_serv_run_on_dep().items()
        self.SERV_RUN_DEP    = get_config.get_config().get_serv_run_dep().items()
        self.SERV_OFF_DEP    = get_config.get_config().get_serv_off_dep().items()

        self.SERV_RUN_ON_DEP = sorted(self.SERV_RUN_ON_DEP, key=lambda item: len(item[1]))
        self.SERV_RUN_DEP    = sorted(self.SERV_RUN_DEP,    key=lambda item: len(item[1]))
        self.SERV_OFF_DEP    = sorted(self.SERV_OFF_DEP,    key=lambda item: len(item[1]))

        self.DEP_RUN_ON      = self.PHYS_RUN_ON_DEP + self.SERV_RUN_ON_DEP
        self.DEP_RUN         = self.PHYS_RUN_DEP    + self.SERV_RUN_DEP
        self.DEP_OFF         = self.PHYS_OFF_DEP    + self.SERV_OFF_DEP
        
#        print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
#        print self.DEP_RUN_ON 
#        print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

    # Returnsa pair of lists:
    # list 1: nodes that should be ON (currently ON or OFF) 
    # list 2: nodes that should be OFF (but currently are ON)
    def main(self):



        # Define necessary lists (variables)
        necc_run_on        = list()
        necc_run           = list()
        necc_off           = list()
        nodes_to_off       = list()
        nodes_to_on_to_off = list()
        tmp_list           = list()
        finals_to_on       = list()
        
        tmp_dep_run_on     = list()
        tmp_dep_run        = list()
        tmp_dep_off        = list()

#        tmp_dep_run_on     = self.DEP_RUN_ON[:]
#        tmp_dep_run        = self.DEP_RUN[:] 
#        tmp_dep_off        = self.DEP_OFF[:]

#        print "!!!!!!!XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
#        print tmp_dep_run_on 
  #      print "!!!!!!!XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

        # Get neccessary nodes to make requested OFF nodes 
        necc_run_on  = self.necc(    necc_run_on, \
                                    self.DEP_RUN_ON, \
#                                    tmp_dep_run_on, \
                                    self.NODES_PHYS_REQUESTED_OFF +  self.NODES_SERV_REQUESTED_OFF)

#        print "22222!!!!!!!XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
#        print tmp_dep_run_on 
#        print "22222!!!!!!!XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"


        # Get neccessary nodes to keep requested ON nodes 
        necc_run     = self.necc(   necc_run, \
                                    self.DEP_RUN, \
#                                    tmp_dep_run, \
                                    self.NODES_PHYS_REQUESTED_ON +  self.NODES_SERV_REQUESTED_ON)

        necc_run_on.sort()
        necc_run.sort()


        # Get nodes that are unnecessarily being ON
        # We should turn-off these nodes
        for node in self.ON_NODES:
            if node not in (necc_run_on + necc_run):
                nodes_to_off.append(node)

        # Get nodes that should be ON to turn off above unnecessary nodes
#        nodes_to_on_to_off = self.necc(necc_off, self.DEP_OFF, nodes_to_off)
        nodes_to_on_to_off = self.necc(necc_off, tmp_dep_off, nodes_to_off)
        for node in nodes_to_on_to_off:
            if node not in necc_off:
                tmp_list.append(node)

        nodes_to_on_to_off = tmp_list[:]
        
        # Nodes that should be ON (finally)
        for node in (necc_run_on + necc_run + nodes_to_on_to_off):
            if node not in finals_to_on:
                finals_to_on.append(node)
        finals_to_on.sort()

        print "requested nodes:"
        for node in self.NODES_PHYS_REQUESTED + self.NODES_SERV_REQUESTED:
            print node
        
        print "Necessary nodes RUN_ON: "
        for node in necc_run_on:
            print node

        print "Necessary nodes RUN: "
        for node in necc_run:
            print node

        print "Nodes to OFF:"
        for node in nodes_to_off:
            print node

        print "Nodes to ON to OFF:"
        for node in nodes_to_on_to_off:
            print node

        print "Final nodes to ON to OFF:"
        for node in finals_to_on:
            print node

        
        return finals_to_on, nodes_to_off #, self.STATES #, self.DEP_RUN_ON, self.DEP_OFF




    # takes dependency and requested nodes, 
    # returns what other nodes are also needed to be ON (true)
    # This function can be replaced by any good and fast Pseudo-Boolean solver. 
    def necc(self, necc, dependency, requested):
        tmp_necc = list()
        childs   = list()
        necc    += requested
        
        for node in requested:
            childs = self.get_childs(dependency, node)
            if childs: 
                childs     = self.remove_nodes(childs, necc)
                tmp_necc   = self.best_childs(childs)
                self.necc(necc, dependency, tmp_necc) 
        return necc

    # Necessary nodes to be ON to make requested nodes ON
#    def necc_nodes(self, requested):
        
        # Here we should sort items in "requested" by the number of OR clauses they have.
#        self.NECC += requested
#        tmp_necc   = list()
#        childs     = list()

        # The main algorithmic part
        # Depth first or width first traverce-r uzeh ? Whats their time complexity? (for length of at most 10 layer? )
#        for node in requested:
#            if self.DEP.has_key(node):
#            childs = self.get_childs(self.DEP, node)
#            if childs: 
#                childs     = self.remove_nodes(childs, self.NECC)
#                tmp_necc   = self.best_childs(childs)
#                self.necc_nodes(tmp_necc) 
#        return self.NECC


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
    sys.exit(get_on_off().main())
