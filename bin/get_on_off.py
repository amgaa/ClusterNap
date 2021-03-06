#! /usr/bin/env python
#

''' 
 Returns: 
            List of OFF-nodes that should be ON: 
            List of ON-nodes that can be OFF: 


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
import get_conf
import logset

class get_on_off:
    def __init__ (self):
        # Get logger
        self.log      = logset.get("get_on_off_event", "event.log")
        self.errorlog = logset.get("get_on_off_error", "error.log")
        self.REQUEST_DIR         = os.path.dirname(os.path.abspath(__file__))
        self.REQUEST_DIR        += "/../requested/nodes/"

        self.NODES_REQUESTED     = os.listdir(self.REQUEST_DIR)
	self.NODES	         = get_conf.get_conf().NODES

        self.STATES              = {}
#        self.STATES              = get_state.get_state().main()
        self.STATES              = get_state.get_state().STATES.copy()
        self.NODES_REQUESTED_ON  = list()
        self.NODES_REQUESTED_OFF = list()
        self.ON_NODES            = list()
        self.OFF_UNKNOWN_NODES   = list()

        self.DEP_RUN_ON          = {}
        self.DEP_RUN             = {}
        self.DEP_OFF             = {}
        
        
	# Check if non-defined node is requested
	for node in self.NODES_REQUESTED:
            if node not in self.NODES.keys():
                print "Error: Non-defined node requested: " + node
                self.errorlog.error("Error: Non-defined node requested: " + node)
        # Get ON nodes
        for node in self.STATES.keys():
            if self.STATES[node] == 1:
                self.ON_NODES.append(node)

        # Get OFF or UNKNOWN nodes
        for node in self.STATES.keys():
            if self.STATES[node] == 0 or self.STATES[node] == -1 :
                self.OFF_UNKNOWN_NODES.append(node)

        # Get the states of requested nodes
        for node in self.NODES_REQUESTED:
            if self.STATES.has_key(node):
                if self.STATES[node] == 1:
                    self.NODES_REQUESTED_ON.append(node)
                else:
                    # Here we take OFF or UNKNOWN state as only OFF.
                    # Later on, need to reconsider this. 
                    self.NODES_REQUESTED_OFF.append(node)

        
        self.DEP_RUN_ON  = get_dependency.get_dependency().get_run_on_dep()
        self.DEP_RUN     = get_dependency.get_dependency().get_run_dep()
        self.DEP_OFF     = get_dependency.get_dependency().get_off_dep()
        self.DEP_RUN_OFF = get_dependency.get_dependency().get_run_off_dep()
        

    # Pseudo Algorithm. All dirty codes in the main() should be changed to this function below. 
    # For now, do not have time to do it with writing my thesis :)
    def on_on_nodes(D_run, D_on, D_off, State_min, State_current):
        Nodes_to_on  = set(self.OFF_UNKNOWN_NODES) & State_min
        Nodes_to_off = set(self.ON_NODES) - Nodes_to_on
        Nodes_to_on  = Nodes_to_on | min_power_state(self.DEP_RUN_ON, Nodes_to_on)
        Nodes_to_on  = Nodes_to_on | min_power_state(self.DEP_RUN_OFF, Nodes_to_off)
        Nodes_to_on  = Nodes_to_on - Nodes_to_off

        for node in Nodes_to_on:
            if not any(all_members_on(clause) for clause in D_run_on[node]):
                Nodes_to_on.remove(node)
                
        for node in Nodes_to_off:
            if not any(all_members_on(clause) for clause in D_off[node]):
                Nodes_to_off.remove(node)

        for node in Nodes_to_off:
            if another_run_dependent_node(node):
                Nodes_to_off.remove(node)

        if not State_min <= Nodes_to_on:
            return on_off_nodes(D_run, D_on, D_off, State_min | Nodes_to_on, State_current)

        return Nodes_to_on, Nodes_to_off

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
	finals_to_off	   = list()	
        nodes_tmp_on       = list()
        

        # Get neccessary nodes to make requested ON nodes 
        necc_run_on  = self.necc_run_on(    necc_run_on, \
                                    self.DEP_RUN_ON, \
                                    self.DEP_RUN, \
                                    self.NODES_REQUESTED_OFF)
        necc_run_on.sort()


        # Get neccessary nodes to keep requested ON nodes 
        necc_run     = self.necc(   necc_run, \
                                    self.DEP_RUN, \
                                    self.NODES_REQUESTED_ON)
        necc_run.sort()


        # Get nodes that are unnecessarily being ON
        # We should turn-off these nodes
        for node in self.ON_NODES:
            if node not in (necc_run_on + necc_run):
                nodes_to_off.append(node)

        # Get nodes that should be ON to turn off above unnecessary nodes
        nodes_to_on_to_off  = self.necc(necc_off, self.DEP_OFF, nodes_to_off)
        t_list = list()
	for node in nodes_to_on_to_off:
            childs = list()
            if self.DEP_OFF.has_key(node):
                childs = self.DEP_OFF[node]
            if childs:
                for child in childs:
                    for chi in child:
                        if chi in nodes_to_on_to_off and chi not in t_list:
                            t_list.append(chi)
            # Below part should be reconsidered! Or not?! :) <-- This is for some unintended situation.
            # For example, when a node is ON but its ON/RUN depending node(s) is/are not actually ON. 
            if self.DEP_RUN_ON.has_key(node):
                childs = self.DEP_RUN_ON[node]
            if childs:
                for child in childs:
                    for chi in child:
                        if chi in nodes_to_on_to_off and chi not in t_list:
                            t_list.append(chi)

        nodes_to_on_to_off = t_list[:]
        
 
        print ":::::::::::::Nodes to on to off::::::::::::::"
        print nodes_to_on_to_off
        print ":::::::::::::::::::::::::::::::::::::::::::::\n"
        
        # Nodes that should be ON
        print "NECC_RUN_ON:"
        print necc_run_on

        print "NECC_RUN:"
        print necc_run


	# Get nodes that are still should be ON (temporarily),
        # because a RUN-dependent child is still ON.
        # This operation should be optimized further!
        nodes_tmp_on = list()
        t_list = list()
        childs = list()
        for node in self.ON_NODES:

            if self.DEP_RUN.has_key(node):
                childs = self.DEP_RUN[node]

            if childs == []:
                childs = [[]]
            childs = self.remove_nodes(childs, self.OFF_UNKNOWN_NODES)
            best_childs = self.best_childs(childs)

            for child in best_childs:
                nodes_tmp_on.append(child)


                
#        for node in (necc_run_on + necc_run + nodes_to_on_to_off ):
        for node in ( necc_run_on + necc_run + nodes_to_on_to_off + nodes_tmp_on ):
            if node not in finals_to_on:
                finals_to_on.append(node)
        finals_to_on.sort()

	for node in nodes_to_off:
	    if node not in finals_to_on:
                finals_to_off.append(node)
	finals_to_off.sort()	

        print ":::::::::::::::Requeste nodes:::::::::::::::::"
        for node in self.NODES_REQUESTED:
            print node
        print ":::::::::::::End of requested nodes::::::::::::\n"
        
        print ":::::::::::::::Final nodes to ON:::::::::::::::"
        for node in finals_to_on:
            print node
        print "::::::::::::End of Final nodes to ON:::::::::::\n"

        print "::::::::::::::::::Nodes to OFF:::::::::::::::::"
        for node in finals_to_off:
            print node
        print "::::::::::::::End of nodes to OFF::::::::::::::\n"


        return finals_to_on, finals_to_off #, self.STATES #, self.DEP_RUN_ON, self.DEP_OFF


    # takes dependency and requested nodes, 
    # returns what other nodes are also needed to be ON (true)
    # This function can be replaced by any good and fast Pseudo-Boolean solver. 
    def necc(self, necc, dependency, requested):
        tmp_necc = list()
        childs   = list()
        necc    += requested
        
        for node in requested:
            if dependency.has_key(node):
                childs = dependency[node]
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
            if dependency.has_key(node):
                childs = dependency[node]
            if childs: 
                childs     = self.remove_nodes(childs, necc)
                tmp_necc   = self.best_childs(childs)
                # Trial:
#                print "NODE: " + node
#                print "BEST CHILD (before): "
#                print tmp_necc
                tmp_on  = [x for x in tmp_necc if self.STATES.has_key(x) and self.STATES[x] == 1]
                tmp_off = [x for x in tmp_necc if self.STATES.has_key(x) and self.STATES[x] != 1]

#                print "BEST CHILD (after): "
#                print tmp_necc
                necc = self.necc_run_on(necc, dependency, run_dependency, tmp_off) 
                necc = self.necc(necc, run_dependency, tmp_on) 

        return necc


    # Chooses best childs from CNForm childs  (childsA OR childsB OR childsC ...)
    def best_childs(self, childs):
        if len(childs) == 0:
            return
        return min(childs, key=len)

    
    # remove nodes, which are already in a list ( for ex. "self.NECC"), from CNF form lists
    def remove_nodes(self, CNF, necc):
        if len(CNF) == 0:
            return 
        for clause in CNF:
            for node in necc:
                if node in clause:
                    clause.remove(node)
        return CNF

if __name__ == "__main__":
    sys.exit(get_on_off().main())
