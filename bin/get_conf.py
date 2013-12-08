#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' 
This program gets the configurations of nodes from corresponding files.
'''

import sys, os, re
import itertools
import time
import logset

class get_conf:

    def __init__(self):
        # Get logger
        self.log = logset.get("get_conf_event", "event.log")
        self.errorlog = logset.get("get_conf_error", "error.log")

        self.CONF_DIR        = os.path.dirname(os.path.abspath(__file__)) + "/../config/"
	self.CONF_FILES = [f for f in os.listdir(self.CONF_DIR) if f.endswith('.conf')]
        self.STATE_DIR       = os.path.dirname(os.path.abspath(__file__)) + "/../state/nodes/"

        # Gets command informations from respective COMM_CONF_FILES
        self.NODES    = {}
        self.COMMANDS = {} # Dictionary of commands defined in COMM_CONF_FOLDER
        self.TYPES    = {}

        # Get configurations for "nodes", "commands", and "types"
 	for conf_file in self.CONF_FILES:
            conf_file = self.CONF_DIR + conf_file
            tmp_nodes = {}
            tmp_comms = {}
            tmp_types = {}
            tmp_nodes, tmp_commands, tmp_types = self.get_conf(conf_file)
            self.NODES.update(tmp_nodes)
            self.COMMANDS.update(tmp_commands)
            self.TYPES.update(tmp_types)


    # Returns  hash table of:
    # commands[name] = [{'host': "", 'user':"", 'command':""}, {'host': "", 'user':"", 'command':""} ... ]        
    def get_on_command(self):
        on_commands = {} 
        tmp_command = {}
        tmp_COMM = ""
        tmp_ARGS = ""

        for node in self.NODES.keys():

            tmp_command = {}

            # Check if on_command is defined 
            if not self.NODES[node].has_key("on_command") or\
                    self.NODES[node]["on_command"].strip() == "":
                print "Node " + node + " has node on_command defined."
                continue

            commands = self.NODES[node]["on_command"].split("|")

            for cmd in commands:
                cmd = cmd.split(",")

                # Check if on_command is defined correctly
                if len(cmd) != 3:
                    print "Node " + node + "\'s on_command definition is incorrect"
                    self.errorlog.error("Node " + node + "\'s on_command definition is incorrect")
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
        
        for node in self.NODES.keys():
            tmp_command = {}
            
            # Check if on_command is defined 
            if not self.NODES[node].has_key("off_command") or\
                    self.NODES[node]["off_command"].strip() == "":
                print "Node " + node + " has node off_command defined."
                continue

            commands = self.NODES[node]["off_command"].split("|")

            for cmd in commands:
                cmd = cmd.split(",")

                # Check if on_command is defined correctly
                if len(cmd) != 3:
                    print "Node " + node + "\'s off_command definition is incorrect"
                    self.errorlog.error("Node " + node + "\'s off_command definition is incorrect")
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
            print "Error: Command " + comm_name + " is not defined in any config file. Please define it there"
            self.errorlog.error("Command " + comm_name + " is not defined in any config file. Please define it there")
            exit(1)

        command = self.COMMANDS[comm_name]["command_line"]

        for i in range(0, len(arglist)):
            command = command.replace( "$ARG" + str(i+1) , arglist[i].strip() )

        # Check some errors
        if "$ARG" in command:
            print "Command definition error: Arguments defined in " +  self.NODE_CONF_DIR + " does not match for command " + comm_name
            self.errorlog.error("Command definition error: Arguments defined in " +  self.NODE_CONF_DIR + " does not match for command " + comm_name)
            exit(1)

        return command
            

    # Parses config file and returns hash table of config
    # config[node] = {'name': 'NodeA', 'address':'192.168...', 'run_dependency': ... }

    def get_conf(self, filename):

        nodes    = {}
        commands = {}
        types    = {}

        f = open(filename, "r")
        line = self.get_line(f)
        while line:
        
            if "{" in line and "define" in line: # Start of definition
                if "node" in line:
                    # Get node(s)' config
                    nodes = self.get_object(f, nodes, filename)
                    
                elif "type" in line:
                    # Get type's config
                    types = self.get_object(f, types, filename)

                elif "command" in line:
                    # Get command's config
                    commands = self.get_object(f, commands, filename)

                else:
                    print "Configuration error: Unknown item definition in file: " + filename
                    self.errorlog.error("Configuration error: Unknown item definition in file: " + filename)
                    exit(1)

            line = self.get_line(f)

        return nodes , commands, types

    
    # Gets config of node(s)
    def get_object(self, f, nodes, filename):
        tmp_nodes = {}
        tmp_nodes = self.get_heads_bodies(f)
        nodes     = self.get_multiple(tmp_nodes, nodes)
        return nodes

    # Parses tmp_nodes to real multiple nodes
    # Ex:
    # Gets tmp_nodes which looks like:
    #            {"name": ["foo0", "foo1", "foo2"], "bar":"xxx"}
    # Adds:
    #
    #            {  
    #                 {"name":"foo0", "bar":"xxx"}, 
    #                 {"name":"foo1", "bar":"xxx"}, 
    #                 {"name":"foo2", "bar":"xxx"}    }
    #
    # to argument dictionary nodes

    def get_multiple(self, tmp_nodes, nodes):
        # Get multiple lines if defined by expressions like [A-B, C ..]
        # Assuming that each 
        for i in range(0, len(tmp_nodes["name"])):
            tmp_node = {}
            for key in tmp_nodes:
                if len(tmp_nodes[key]) == 1: # Has expression or not!
                    tmp_node[key] = tmp_nodes[key][0]
                elif len(tmp_nodes[key]) == len(tmp_nodes["name"]):
                    tmp_node[key] = tmp_nodes[key][i]
                else:
                    print "Configuration error!. Number of items inside [] does not match in config file: " + filename
                    self.errorlog.error("Configuration error!. Number of items inside [] does not match in config file: " + filename )
                    exit(1)
        
            # If a node with same name already defined:
            if nodes.has_key(tmp_node["name"]):
                print "Configuration error!. Duplicate definition of node: " + tmp_node["name"]  + " in " + filename 
                self.errorlog.error("Configuration error!. Duplicate definition of node: " + tmp_node["name"] + " in " + filename)
                exit(1)

            nodes[tmp_node["name"]] = tmp_node
        return nodes
        
    
    # Parses heads and bodies of config parts
    # Ex: 
    # " name:  foo[0-2]
    #   bar:   xxx
    # Returns dictionary:
    # {"name": ["foo0", "foo1", "foo2"], "bar":"xxx"}
    def get_heads_bodies(self, f):
        trap = 0
        heads_bodies = {}
        line = self.get_line(f)
        while line and ":" in line:
            if line.endswith("}"):
                line = line[:-1]
                trap = 1
            head, body = line.split(":")
            head = head.strip()
            body = body.strip()
            body = self.create_lines(body)
            heads_bodies[head] = body
            if trap:
                break
            line = self.get_line(f)

        # All objects must have "name"
        if not heads_bodies.has_key("name"): 
            print "Configuration error. Please check your node definition in config file: " + filename
            self.errorlog.error("Configuration error. Please check your node definition in config file: " + filename)
            exit(1)

        return heads_bodies



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
        return line
        


    # Create power state files in ClusterNap/states/  folder.
    # Remove file which are not defined in config. 
    def create_state_files(self):

        # Remove state files whose node is not define in config 
        old_state_files = os.listdir(self.STATE_DIR)
        for state_file in old_state_files:
            if state_file not in self.NODES.keys():
                print "Removing state file, because its node is not defined: " + state_file 
                self.log.info("Removing state file, because its node is not defined: " + state_file)
                os.unlink(self.STATE_DIR + state_file)

        # Create state files whose node is defined in config, but state file is not created yet. 
        for node in self.NODES.keys():
            if not os.path.isfile(self.STATE_DIR + node):
                print "Creating following state file: " + node 
                self.log.info("Creating following state file: " + node)
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
                self.errorlog.error("Error in config. Unknown config: " + exprs)
                print "Expression inside [] might be wrong: " + exprs
                self.errorlog.error("Expression inside [] might be wrong: " + exprs)
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
                self.errorlog.error("Configuration error: Number of items in different brackets does not match!")
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
        print "ON COMMANDS"
        for node in self.NODES:
            if self.NODES[node].has_key("on_command"):
                print node + " : " + self.NODES[node]["on_command"]
            else:
                print node + " : Not defined!"
                self.log.warn("Node " + node + " has no on_command defined!")
        print self.get_on_command()
        
        print "OFF COMMANDS"
        for node in self.NODES:
            if self.NODES[node].has_key("off_command"):
                print node + " : " + self.NODES[node]["off_command"]
            else:
                print node + " : Not defined!"
                self.log.warn("Node " + node + " has no off_command defined!")
        print self.get_off_command()

        
#        print "NODES:"
#        print self.NODES
        print "COMMANDS:"
        print self.COMMANDS
        print "TYPES:"
        print self.TYPES
        return

if __name__ == "__main__":
    sys.exit(get_conf().main())
