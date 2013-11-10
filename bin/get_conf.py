#!/usr/bin/python
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
        tmp_node = {}

        f = open(filename, "r")
        for line in f:
            line = line.strip()

            # Ignore comment-outed or empty line
            if line[:1] == "" or line[:1] == "#": 
                continue

            # Remove comments
            line = line.split("#")
            line = line[0]
        
            if "{" in line and "define" in line: # Start of definition
                continue
#                print "START"
            elif "}" in line:                    # End of definition
                if not tmp_node.has_key("name"):
                    print "Node definition error. Please check your config file."
                    exit(1)
                nodes[tmp_node["name"]] = tmp_node
                tmp_node = {}
#                print "END"
            else:                                # Body of definition
                head, body = line.split(":")
                head = head.strip()
                body = body.strip()
                tmp_node[head] = body
#                print tmp_node

        return nodes

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
                os.chmod(self.STATE_DIR + node, 666)
        
    def main(self):

        self.create_state_files()
	print self.CONFIG
        print "ON COMMANDS"
        print self.get_on_command()
        print "OFF COMMANDS"
        print self.get_off_command()
        return

if __name__ == "__main__":
    sys.exit(get_conf().main())

