#!/usr/bin/python
# -*- coding: utf-8 -*-

''' 
This program gets current states of nodes from states/ folder and updates xdot file's nodes' colors.
'''

import sys, os, re
import itertools
import time
import get_conf
import get_state
import get_dependency
import get_on_off

class update_xdot:
    def __init__(self):
	self.XDOT_FILE  = os.path.dirname(os.path.abspath(__file__)) + "/../graphs/CN.xdot"       
        self.CONFIG = {}
        self.CONFIG = get_conf.get_conf().CONFIG
        self.REQUEST_DIR             = os.path.dirname(os.path.abspath(__file__))
        self.REQUEST_DIR            += "/../requested/nodes/"
        self.NODES_REQUESTED    = os.listdir(self.REQUEST_DIR)

        self.STATES                  = {}
        self.STATES                  = get_state.get_state().main()

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


    def change_xdot(self):
        # Read from previously generated xdot file
        with open(self.XDOT_FILE, 'r') as file:
            data = file.readlines()

            
        for i in range(0,len(data)):
            line = data[i]
            if line.split()[0].strip() in self.NODES\
                    and not "->" in line:
                line = self.edit_line(line)

                data[i] = line

        # Write to new xdot file
        with open( self.XDOT_FILE[:-5] + "_updated.xdot", 'w') as file:
            file.writelines( data )


    # Edits colors and fillcolors according to node's state
    def edit_line(self, line):
        node = line.split()[0].strip()

        match1 = re.search(r'color=\w*', line)
        match1 = match1.group()[6:]
        match2 = re.search(r'fillcolor=\w*', line)
        match2 = match2.group()[10:]
        
        # Change color and fill color according to node's status adn requests. 
        if node in self.NODES_REQUESTED:
            color = "red, penwidth=3"
        elif node in self.NODES2ON and node not in self.NODES2OFF:
            color = "orange, penwidth=3"
        elif node in self.NODES2OFF:
            color = "green, penwidth=3"
        else:
            color = "black"


        if self.STATES.has_key(node) and self.STATES[node] == 1:
            fillcolor = "yellow"
        elif self.STATES.has_key(node) and self.STATES[node] == 0:
            fillcolor = "blue"
        else:
            fillcolor = "grey"

        line = line.replace(match1, color)
        line = line.replace(match2, fillcolor)

        return line


    def find_sub_string(raw_string, start_marker, end_marker):
        return re.sub(
            r'(?<={}).*?(?={})'.format(re.escape(start_marker), re.escape(end_marker)),
            lambda m: m.group().strip().replace(' ', '_'),
            raw_string)

    def main(self):
        
        self.change_xdot()
        return

if __name__ == "__main__":
    sys.exit(update_xdot().main())
    
