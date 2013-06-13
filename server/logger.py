#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, re
import time
import networkx as nx

""" 
 This class takes care of selecting the right nodes.
 Main algorithm should be kind of complex since it has to 
 take care of which nodes to choose from multiple possible
 options such as those including "OR" operation. 
 When selecting, the algorithm should consider power comsumption 
 of each nodes and and present status of each node etc. 
 
 For now lets keep it as simple as possible (2013-05-15)

"""

class get_dependency:

    def __init__(self):
        self.CONFDIR        = os.path.dirname(os.path.abspath(__file__))
        self.CONFDIR       += "/config/"
        self.DEPENDENCY_PHYSICAL = "physical_run.dep"
        self.DEPENDENCY_SERVICE  = "service_run.dep"
        self.Graph          = nx.DiGraph()
        self.phys_nodes      = list() # Physical nodes and their children
        self.serv_nodes      = list() # Service nodes and their children
        self.right_nodes     = list() # Nodes which we consider when controlling cluster power state

    #Gets physical nodes from the corresponding config file (physical.dep)
    def get_phys_nodes(self):
        f = open(self.CONFDIR + self.DEPENDENCY_PHYSICAL, "r")
        
        for line in f:
            line = line.strip()

            # Ignore comment-outed or empty line
            if line[:1] != "" and line[:1] != "#": 

                head, body = line.split(":")
                head = head.strip()

                if head == "node": 
                    pair = list()
                    pair.append(body.strip())

                elif head == "depends":
                    tmp_body = list()
                    body = body.split("|")
                    for items in body:
                        items = items.split(",")
                        items = [item.strip() for item in items]
                        tmp_body.append(items)

                    pair.append(tmp_body)
                    self.phys_nodes.append(pair)
                else:
                    print "Unknown Syntax: " + head.strip()
                    exit(1)

        return self.phys_nodes

    # Gets service nodes from the corresponding config file (service.dep)
    def get_serv_nodes(self):        
        f = open(self.CONFDIR + self.DEPENDENCY_SERVICE, "r")
        
        for line in f:
            line = line.strip()

            # Skip comment-outed or empty linse
            if line[:1] != "" and line[:1] != "#":

                head, body = line.split(":")
                head = head.strip()

                if head == "service": 
                    pair = list()
                    pair.append(body.strip())

                elif head == "depends":
                    tmp_body = list()
                    body = body.split("|")
                    for items in body:
                        items = items.split(",")
                        items = [item.strip() for item in items]
                        tmp_body.append(items)

                    pair.append(tmp_body)
                    self.serv_nodes.append(pair)
                else:
                    print "Unknown Syntax: " + head.strip()
                    exit(1)

        return self.serv_nodes
    

    def main(self, argv):
        self.args = argv
        # print get_graph().get_physical().edges(data=True)
        print "services:  " 
        print get_dependency().get_serv_nodes()
        print "physical nodes:  "
        print get_dependency().get_phys_nodes()



if __name__ == "__main__":
    sys.exit(get_dependency().main(sys.argv))
