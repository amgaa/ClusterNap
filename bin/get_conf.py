#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' 
This program gets the configurations of nodes from corresponding files.
'''

import sys, os, re
import itertools
import time

class get_conf:

    def __init__(self):
        self.CONF_DIR        = os.path.dirname(os.path.abspath(__file__)) + "/../config/"
	self.NODE_CONF_DIR   = self.CONF_DIR + "nodes/" 
	self.NODE_CONF_FILES = [f for f in os.listdir(self.NODE_CONF_DIR) if f.endswith('.conf')]
        self.COMM_CONF_DIR   = self.CONF_DIR + "/commands/"   
        self.COMM_CONF_FILES = os.listdir(self.COMM_CONF_DIR) 
        self.STATE_DIR       = os.path.dirname(os.path.abspath(__file__)) + "/../state/nodes/"

        # Gets command informations from respective COMM_CONF_FILES
        self.COMMANDS = {} # Dictionary of commands defined in COMM_CONF_FOLDER
        for comm in self.COMM_CONF_FILES:
            f = open(self.COMM_CONF_DIR + comm)
            self.COMMANDS[comm] = f.readline().split('\n')[0]

        self.CONFIG = {}
	for conf_file in self.NODE_CONF_FILES:
		conf_file = self.NODE_CONF_DIR + conf_file
		self.CONFIG.update(self.get_conf(conf_file))

        self.ON_COMMANDS = {}
        self.ON_COMMANDS = self.get_on_command()
        self.OFF_COMMANDS = {}
        self.OFF_COMMANDS = self.get_off_command()


    # Returns  hash table of:
    # commands[name] = [{'host': "", 'user':"", 'command':""}, {'host': "", 'user':"", 'command':""} ... ]        
    def get_on_command(self):
        on_commands = {} 
        tmp_command = {}
        tmp_COMM = ""
        tmp_ARGS = ""

        for node in self.CONFIG.keys():
            tmp_command = {}

            # Check if on_command is defined 
            if not self.CONFIG[node].has_key("on_command") or\
                    self.CONFIG[node]["on_command"].strip() == "":
                print "Node " + node + " has node on_command defined."
                continue

            commands = self.CONFIG[node]["on_command"].split("|")

            for cmd in commands:
                cmd = cmd.split(",")

                # Check if on_command is defined correctly
                if len(cmd) != 3:
                    print "node " + node + "\'s on_command definition is incorrect"
                    continue 

                tmp_command["host"]    = cmd[0].strip()
                tmp_command["user"]    = cmd[1].strip()
                tmp_COMM               = cmd[2].split("!")[0].strip()
                tmp_ARGS               = cmd[2].strip().split("!")[1:]
                tmp_command["command"] = self.generate_command(tmp_COMM, tmp_ARGS)
            
            if on_commands.has_key(node):
                on_commands[node].append(tmp_command)
            else:
                on_commands[node] = []
                on_commands[node].append(tmp_command)
            
        return on_commands
 
    # Returns  hash table of:
    # commands[name] = [{'host': "", 'user':"", 'command':""}, {'host': "", 'user':"", 'command':""} ... ]
    def get_off_command(self):
        off_commands = {} 
        tmp_command = {}
        
        for node in self.CONFIG.keys():
            tmp_command = {}
            
            # Check if on_command is defined 
            if not self.CONFIG[node].has_key("off_command") or\
                    self.CONFIG[node]["off_command"].strip() == "":
                print "Node " + node + " has node off_command defined."
                continue

            commands = self.CONFIG[node]["off_command"].split("|")

            for cmd in commands:
                cmd = cmd.split(",")

                # Check if on_command is defined correctly
                if len(cmd) != 3:
                    print "node " + node + "\'s off_command definition is incorrect"
                    continue 

                tmp_command["host"]    = cmd[0].strip()
                tmp_command["user"]    = cmd[1].strip()
                tmp_COMM               = cmd[2].split("!")[0].strip()
                tmp_ARGS               = cmd[2].strip().split("!")[1:]
                tmp_command["command"] = self.generate_command(tmp_COMM, tmp_ARGS)
            
            if off_commands.has_key(node):
                off_commands[node].append(tmp_command)
            else:
                off_commands[node] = []
                off_commands[node].append(tmp_command)
            
        return off_commands


    # Gets real commands from given COMM and ARGS
    # Example: 
    #           COMM = ssh $ARG1@$ARG2 $ARG3
    #           ARGS = ['root', 'localhost', 'shutdown -h now'] 
    # then this function returns a string which looks like
    #           ssh root@localhost shutdown -t now
    #    
    def generate_command(self, comm_name, arglist):
        # If command is not defined
        if not self.COMMANDS.has_key(comm_name):
            print "Error: Command " + comm_name + " is not defined in " + self.COMM_CONF_DIR + ". Please define it there"
            exit(1)
        # If number of arguments does not match
#        if self.COMMANDS[comm_name].count("$") != len(arglist):
#            print "Error: Number of arguments for command \"" + comm_name + "\" does not match."
#            print "Argument list is: "
#            print arglisti
#            print "Number of arguments for command " + comm_name + " is:"
#            print self.COMMANDS[comm_name].count("$ARG")
#            exit(1)

        command = self.COMMANDS[comm_name]

        for i in range(0, len(arglist)):
            command = command.replace( "$ARG" + str(i+1) , arglist[i].strip() )

        # Check some errors
        if "$ARG" in command:
            print "Command definition error: Arguments defined in " +  self.NODE_CONF_DIR + " does not match for command " + comm_name

            exit(1)

        return command
            

    # Parses config file and returns hash table of config
    # config[node] = {'name': 'NodeA', 'address':'192.168...', 'run_dependency': ... }

    def get_conf(self, filename):
        head_types = ["name", "type", "address", "run_dependencies", "on_dependencies", "off_dependencies", "on_command", "off_command"]
        nodes    = {}
        tmp_nodes = {}

        f = open(filename, "r")

#        for line in f:
#        line=f.readline()
        line = self.get_line(f)
#        print line
        while line:
        
            if "{" in line and "define" in line: # Start of definition
                line = self.get_line(f)
                continue
#                print "START"
            elif "}" in line:                    # End of definition
                if not tmp_nodes.has_key("name"):
                    print "Node definition error. Please check your config file."
                    exit(1)
                # Get multiple lines if defined by expessions like [A-B, C ..]
                for i in range(0, len(tmp_nodes["name"])):
                    tmp_node = {}
                    for key in tmp_nodes:
                        if len(tmp_nodes[key]) == 1: # Has expression or not!
                            tmp_node[key] = tmp_nodes[key][0]
                        elif len(tmp_nodes[key]) == len(tmp_nodes["name"]):
                            tmp_node[key] = tmp_nodes[key][i]
                        else:
                            print "Configuration error!. Number of items inside [] does not match in " + key
                            exit(1)
                    nodes[tmp_node["name"]] = tmp_node
                tmp_nodes = {}
#                print "END"
            else:                                # Body of definition
                head, body = line.split(":")
                head = head.strip()
                body = body.strip()
                body = self.create_lines(body)
                tmp_nodes[head] = body


#            line=f.readline()
            line=self.get_line(f)

        return nodes

    # Gets line from config file
    # Ignores comments
    # Concatenates lines if ends with "\"
    # returns string
    def get_line(self, f):
        line = f.readline()
        if not line:
            return 
        line = line.strip()

        # Ignore comment-outed or empty line
        if line[:1] == "" or line[:1] == "#": 
        #    continue
            line = self.get_line(f)
        if not line:
            return

        # Remove comments
        line = line.split("#")
        line = line[0].strip()
        
        # When line ends with "\", get next line and concatenate it
        if line.endswith("\\"):
            line = line[:-1]
            line += self.get_line(f)
#        print line
        return line
        


    # Create power state files in ClusterNap/states/  folder.
    # Remove file which are not defined in config. 
    def create_state_files(self):

        # Remove state files whose node is not define in config 
        old_state_files = os.listdir(self.STATE_DIR)
        for state_file in old_state_files:
            if state_file not in self.CONFIG.keys():
                print "Removing state file, because its node is not defined: " + state_file 
                os.unlink(self.STATE_DIR + state_file)

        # Create state files whose node is defined in config, but state file is not created yet. 
        for node in self.CONFIG.keys():
            if not os.path.isfile(self.STATE_DIR + node):
                print "Creating following state file: " + node 
                f = open(self.STATE_DIR + node, 'w')
                f.write("-1\n")
                f.close()
                os.chmod(self.STATE_DIR + node, 0666)

    # Gets items in config and returns their list
    # Input ex: "120-123, 145, 147"
    # return  : ["120", "121", "122", "123", "145", "147"]
    def get_items(self, exprs):
        if not exprs:
            return
        
        itemlist = list()
        itemstr = map( str.strip, exprs.split(","))

        for items in itemstr:
            items = map(str.strip, items.split("-"))

            if len(items) == 1:
                itemlist.append(items[0]) # Can be digit and string

            elif         len(items) == 2    \
                     and items[0].isdigit() \
                     and items[1].isdigit():    # can only be integer
                for i in range(int(items[0]), int(items[1]) + 1 ):
                    itemlist.append(str(i).zfill(len(items[1])))
            else:
                print "Error in config. Unknown config: " + exprs
                print "Expression inside [] might be wrong: " + exprs
                exit(1)
                
        return itemlist

    # Gets item expressions from string.
    # Item expressions are written inside brackets [expr1, expr2, ...]
    # Each line of exprstr should only contain one pair of brackets "[ ... ]"  <--- Now multiple is ok, hopefully
    def get_exprs(self, exprstr):
        exprs = list()
        exprs = re.findall(r"\[(.+?)\]", exprstr)
        if exprs == []: # empty
            return

        return exprs
#        return expr.group(1)


    # Gets a line with expressions.
    # Ex: "foo[100-101, 105] [A, C, D]"
    # Ret: ["foo100 A", "foo101 C", "foo105 D"]
    def create_lines(self, line):
        lines   = list()
        items2D = list()
        exprs   = self.get_exprs(line)

        #If no expression        
        if not exprs:           
            lines.append(line)
            return lines
        
        # Create table of each items
        for expr in exprs:
            items = self.get_items(expr)
            items2D.append(items)
            # Number of items in each bracket should match!
            if len(items) != len(items2D[0]):
                print "Configuration error: Number of items in different brackets does not match!"
                print "Following may help:"
                print items
                print items2D[0]
                exit(1)

        # Create list of N lines. N is number of items in single bracket [] 
        for i in range(0, len(items2D[0])):
            lines.append(line)

        # Replace 
        for items in items2D:
            for i in range(0, len(items)):
                # replace items[i] in lines[i]
                lines[i] = re.sub(r"\[(.+?)\]", items[i], lines[i], 1)
        
        return lines

        
    def main(self):

        self.create_state_files()
        
#        for node in self.CONFIG:
#            print node
#	print self.CONFIG
        print "ON COMMANDS"
        for node in self.CONFIG:
            print node + " : " + self.CONFIG[node]["on_command"]
        print "OFF COMMANDS"
        for node in self.CONFIG:
            print node + " : " + self.CONFIG[node]["off_command"]
 
#        for command in self.get_off_command():
#            print command
#        print self.get_items("120-125, charlie, 240")
#        print self.get_expr("10.0.0.[120-140, 650]")
#        print self.get_expr("10.0.0.[120-140, 65] 192.[168].0.1")
#        print self.create_lines("100.0.0.[120-122, 125]")
#        print self.create_lines("100.0.0.[fdjhg-23]")
        return

if __name__ == "__main__":
    sys.exit(get_conf().main())
