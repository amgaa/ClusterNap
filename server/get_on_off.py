#! /usr/bin/python
#

''' 
 Returns: 
            List of node that should be ON: 
            List of node that can be OFF: 


 Given the dependencies of all nodes (D), requested nodes (R) and current states of all nodes (S)
 This program gets minimum number of nodes which are required for requested nodes to be ON. 
 It also returns the list of nodes which we can turn-off. 
 However this program does not tell how to turn-on all of requested nodes, (i.e. by what order ...).
 action_on_off.py does this. 
'''

import os, sys, re
import itertools
import get_dependency
import get_state

class get_on_off:
    def __init__ (self):
        self.REQUEST_DIR             = os.path.dirname(os.path.abspath(__file__))
        self.REQUEST_DIR            += "/requested/"
        self.PHYS_REQUEST_DIR        = self.REQUEST_DIR + "physical/"
        self.SERV_REQUEST_DIR        = self.REQUEST_DIR + "service/"

        self.NODES_PHYS_REQUESTED    = os.listdir(self.PHYS_REQUEST_DIR)
        self.NODES_SERV_REQUESTED    = os.listdir(self.SERV_REQUEST_DIR)

        self.STATES                  = {}
        self.STATES                  = get_state.get_state().main()
        print self.STATES
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

        self.DEP_RUN_ON      = list()
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

#        print "self.STATES"
#        print self.STATES

#        print "PHYS REQ: "
#        print self.NODES_PHYS_REQUESTED
#        print "SERV REQ:"
#        print self.NODES_SERV_REQUESTED

#        print "PHYS REQ ON: "
#        print self.NODES_PHYS_REQUESTED_ON
#        print "SERV REQ ON:"
#        print self.NODES_SERV_REQUESTED_ON
#        print "PHYS REQ OFF: "
#        print self.NODES_PHYS_REQUESTED_OFF
#        print "SERV REQ OFF: "
#        print self.NODES_SERV_REQUESTED_OFF

        self.PHYS_RUN_ON_DEP = get_dependency.get_dependency().get_phys_run_on_dep().items()
        self.PHYS_RUN_DEP    = get_dependency.get_dependency().get_phys_run_dep().items()
        self.PHYS_OFF_DEP    = get_dependency.get_dependency().get_phys_off_dep().items()

        self.SERV_RUN_ON_DEP = get_dependency.get_dependency().get_serv_run_on_dep().items()
        self.SERV_RUN_DEP    = get_dependency.get_dependency().get_serv_run_dep().items()
        self.SERV_OFF_DEP    = get_dependency.get_dependency().get_serv_off_dep().items()

        self.SERV_RUN_ON_DEP = sorted(self.SERV_RUN_ON_DEP, key=lambda item: len(item[1]))
        self.SERV_RUN_DEP    = sorted(self.SERV_RUN_DEP,    key=lambda item: len(item[1]))
        self.SERV_OFF_DEP    = sorted(self.SERV_OFF_DEP,    key=lambda item: len(item[1]))

        self.DEP_RUN_ON      = self.PHYS_RUN_ON_DEP + self.SERV_RUN_ON_DEP
        self.DEP_RUN         = self.PHYS_RUN_DEP    + self.SERV_RUN_DEP
        self.DEP_OFF         = self.PHYS_OFF_DEP    + self.SERV_OFF_DEP
        
#        print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
#        print self.DEP_RUN_ON 
#        print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

    # Returns a pair of lists:
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

        # Get neccessary nodes to make requested ON nodes 
        necc_run_on  = self.necc_run_on(    necc_run_on, \
                                    self.DEP_RUN_ON, \
                                    self.DEP_RUN, \
                                    self.NODES_PHYS_REQUESTED_OFF +  self.NODES_SERV_REQUESTED_OFF)

        # Get neccessary nodes to keep requested ON nodes 
        necc_run     = self.necc(   necc_run, \
                                    self.DEP_RUN, \
                                    self.NODES_PHYS_REQUESTED_ON +  self.NODES_SERV_REQUESTED_ON)

        necc_run_on.sort()
        necc_run.sort()

        # Get nodes that are unnecessarily being ON
        # We should turn-off these nodes
        for node in self.ON_NODES:
            if node not in (necc_run_on + necc_run):
                nodes_to_off.append(node)

        # Get nodes that should be ON to turn off above unnecessary nodes
        nodes_to_on_to_off = self.necc(necc_off, self.DEP_OFF, nodes_to_off)
        print "START: NODES TO ON TO OFF"
        print nodes_to_on_to_off
        print "END:   NODES TO ON TO OFF"

        # What is above doing ??
#        for node in nodes_to_on_to_off:
#            if node not in necc_off:
#            if node not in nodes_to_off:
#                tmp_list.append(node)
#
#        nodes_to_on_to_off = tmp_list[:]
        
        
        # Nodes that should be ON (finally)
        print "NECC_RUN_ON:"
        print necc_run_on

        print "NECC_RUN:"
        print necc_run

        for node in (necc_run_on + necc_run + nodes_to_on_to_off):
            if node not in finals_to_on:
                finals_to_on.append(node)
        finals_to_on.sort()

        print ":::::::::::::::Requested nodes:::::::::::::::::"
        for node in self.NODES_PHYS_REQUESTED + self.NODES_SERV_REQUESTED:
            print node
        print ":::::::::::::End of requested nodes::::::::::::\n"
        
        print ":::::::::::::::Final nodes to ON:::::::::::::::"
        for node in finals_to_on:
            print node
        print "::::::::::::End of Final nodes to ON:::::::::::\n"

        print "::::::::::::::::::Nodes to OFF:::::::::::::::::"
        for node in nodes_to_off:
            print node
        print "::::::::::::::End of nodes to OFF::::::::::::::\n"

        
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


    # Same function as "necc". But takes OFF nodes as argument for DEP_RUN_ON
    def necc_run_on(self, necc, dependency, run_dependency, requested):
        tmp_necc = list()
        tmp_off  = list()
        tmp_on   = list()
        childs   = list()
        necc    += requested
        
        for node in requested:
            childs = self.get_childs(dependency, node)
            if childs: 
                childs     = self.remove_nodes(childs, necc)
                tmp_necc   = self.best_childs(childs)
                # Trial:
                print "NODE: " + node
                print "BEST CHILD (before): "
                print tmp_necc
                tmp_on  = [x for x in tmp_necc if self.STATES.has_key(x) and self.STATES[x] == 1]
                tmp_off = [x for x in tmp_necc if self.STATES.has_key(x) and self.STATES[x] != 1]
#                for tmp_node in tmp_necc:
#                    print "tmp_node: " + tmp_node
#                    print "tmp_state" 
#                    print self.STATES[tmp_node]
#                    if self.STATES.has_key(tmp_node) and self.STATES[tmp_node] == 1:
#                        tmp_necc.remove(tmp_node)
                print "BEST CHILD (after): "
                print tmp_necc
                self.necc_run_on(necc, dependency, run_dependency, tmp_off) 
                necc = self.necc(necc, run_dependency, tmp_on) 

        return necc


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
