#! /usr/bin/python
# -*- coding: utf-8 -*-

''' 
This program gets the dependencies of nodes from corresponding files.

Returns a hash table of { node: [dependency list] } .
Dependency list is in boolean CNF form. 
'''

import sys, os, re
import itertools
import time

class get_dependency:

    def __init__(self):
        self.DEPDIR        = os.path.dirname(os.path.abspath(__file__))
        self.DEPDIR       += "/dependency/"

        self.DEPDIR_PHYS     = self.DEPDIR      + "/physical/" 
        self.DEPDIR_PHYS_RUN = self.DEPDIR_PHYS + "/run/" 
        self.DEPDIR_PHYS_ON  = self.DEPDIR_PHYS + "/on/" 
        self.DEPDIR_PHYS_OFF = self.DEPDIR_PHYS + "/off/" 

        self.DEPDIR_SERV     = self.DEPDIR      + "/service/" 
        self.DEPDIR_SERV_RUN = self.DEPDIR_SERV + "/run/" 
        self.DEPDIR_SERV_ON  = self.DEPDIR_SERV + "/on/" 
        self.DEPDIR_SERV_OFF = self.DEPDIR_SERV + "/off/" 

        self.RUN_DEPS_PHYS = list()
        self.RUN_DEPS_SERV = list()
        self.ON_DEPS_PHYS  = list()
        self.ON_DEPS_SERV  = list()
        self.OFF_DEPS_PHYS = list()
        self.OFF_DEPS_SERV = list()

        # Get dependency file names from corresponding folders
        self.RUN_DEPS_PHYS = os.listdir( self.DEPDIR_PHYS_RUN )
        self.RUN_DEPS_SERV = os.listdir( self.DEPDIR_SERV_RUN )
        self.ON_DEPS_PHYS  = os.listdir( self.DEPDIR_PHYS_ON  )
        self.ON_DEPS_SERV  = os.listdir( self.DEPDIR_SERV_ON  )
        self.OFF_DEPS_PHYS = os.listdir( self.DEPDIR_PHYS_OFF )
        self.OFF_DEPS_SERV = os.listdir( self.DEPDIR_SERV_OFF )

        # Get dep files which only has '.dep' extension
        self.RUN_DEPS_PHYS[:] = [ dep for dep in self.RUN_DEPS_PHYS if dep[-4:] == '.dep' ] 
        self.RUN_DEPS_SERV[:] = [ dep for dep in self.RUN_DEPS_SERV if dep[-4:] == '.dep' ]
        self.ON_DEPS_PHYS[:]  = [ dep for dep in self.ON_DEPS_PHYS  if dep[-4:] == '.dep' ]
        self.ON_DEPS_SERV[:]  = [ dep for dep in self.ON_DEPS_SERV  if dep[-4:] == '.dep' ]
        self.OFF_DEPS_PHYS[:] = [ dep for dep in self.OFF_DEPS_PHYS if dep[-4:] == '.dep' ]
        self.OFF_DEPS_SERV[:] = [ dep for dep in self.OFF_DEPS_SERV if dep[-4:] == '.dep' ]

        self.phys_nodes      = {}  # list() # Physical nodes and their children
        self.serv_nodes      = {}  # list() # Service nodes and their children
        self.right_nodes     = list() # Nodes which we consider when controlling cluster power state
        self.TYPE            = {}


    # Checks whether a node is "physical" or "service"
    # Returns dictionary of all nodes written in config dir and their types
    def get_type(self):
        types     = {}
        phys_nodes = list()
        serv_nodes = list()
        phys_nodes = self.get_phys_run_on_dep().keys()
        phys_nodes += self.get_phys_off_dep().keys()

        serv_nodes = self.get_serv_run_on_dep().keys()
        serv_nodes += self.get_serv_off_dep().keys()

        for phys_node in phys_nodes:
            types[phys_node] = 'physical'
        for serv_node in serv_nodes:
            types[serv_node] = 'service'

        return types
            
    # Returns combination RUN and ON dependencies of physical nodes
    def get_phys_run_on_dep(self):
        deps = {}
        deps = self.get_phys_run_dep()
        deps.update( self.get_phys_on_dep() )
        return deps

    # Returns combination RUN and ON dependencies of service nodes
    def get_serv_run_on_dep(self):
        deps = {}
        deps = self.get_serv_run_dep()
        deps.update( self.get_serv_on_dep() )
        return deps

    # Returns RUN dependencies of physical nodes
    def get_phys_run_dep(self):
        deps = {}
        for name in self.RUN_DEPS_PHYS:
            deps.update(self.get_phys_dep(self.DEPDIR_PHYS_RUN + name))
        return deps    

    # Returns RUN dependencies of service nodes
    def get_serv_run_dep(self):
        deps = {}
        for name in self.RUN_DEPS_SERV:
            deps.update(self.get_serv_dep(self.DEPDIR_SERV_RUN + name))
        return deps    

    # Returns ON dependencies of physical nodes
    def get_phys_on_dep(self):
        deps = {}
        for name in self.ON_DEPS_PHYS:
            deps.update(self.get_phys_dep(self.DEPDIR_PHYS_ON + name))
        return deps    

    # Returns ON dependencies of service nodes
    def get_serv_on_dep(self):
        deps = {}
        for name in self.ON_DEPS_SERV:
            deps.update(self.get_serv_dep(self.DEPDIR_SERV_ON + name))
        return deps    

    # Returns OFF dependencies of physical nodes
    def get_phys_off_dep(self):
        deps = {}
        for name in self.OFF_DEPS_PHYS:
            deps.update(self.get_phys_dep(self.DEPDIR_PHYS_OFF + name))
        return deps    

    # Returns OFF dependencies of service nodes
    def get_serv_off_dep(self):
        deps = {}
        for name in self.OFF_DEPS_SERV:
            deps.update(self.get_serv_dep(self.DEPDIR_SERV_OFF + name))
        return deps    

    def get_phys_dep(self, filename):
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
                    if self.phys_nodes.has_key(pair[0]):  # When the same node has multiple dep files, we take cartesian product. Bad depedency writing may lead to longer computation time!!!
                        product = [ x+y for x in self.phys_nodes[pair[0]] for y in pair[1]]
                        self.phys_nodes[pair[0]] = product
                    else:
                        self.phys_nodes[pair[0]] = pair[1]

                else:
                    print "Unknown Syntax: " + head.strip()
                    exit(1)
        f.close()
        return self.phys_nodes

    # Gets service nodes from the corresponding config file (service.dep)
    def get_serv_dep(self, filename):        
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
                        product = [ x+y for x in self.serv_nodes[pair[0]] for y in pair[1]]
                        self.serv_nodes[pair[0]] = product
                    else:
                        self.serv_nodes[pair[0]] = pair[1]

                else:
                    print "Unknown Syntax: " + head.strip()
                    exit(1)
        f.close()
        return self.serv_nodes
    

    def main(self, argv):
        self.args = argv
        print "services RUN_ON_DEP:  " 
        for item in get_dependency().get_serv_run_on_dep().items():
            print item
        print "physical nodes RUN_ON_DEP:  "
        for item in get_dependency().get_phys_run_on_dep().items():
            print item
        print "physical nodes RUN_DEP:  "
        for item in get_dependency().get_phys_run_dep().items():
            print item
        print "services RUN_DEP:  " 
        for item in get_dependency().get_serv_run_dep().items():
            print item

        return

    
if __name__ == "__main__":
    sys.exit(get_dependency().main(sys.argv))
