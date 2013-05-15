#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, re
import time
import networkx as nx

# This class takes care of selecting the right nodes.
# Main algorithm should be kind of complex since it has to 
# take care of which nodes to choose from multiple possible
# options such as those including "OR" operation. 
# When selecting, the algorithm should consider power comsumption 
# of each nodes and and present status of each node etc. 
# 
# For now lets keep it as simple as possible (2013-05-15)

class get_right_nodes:

    def __init__(self):
        self.CONFDIR        = os.path.dirname(os.path.abspath(__file__))
        self.CONFDIR       += "/configs/"
        self.DEPENDENCY_PHYSICAL = "physical.dep"
        self.DEPENDENCY_SERVICE  = "service.dep"
        self.Graph          = nx.DiGraph()
        self.phys_nodes      = list() # Physical nodes and their children
        self.serv_nodes      = list() # Service nodes and their children
        self.right_nodes     = list() # Nodes which we consider when controlling cluster power state

    #Gets physical nodes from the corresponding config file
    def get_phys_nodes(self):
        f = open(self.CONFDIR + self.DEPENDENCY_PHYSICAL, "r")
        
        for line in f:
            line = line.strip()

            if line[:1] != "" and line[:1] != "#":   # Skip comment-outed or empty line
                pair = list()
                parent, childs = line.split(":")
                childs = childs.split(",")
                childs = [child.strip() for child in childs]
                pair.append(parent)
                pair.append(childs)
                self.phys_nodes.append(pair)
        return self.phys_nodes

    # Gets service nodes from the corresponding config file
    def get_serv_nodes(self):        
        f = open(self.CONFDIR + self.DEPENDENCY_SERVICE, "r")
        
        for line in f:
            line = line.strip()

            if line[:1] != "" and line[:1] != "#":   # Skip comment-outed or empty lines
                pair = list()
                parent, childs = line.split(":")
                childs = childs.split(",")
                childs = [child.strip() for child in childs]
                pair.append(parent)
                pair.append(childs)
                self.serv_nodes.append(pair)
        return self.serv_nodes
    
    # Gets the power status of physical nodes
    def get_phys_node_status(self):
        return 0
        
    # Gets the running status of service nodes
    def get_serv_node_status(self):
        return 0

    # Get the right graph informations.
    # The most IMPORTANT function of this class
    def get_right_nodes(self):

    def main(self, argv):
        self.args = argv
        # print get_graph().get_physical().edges(data=True)
        print get_right_nodes().get_serv_nodes()


class get_graph:
                # Add nodes to the Graph 
                # self.Graph.add_node(parent)
                # self.Graph.add_nodes_from(childs)
                # [self.Graph.add_edge(parent, child) for child in childs]
    


if __name__ == "__main__":
    sys.exit(get_right_nodes().main(sys.argv))
