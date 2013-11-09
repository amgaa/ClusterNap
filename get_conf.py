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
        self.CONFDIR           = os.path.dirname(os.path.abspath(__file__))
        self.CONF_FILE         = self.CONFDIR + "/config/proto.conf"
        self.CONFIG = {}
        self.CONFIG = self.get_conf()
        self.ON_COMMANDS = {}
        self.ON_COMMANDS = self.get_on_command()
        self.OFF_COMMANDS = {}
        self.OFF_COMMANDS = self.get_off_command()



    # Returns  hash table of:
    # commands[name] = [{'host': "", 'user':"", 'command':""}, {'host': "", 'user':"", 'command':""} ... ]        
    def get_on_command(self):
        on_commands = {} 
        tmp_command = {}
        
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
                tmp_command["command"] = cmd[2].strip()
            
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
                tmp_command["command"] = cmd[2].strip()
            
            if off_commands.has_key(node):
                off_commands[node].append(tmp_command)
            else:
                off_commands[node] = []
                off_commands[node].append(tmp_command)
            
        return off_commands
            

    # Parses config file and returns hash table of config
    # config[node] = {'name': 'NodeA', 'address':'192.168...', 'run_dependency': ... }

    def get_conf(self):
        head_types = ["name", "type", "address", "run_dependencies", "on_dependencies", "off_dependencies", "on_command", "off_command"]
        nodes    = {}
        tmp_node = {}

        f = open(self.CONF_FILE, "r")
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

        
    def main(self):
        
        print self.get_conf()
        print "ON COMMANDS"
        print self.get_on_command()
        print "OFF COMMANDS"
        print self.get_off_command()
        return

if __name__ == "__main__":
    sys.exit(get_conf().main())
