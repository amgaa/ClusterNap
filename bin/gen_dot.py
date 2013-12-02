#! /usr/bin/python
#

import os, sys, re
import itertools
import get_dependency
import get_on_off
import get_state

class gen_dot:
    def __init__ (self):
        self.REQUEST_DIR             = os.path.dirname(os.path.abspath(__file__))
        self.REQUEST_DIR            += "/../requested/nodes/"
        self.NODES_REQUESTED         = os.listdir(self.REQUEST_DIR)
	self.OUT_DIR		     = os.path.dirname(os.path.abspath(__file__)) + "/../graphs/"
	self.OUT_FILE		     = "CN.dot"
	
        self.STATES                  = {}
        self.STATES                  = get_state.get_state().STATES.copy()
#        self.STATES                  = get_on_off.get_on_off().STATES.copy()

        self.ON_DEP     = get_dependency.get_dependency().get_on_dep()
        self.RUN_DEP    = get_dependency.get_dependency().get_run_dep()
        self.OFF_DEP    = get_dependency.get_dependency().get_off_dep()

        self.NODES      = list()



        for node in self.RUN_DEP.keys():
            if node not in self.NODES:
                self.NODES.append(node)

        for node in self.ON_DEP.keys():
            if node not in self.NODES:
                self.NODES.append(node)

        for node in self.OFF_DEP.keys():
            if node not in self.NODES:
                self.NODES.append(node)


        self.NODES2ON, self.NODES2OFF = get_on_off.get_on_off().main()

    def main(self):

        print "REQUESTED:" 
        print self.NODES_REQUESTED
        print "\n"

        print "STATES:"
        print self.STATES
        print "\n"

        print "DEPS:"
        print self.ON_DEP
        print self.RUN_DEP
        print self.OFF_DEP
        print "\n"

        print "NODES TO ON:"
        print self.NODES2ON
        print "\n"

        print "NODES TO OFF:"
        print self.NODES2OFF

        self.gen_dot()

#    def write_edge(self, parent, child, color, ):
        

    def gen_dot(self):
        
#        f = open('CN.dot', 'w')
        f = open( self.OUT_DIR + self.OUT_FILE, 'w')
        
        f.write("digraph CN { \n")

        #Create color for nodes: ON -> yellow, OFF -> black, Unknown -> gray
        for node in self.NODES:
            f.write( "\"" + node + "\" [" )
            
            f.write("style=\"filled\"\t color=" )
            
            if node in self.NODES_REQUESTED:
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
        
        for node in self.ON_DEP.keys():
            n= 0 #For 
            for clause in self.ON_DEP[node]:
                f.write("\"" + node  +  "\" -> \"OR:ON:" + node + str(n) + "\" [color=red];\n") #Create OR operation diamond
                f.write("\"OR:ON:" + node + str(n) + "\" [shape=diamond, style=filled, label=\"\", height=.1, width=.1];\n   ")
                
                for child in clause:
                    f.write("\"OR:ON:" + node + str(n) + "\" -> \"" + child + "\" [color=red];\n")
                n = n+1

        for node in self.OFF_DEP.keys():
            n = 0 #For 
            for clause in self.OFF_DEP[node]:
                f.write("\"" + node  +  "\" -> \"OR:OFF:" + node + str(n) + "\" [color=blue];\n") #Create OR operation diamond
                f.write("\"OR:OFF:" + node + str(n) + "\" [shape=diamond, style=filled, label=\"\", height=.1, width=.1];\n   ")
                
                for child in clause:
                    f.write("\"OR:OFF:" + node + str(n) + "\" -> \"" + child + "\" [color=blue] ;\n")
                n = n+1

        for node in self.RUN_DEP.keys():
            n= 0 #For 
            for clause in self.RUN_DEP[node]:
                f.write("\"" + node  +  "\" -> \"OR:RUN:" + node + str(n) + "\";\n") #Create OR operation diamond
                f.write("\"OR:RUN:" + node + str(n) + "\" [shape=diamond, style=filled, label=\"\", height=.1, width=.1];\n   ")
                
                for child in clause:
                    f.write("\"OR:RUN:" + node + str(n) + "\" -> \"" + child + "\";\n")
                n = n+1

        f.write("}\n")
        f.close()
    

if __name__ == "__main__":
    sys.exit(gen_dot().main())
