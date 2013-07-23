#! /usr/bin/python
#

import os, sys, re
import itertools
import get_dependency
import get_state
import get_on_off

class gen_dot:
    def __init__ (self):
        self.REQUEST_DIR             = os.path.dirname(os.path.abspath(__file__))
        self.REQUEST_DIR            += "/requested/"
        self.PHYS_REQUEST_DIR        = self.REQUEST_DIR + "physical/"
        self.SERV_REQUEST_DIR        = self.REQUEST_DIR + "service/"

        self.NODES_PHYS_REQUESTED    = os.listdir(self.PHYS_REQUEST_DIR)
        self.NODES_SERV_REQUESTED    = os.listdir(self.SERV_REQUEST_DIR)

        self.STATES                  = {}
        self.STATES                  = get_state.get_state().main()

        self.PHYS_ON_DEP     = get_dependency.get_dependency().get_phys_on_dep()
        self.PHYS_RUN_DEP    = get_dependency.get_dependency().get_phys_run_dep()
        self.PHYS_OFF_DEP    = get_dependency.get_dependency().get_phys_off_dep()

        self.SERV_ON_DEP     = get_dependency.get_dependency().get_serv_on_dep()
        self.SERV_RUN_DEP    = get_dependency.get_dependency().get_serv_run_dep()
        self.SERV_OFF_DEP    = get_dependency.get_dependency().get_serv_off_dep()

        self.PHYS_NODES      = list()
        for node in self.PHYS_ON_DEP.keys():
            if node not in self.PHYS_NODES:
                self.PHYS_NODES.append(node)

        for node in self.PHYS_OFF_DEP.keys():
            if node not in self.PHYS_NODES:
                self.PHYS_NODES.append(node)

        for node in self.PHYS_RUN_DEP.keys():
            if node not in self.PHYS_NODES:
                self.PHYS_NODES.append(node)

        self.SERV_NODES      = list()
        for node in self.SERV_ON_DEP.keys():
            if node not in self.SERV_NODES:
                self.SERV_NODES.append(node)

        self.SERV_NODES      = list()
        for node in self.SERV_OFF_DEP.keys():
            if node not in self.SERV_NODES:
                self.SERV_NODES.append(node)

        self.SERV_NODES      = list()
        for node in self.SERV_RUN_DEP.keys():
            if node not in self.SERV_NODES:
                self.SERV_NODES.append(node)

        self.NODES           = self.PHYS_NODES + self.SERV_NODES

        self.NODES2ON, self.NODES2OFF = get_on_off.get_on_off().main()

    def main(self):

        print "REQUESTED:" 
        print self.NODES_PHYS_REQUESTED
        print self.NODES_SERV_REQUESTED
        print "\n"

        print "STATES:"
        print self.STATES
        print "\n"

        print "DEPS:"
        print self.PHYS_ON_DEP
        print self.SERV_ON_DEP
        print self.PHYS_RUN_DEP
        print self.SERV_RUN_DEP
        print self.PHYS_OFF_DEP
        print self.SERV_OFF_DEP
        print "\n"

        print "NODES TO ON:"
        print self.NODES2ON
        print "\n"

        print "NODES TO OFF:"
        print self.NODES2OFF

        print "PHYSICAL NODES:"
        print self.PHYS_NODES
        print "\n"

        print "SERVICE NODES:"
        print self.SERV_NODES
        print "\n"

        
        self.gen_dot()

#    def write_edge(self, parent, child, color, ):
        

    def gen_dot(self):
        
        f = open('CN.dot', 'w')
        
        f.write("digraph CN { \n")

        #Create color for nodes: ON -> yellow, OFF -> black, Unknown -> gray
        for node in self.NODES:
            f.write( "\"" + node + "\" [" )
            
            # If physical node, make it rectange
            if node in self.PHYS_NODES:
                f.write("shape=box,\t")

            f.write("style=\"filled\"\t color=" )
            
            if node in self.NODES_PHYS_REQUESTED + self.NODES_SERV_REQUESTED:
                f.write("red, penwidth=3, ")
            elif node in self.NODES2ON and node not in self.NODES2OFF:
                f.write("orange, penwidth=3, ")
            elif node in self.NODES2OFF:
                f.write("green, penwidth=3, ")
            else:
                f.write("black, ")

            f.write("fillcolor= ")
            

            if self.STATES.has_key(node) and self.STATES[node] == 1:
                f.write("yellow")
            elif self.STATES.has_key(node) and self.STATES[node] == 0:
                f.write("blue")
            else:
                f.write("grey")
            
            f.write("] ;\n")

                                

        #Create edges
        
        # SERVICES
        for node in self.SERV_ON_DEP.keys():
            n= 0 #For 
            for clause in self.SERV_ON_DEP[node]:
                f.write("\"" + node  +  "\" -> \"OR:ON:" + node + str(n) + "\" [color=red];\n") #Create OR operation diamond
                f.write("\"OR:ON:" + node + str(n) + "\" [shape=diamond, style=filled, label=\"\", height=.1, width=.1];\n   ")
                
                for child in clause:
                    f.write("\"OR:ON:" + node + str(n) + "\" -> \"" + child + "\" [color=red];\n")
                n = n+1

        for node in self.SERV_OFF_DEP.keys():
            n = 0 #For 
            for clause in self.SERV_OFF_DEP[node]:
                f.write("\"" + node  +  "\" -> \"OR:OFF:" + node + str(n) + "\" [color=blue];\n") #Create OR operation diamond
                f.write("\"OR:OFF:" + node + str(n) + "\" [shape=diamond, style=filled, label=\"\", height=.1, width=.1];\n   ")
                
                for child in clause:
                    f.write("\"OR:OFF:" + node + str(n) + "\" -> \"" + child + "\" [color=blue] ;\n")
                n = n+1

        for node in self.SERV_RUN_DEP.keys():
            n= 0 #For 
            for clause in self.SERV_RUN_DEP[node]:
                f.write("\"" + node  +  "\" -> \"OR:RUN:" + node + str(n) + "\";\n") #Create OR operation diamond
                f.write("\"OR:RUN:" + node + str(n) + "\" [shape=diamond, style=filled, label=\"\", height=.1, width=.1];\n   ")
                
                for child in clause:
                    f.write("\"OR:RUN:" + node + str(n) + "\" -> \"" + child + "\";\n")
                n = n+1


        # PHYSICAL NODES
        for node in self.PHYS_ON_DEP.keys():
            n= 0 #For 
            for clause in self.PHYS_ON_DEP[node]:
                f.write("\"" + node  +  "\" -> \"OR:ON:" + node + str(n) + "\" [color=red];\n") #Create OR operation diamond
                f.write("\"OR:ON:" + node + str(n) + "\" [shape=diamond, style=filled, label=\"\", height=.1, width=.1];\n   ")
                
                for child in clause:
                    f.write("\"OR:ON:" + node + str(n) + "\" -> \"" + child + "\" [color=red];\n")
                n = n+1
            
        for node in self.PHYS_OFF_DEP.keys():
            n= 0 #For 
            for clause in self.PHYS_OFF_DEP[node]:
                f.write("\"" + node  +  "\" -> \"OR:OFF:" + node + str(n) + "\" [color=blue];\n") #Create OR operation diamond
                f.write("\"OR:OFF:" + node + str(n) + "\" [shape=diamond, style=filled, label=\"\", height=.1, width=.1];\n   ")
                
                for child in clause:
                    f.write("\"OR:OFF:" + node + str(n) + "\" -> \"" + child + "\" [color=blue] ;\n")
                n = n+1


        for node in self.PHYS_RUN_DEP.keys():
            n= 0 #For 
            for clause in self.PHYS_RUN_DEP[node]:
                f.write("\"" + node  +  "\" -> \"OR:RUN:" + node + str(n) + "\";\n") #Create OR operation diamond
                f.write("\"OR:RUN:" + node + str(n) + "\" [shape=diamond, style=filled, label=\"\", height=.1, width=.1];\n   ")
                
                for child in clause:
                    f.write("\"OR:RUN:" + node + str(n) + "\" -> \"" + child + "\";\n")
                n = n+1



        f.write("}\n")
        f.close()
    

if __name__ == "__main__":
    sys.exit(gen_dot().main())
