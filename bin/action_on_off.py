#! /usr/bin/python

#'''
# Tries to change states of nodes according to the information (what nodes should be ON and which ones should b#e off)
# from get_on_off.py by checking their dependencies and their childs' states. 
#
# Tries to make all necessary nodes ON 
# Tries to make all unnecessary nodes OFF
# '''

import sys, os, re
import get_on_off
import get_dependency
import get_state
import change_state
import get_conf
import subprocess
import time
import shlex
import logset

class action_on_off:
    def __init__(self):
        # Get logger
        self.log      = logset.get("action_event", "event.log")
        self.errorlog = logset.get("action_error", "error.log")
        self.NODES_TO_ON  = list()
        self.NODES_TO_OFF = list()
        self.STATES       = {}
        self.DEP_RUN      = {}
        self.DEP_RUN_ON   = {}
        self.DEP_OFF      = {}
        # Dependency-g get config-s avah
        self.NODES_TO_ON, self.NODES_TO_OFF = get_on_off.get_on_off().main()
        self.tmp_nodestoon = self.NODES_TO_ON[:]
        self.tmp_nodestooff = self.NODES_TO_OFF[:]
        print "NODES TO ON:"
        print self.NODES_TO_ON 
        print "NODES TO OFF:"
        print self.NODES_TO_OFF 
        
        self.STATES     = dict(get_state.get_state().main())
        self.DEP_RUN    = get_dependency.get_dependency().get_run_dep()
        self.DEP_RUN_ON = get_dependency.get_dependency().get_run_on_dep()
        self.DEP_OFF    = get_dependency.get_dependency().get_off_dep()
        
        # ON and OFF scripts: 
        # On what "host", which "command" should be executed, "who" should run that script 
        self.ON_COMMANDS     = get_conf.get_conf().get_on_command()
        self.OFF_COMMANDS    = get_conf.get_conf().get_off_command()
        self.COMMAND_OUT_LOG = os.path.dirname(os.path.abspath(__file__)) + "/../logs/command_out.log"

        self.PROCS     = set() # Pool of executing child processes
        self.MAX_PROCS = 10    # Max number of proccesses in the processes pool

        # Leave only OFF nodes in  self.NODES_TO_ON. 
        # Here we also leave Unknown state nodes untouched.
        tmp_list = list()
        tmp_list = self.NODES_TO_ON[:]
        for node in tmp_list:
            if self.STATES.has_key(node):
                if self.STATES[node] != 0:
                    self.NODES_TO_ON.remove(node)

        # Leave only ON nodes in self.NODES_TO_OFF
        # Here we also leave Unknown state nodes untouched.
        tmp_list = self.NODES_TO_OFF[:]
        for node in tmp_list:
            if self.STATES.has_key(node):
                if self.STATES[node] != 1:
                    self.NODES_TO_OFF.remove(node)
                    
        # Shows if a node has RUN-dep ON child
        self.HAS_RUN_DEP_ON_CHILD = {}
        for node in self.NODES_TO_OFF:
            self.HAS_RUN_DEP_ON_CHILD[node] = 0
 
        for node in self.NODES_TO_OFF:
            childs = list()
            if self.DEP_RUN.has_key(node):
                childs = self.DEP_RUN[node]

            for clause in childs:
                for nodeA in clause:
                    if nodeA in self.NODES_TO_OFF:
                        print "RUN DEP NODE OF "+  nodeA + " is " + node 
                        self.HAS_RUN_DEP_ON_CHILD[nodeA] = 1

        # Shows if a node has OFF-dep ON child
        self.HAS_OFF_DEP_ON_CHILD = {}
        for node in self.NODES_TO_OFF:
            self.HAS_OFF_DEP_ON_CHILD[node] = 0
 
        for node in self.NODES_TO_OFF:
            childs = list()
            if self.DEP_OFF.has_key(node):
                childs = self.DEP_OFF[node]

            for clause in childs:
                for nodeA in clause:
                    if nodeA in self.NODES_TO_OFF:
                        print "OFF DEP NODE OF "+  nodeA + " is " + node 
                        self.HAS_OFF_DEP_ON_CHILD[nodeA] = 1


    # Turns on ON-able OFF nodes
    def try_on(self, nodes_to_on):
        for node in nodes_to_on:
            if not self.STATES.has_key(node): # Already ON
                print "Node " + node + "'s state is not defined in folder states/nodes/"
                print "Please define it. (Create a file named \"" + node + "\" in there.)"
                self.errorlog.error("Node " + node + " has no state file defined in states/nodes/ folder!")
                continue

            if self.STATES[node] == 1: # Already ON
                continue

            # In case no script is defined
            if not self.ON_COMMANDS.has_key(node):
                print "node " + node + " has no COMMAND defined to make it ON in config/nodes/ folder. Please define it there"
                self.errorlog.error("node " + node + " has no COMMAND defined to make it ON in config/nodes/ folder. Please define it there")
                continue

            if self.on_able(node):
                flag = 0
                for host in self.ON_COMMANDS[node]: # When there are multiple hosts from which we can execute on/off script , we need to select one. In out case, just choose first host that is ON
                    if self.STATES.has_key(host['host']) and self.STATES[host['host']] == 1:
                        self.to_procs_pool(host)
                        flag = 1
                        print "Turn ON command sent to " + node
                        self.log.info('Turn-ON command sent to ' + node)
                        break
                if flag == 0: # No host was available
                    print "Error: No ON script has been run for node " + node + "!"
                    self.errorlog.error('Node ON script has been run for node ' + node + '!')
                    
            else:
                print "Cannot turn on " + node + " for now"
                self.log.info('Cannot turn-ON node' + node + ' for now')



    # Turns off OFF-able ON nodes
    def try_off(self, nodes_to_off):
        for node in nodes_to_off:
            if self.STATES[node] == 0: # Already OFF
                continue

            # In case no script is defined
            if not self.OFF_COMMANDS.has_key(node):
                print "node " + node + " has no COMMAND defined to make it OFF in config/nodes/ folder. Please define it there"
                self.errorlog.error("node " + node + " has no COMMAND defined to make it OFF in config/nodes/ folder. Please define it there")
                continue

            if self.off_able(node):
                flag = 0
                for host in self.OFF_COMMANDS[node]: # When there are multiple hosts from which we can execute on/off script , we need to select one. In out case, just choose first host that is ON
                    if self.STATES.has_key(host['host']) and self.STATES[host['host']] == 1:
                        self.to_procs_pool(host)
                        print "Turn OFF command sent to " + node
                        self.log.info('Turn-OFF command sent to ' + node)
                        flag = 1

                        break
                if flag == 0: # No host was available
                    print "Error: No OFF script has been run for node " + node + "!"
                    self.errorlog.error('Node OFF script has been run for node ' + node + '!')

            else:
                print "Cannot turn off " + node + " for now"
                self.log.info('Cannot turn-OFF node' + node + ' for now')

                
    # Adds command to execute into the subprocesses' pool.
    # So the commands are executed in parallel
    def to_procs_pool(self, host):
        cmd = self.create_cmd(host['host'], host['command'], host['user'])
#        self.PROCS.add(subprocess.Popen(cmd))
        self.PROCS.add(subprocess.Popen(cmd))
        if len(self.PROCS) >= self.MAX_PROCS:
            os.wait()
            procs.difference_update(p for p in procs if p.poll is not None)
        

    # Creates ON/OFF command
    def create_cmd(self, host, path_script, user):
        cmd  = "ssh -t -q root@" + host
        cmd += " \'su - " + user
        cmd += " -c " + " \"" + path_script + "\"  \'"
#        cmd += " >> " + self.COMMAND_OUT_LOG
        cmd =shlex.split(cmd)
        return cmd


    # Checks if an OFF node is ON-able (necessary childs are ON)
    def on_able(self, node):
        if not self.DEP_RUN_ON.has_key(node):
            return 1

        # When the first occurence of all nodes in any of clause os ON, return 1
        childs = self.DEP_RUN_ON[node]
        for clause in childs:
            flag = 0
            for node in clause:
                if self.STATES.has_key(node) and self.STATES[node] != 1:
                    flag = 1
                    break
                if not self.STATES.has_key(node):
                    flag = 1
                    break
            if flag == 0:
                return 1
        return 0

    # Checks if an ON node is OFF-able (necessary childs are ON)
    def off_able(self, node):
        if not self.DEP_OFF.has_key(node):
            print "No OFF-dependency found for node " + node
            self.log.debug("No OFF-dependency found for node " + node)
            return 0

        # Need to know if there is RUN_dependencies among nodes_to_off.
        # If so, we should start from the childs
        if self.HAS_RUN_DEP_ON_CHILD[node]:
            print node + " has some child nodes working. Cannot turn off"
            self.log.debug(node + " has some child nodes working. Cannot turn off")
            return 0

        if self.HAS_OFF_DEP_ON_CHILD[node]:
            print node + " has some child nodes working. Cannot turn off"
            self.log.debug(node + " has some child nodes working. Cannot turn off")
            return 0

        # When the first occurence of all nodes in any of clause os ON, return 1
        # We also need to check if given "node" is parent of any other ON node by "RUN_DEP". 
        # In this case, we cannot turn off the given node. 
        childs = self.DEP_OFF[node]
        for clause in childs:
            flag = 0
            for node in clause:
                if self.STATES.has_key(node) and self.STATES[node] != 1:
                    flag = 1
                if not self.STATES.has_key(node):
                    flag = 1
            if flag == 0:
                return 1

        return 0


    # Checks if a node has RUN dependency running child(s) in nodes_to_off nodes. 
    def has_running_childs(self, node):
        if self.HAS_RUNNING_OFF_TO_CHILD[node]:
            return 1
        return 0

    
    def main(self):
        print "NODES TO ON and their states: "
        for node in self.tmp_nodestoon:
            if self.STATES.has_key(node):
                print node + ": " + str(self.STATES[node])
            else:
                print node + ": state unwritten"
        print "\n\n"

        print "NODES TO OFF and their states: "
        for node in self.tmp_nodestooff:
            if self.STATES.has_key(node):
                print node + ": " + str(self.STATES[node])
            else:
                print node + ": state unwritten"
        print "\n\n"

        self.try_on(self.NODES_TO_ON)
        self.try_off(self.NODES_TO_OFF)

#        print __name__
        return

if __name__ == "__main__":
    sys.exit(action_on_off().main())
