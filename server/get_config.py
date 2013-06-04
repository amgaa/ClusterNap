#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, re
import time
import networkx as nx

""" 
 For now lets keep it as simple as possible (2013-05-15)

"""

class get_config:

    def __init__(self):
        self.CONFDIR        = os.path.dirname(os.path.abspath(__file__))
        self.CONFDIR       += "/config/"
        self.RUN_DEPENDENCY_PHYSICAL = "physical_run.dep"
        self.RUN_DEPENDENCY_SERVICE  = "service_run.dep"
        self.ON_DEPENDENCY_PHYSICAL  = "physical_on.dep"
        self.ON_DEPENDENCY_SERVICE   = "service_on.dep"
        self.OFF_DEPENDENCY_PHYSICAL = "physical_off.dep"
        self.OFF_DEPENDENCY_SERVICE  = "service_off.dep"
        self.Graph           = nx.DiGraph()
        self.phys_nodes      = {}  # list() # Physical nodes and their children
        self.serv_nodes      = {}  # list() # Service nodes and their children
        self.right_nodes     = list() # Nodes which we consider when controlling cluster power state

    #Gets physical nodes from the corresponding config file (physical.dep)
    def get_phys_nodes(self):
        names = self.CONFDIR + self.RUN_DEPENDENCY_PHYSICAL, self.CONFDIR + self.ON_DEPENDENCY_PHYSICAL
        deps = {}
        for name in names:
            deps.update(self.get_phys_dep(name))
        return deps

    def get_serv_nodes(self):
        names = self.CONFDIR + self.RUN_DEPENDENCY_SERVICE, self.CONFDIR + self.ON_DEPENDENCY_SERVICE
        deps = {}
        for name in names:
            deps.update(self.get_serv_dep(name))
        return deps

    def get_phys_dep(self, filename):
#    def get_phys_nodes(self, filenames):
#        f = open(self.CONFDIR + self.RUN_DEPENDENCY_PHYSICAL, "r")
        f = open(filename, "r")
        
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
                        if tmp_body == [['']]: # When a node does not have any dependents, 
                            tmp_body = []      # make sure it has no dependents by making it empty instead of [['']]
                    pair.append(tmp_body)
                    if self.phys_nodes.has_key(pair[0]):
                        self.phys_nodes[pair[0]] += pair[1]
                    else:
                        self.phys_nodes[pair[0]] = pair[1]

                else:
                    print "Unknown Syntax: " + head.strip()
                    exit(1)
        f.close()
        return self.phys_nodes

    # Gets service nodes from the corresponding config file (service.dep)
    def get_serv_dep(self, filename):        
#        f = open(self.CONFDIR + self.RUN_DEPENDENCY_SERVICE, "r")
        f = open(filename, "r")
        
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
                    if self.serv_nodes.has_key(pair[0]):
                        self.serv_nodes[pair[0]] += pair[1]
                    else:
                        self.serv_nodes[pair[0]] = pair[1]

                else:
                    print "Unknown Syntax: " + head.strip()
                    exit(1)
        f.close()
        return self.serv_nodes
    

    def main(self, argv):
        self.args = argv
        # print get_graph().get_physical().edges(data=True)
        print "services:  " 
        print get_config().get_serv_nodes()
        print "physical nodes:  "
        print get_config().get_phys_nodes()


if __name__ == "__main__":
    sys.exit(get_config().main(sys.argv))
