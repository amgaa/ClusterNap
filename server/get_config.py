#! /usr/bin/python
# -*- coding: utf-8 -*-

''' 
This program gets the configurations of nodes from corresponding files.

Returns a hash table of nodes {node_name: {'on_script' , 
                                           'on_host'   , 
                                           'on_user'   ,
                                           'off_script',
                                           'off_host'  , 
                                           'off_user' 
                                           }}
'''

import sys, os, re
import itertools
import time

class get_config:

    def __init__(self):
        self.CONFDIR        = os.path.dirname(os.path.abspath(__file__))
        self.CONFDIR       += "/config/"

        self.CONFDIR_PHYS     = self.CONFDIR      + "/physical/" 
        self.CONFDIR_SERV     = self.CONFDIR      + "/service/" 

        self.CONFS_PHYS = list()
        self.CONFS_SERV = list()

        # Get config file names from corresponding folders
        self.CONFS_PHYS = os.listdir( self.CONFDIR_PHYS )
        self.CONFS_DEPS = os.listdir( self.CONFDIR_SERV )

        # Get config files which only has '.conf' extension
        self.CONFS_PHYS[:] = [ conf for conf in self.CONFS_PHYS if conf[-5:] == '.conf' ] 
        self.CONFS_SERV[:] = [ conf for conf in self.CONFS_SERV if conf[-5:] == '.conf' ]


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
        phys_nodes = self.get_phys_conf().keys()
        serv_nodes = self.get_serv_conf().keys()

        for phys_node in phys_nodes:
            types[phys_node] = 'physical'
        for serv_node in serv_nodes:
            types[serv_node] = 'service'

        return types

            
    # Returns RUN dependencies of physical nodes
    def get_phys_conf(self):
        confs = {}
        for name in self.CONFS_PHYS:
            confs.update(self.get_phys_conf(self.CONFDIR_PHYS + name))
        return confs    


    # Returns RUN dependencies of service nodes
    def get_serv_conf(self):
        confs = {}
        for name in self.CONFS_SERV:
            confs.update(self.get_serv_conf(self.CONFDIR_SERV + name))
        return confs    

    def get_phys_conf(self, filename):
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
    def get_serv_conf(self, filename):        
#        f = open(self.DEPDIR + self.RUN_DEPENDENCY_SERVICE, "r")
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
