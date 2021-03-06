#! /usr/bin/env python
# -*- coding: utf-8 -*-

''' 
This program gets the dependencies of nodes from corresponding files.

Returns a hash table of { node: [dependency list] } .
Dependency list is in boolean CNF form. 
'''

import sys, os, re
import itertools
import time
import get_conf
import logset

class get_dependency:

    def __init__(self):
        self.log      = logset.get("get_dep_event", "event.log")
        self.errorlog = logset.get("get_dep_error", "error.log")
        self.NODES = {}
        self.NODES = get_conf.get_conf().NODES
        self.run_deps        = {}
        self.on_deps         = {}
        self.off_deps        = {}

    def get_run_dep(self):
        for node in self.NODES.keys():
            tmp_body = list()

            # When no RUN-dependency is defined for the node
            if not self.NODES[node].has_key("run_dependencies"):
                self.NODES[node]["run_dependencies"] = ''

            body = self.NODES[node]["run_dependencies"].split("|")
            for items in body:
                items = items.split(",")
                items = [item.strip() for item in items]
                tmp_body.append(items)
                if tmp_body == [['']]: # When a node does not have any dependencies
                    tmp_body = []

            self.run_deps[node] = tmp_body
        return self.run_deps

    def get_on_dep(self):
        for node in self.NODES.keys():
            tmp_body = list()

            if not self.NODES[node].has_key("on_dependencies"):
                self.NODES[node]["on_dependencies"] = ''

            body = self.NODES[node]["on_dependencies"].split("|")
            for items in body:
                items = items.split(",")
                items = [item.strip() for item in items]
                tmp_body.append(items)
                if tmp_body == [['']]: # When a node does not have any dependencies
                    tmp_body = []

            self.on_deps[node] = tmp_body

            for clause in tmp_body:
                for dep_node in clause:
                    if node == dep_node and not 'localhost' == node:
                        msg = "Node cannot be ON-dependent on itself!"
                        msg += "\n"
                        msg += "Node '" + node + "' has ON-dependent on itself! Please fix it!"
                        print msg
                        self.errorlog.error(msg)
        return self.on_deps

    def get_off_dep(self):
        for node in self.NODES.keys():
            tmp_body = list()

            if not self.NODES[node].has_key("off_dependencies"):
                self.NODES[node]["off_dependencies"] = ''

            body = self.NODES[node]["off_dependencies"].split("|")
            for items in body:
                items = items.split(",")
                items = [item.strip() for item in items]
                tmp_body.append(items)
                if tmp_body == [['']]: # When a node does not have any dependencies
                    tmp_body = []

            self.off_deps[node] = tmp_body
        return self.off_deps

    def get_run_on_dep(self):
        on_deps = self.get_on_dep()
        deps = {}
        deps = self.get_run_dep()

        for node in deps.keys():
      	  
            if on_deps.has_key(node):

                if deps[node] == []:  #Otherwise, it returns wrong value. Does not do cartesian product when it is empty. 
		    deps[node] = on_deps[node]
		
                # Get the cartesian product of two dependencies
#                product = [ x+y for x in deps[node] for y in on_deps[node]]
                product = [ x+y for x in on_deps[node] for y in deps[node]]

                # Remove some items which occur more than once in the same clause
                tmp_product = []
                for clause in product:
                    tmp_clause = []
                    for elem in clause:
                        if not elem in tmp_clause:
                            tmp_clause.append(elem)
                    tmp_product.append(tmp_clause)
                deps[node] = tmp_product
            
        # If on dependency have some nodes whoch run_dep does not have, add that too
        for node in on_deps.keys():
            if not deps.has_key(node):
                deps[node] = on_deps[node]

        return deps


    def get_run_off_dep(self):
        off_deps = self.get_off_dep()
        deps = {}
        deps = self.get_run_dep()

        for node in deps.keys():
            if off_deps.has_key(node):

                if deps[node] == []:  #Otherwise, it returns wrong value. Does not do cartesian product when it is empty. 
		    deps[node] = off_deps[node]
		
                # Get the cartesian product of two dependencies
#                product = [ x+y for x in deps[node] for y in on_deps[node]]
                product = [ x+y for x in off_deps[node] for y in deps[node]]

                # Remove some items which occur more than once in the same clause
                tmp_product = []
                for clause in product:
                    tmp_clause = []
                    for elem in clause:
                        if not elem in tmp_clause:
                            tmp_clause.append(elem)
                    tmp_product.append(tmp_clause)
                deps[node] = tmp_product
            
        # If off dependency have some nodes whoch run_dep does not have, add that too
        for node in off_deps.keys():
            if not deps.has_key(node):
                deps[node] = off_deps[node]
        return deps


    def main(self, argv):
        self.args = argv

        print "NEW OFF DEPENDENCIES:"
        for item in get_dependency().get_off_dep().items():
            print item
        print "\n\n"

        print "NEW RUN DEPENDENCIES:"
        for item in get_dependency().get_run_dep().items():
            print item
        print "\n\n"

        print "NEW ON DEPENDENCIES:"
        for item in get_dependency().get_on_dep().items():
            print item
        print "\n\n"

        print "NEW RUN ON DEPENDENCIES:"
        for item in get_dependency().get_run_on_dep().items():
            print item
    
        return
    
if __name__ == "__main__":
    sys.exit(get_dependency().main(sys.argv))
