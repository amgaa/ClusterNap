#! /usr/bin/python

''' 
 Tries to change states of nodes according to the information (what nodes should be ON and which ones should be off)
 from get_on_off.py by checking their dependencies and their childs' states. 

 Tries to make all necessary nodes ON 
 Tries to make all unnecessary nodes OFF
'''

import sys, os, re
import get_on_off
import get_dependency
import get_state
import change_state
#import get_config
import get_conf


class action_on_off:
    def __init__(self):
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
        self.COMMAND_OUT_LOG = os.path.dirname(os.path.abspath(__file__)) + "/logs/command_out.log"

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


#        return


    # Turns on ON-able OFF nodes
    def try_on(self, nodes_to_on):
        for node in nodes_to_on:
            if not self.STATES.has_key(node): # Already ON
                print "Node " + node + "'s state is not define in folder states/{physical. service}/"
                print "Please define it. (Create a file named \"" + node + "\" in there.)"
                continue

            if self.STATES[node] == 1: # Already ON
                continue

            # In case no script is defined
            if not self.ON_COMMANDS.has_key(node):
                print "node " + node + " has no script to make it ON in config/scripts/{physical, service}/on/ folder. Please define it there"
                continue

            if self.on_able(node):
                flag = 0
                for host in self.ON_COMMANDS[node]: # When there are multiple hosts from which we can execute on/off script , we need to select one. In out case, just choose first host that is ON
                    if self.STATES.has_key(host['host']) and self.STATES[host['host']] == 1:
                        self.exec_on_host(host['host'], \
                                              host['command'],\
                                              host['user'],\
                                              node,\
                                              'ON')
                        flag = 1
                        print "Turn ON command sent to " + node
                        break
                if flag == 0: # No host was available
                    print "Error: No ON script has been run for node " + node + "!"
                    
            else:
                print "Cannot turn on " + node + " for now"


    # Turns off OFF-able ON nodes
    def try_off(self, nodes_to_off):
        for node in nodes_to_off:
            if self.STATES[node] == 0: # Already OFF
                continue

            # In case no script is defined
            if not self.OFF_COMMANDS.has_key(node):
                print "node " + node + " has no script to make it OFF in config/scripts/{physical, service}/on/ folder. Please define it there"
                continue

            if self.off_able(node):
                flag = 0
                for host in self.OFF_COMMANDS[node]: # When there are multiple hosts from which we can execute on/off script , we need to select one. In out case, just choose first host that is ON
                    if self.STATES.has_key(host['host']) and self.STATES[host['host']] == 1:
                        self.exec_on_host(host['host'],\
                                              host['command'],\
                                              host['user'],\
                                              node,\
                                              'OFF')
                        print "Turn OFF command sent to " + node
                        flag = 1
                        break
                if flag == 0: # No host was available
                    print "Error: No OFF script has been run for node " + node + "!"

            else:
                print "Cannot turn off " + node + " for now"

    # Executes a script on given host as given user
    def exec_on_host (self, host, path_script, user, node, onoff):
        command  = "ssh -t -q root@" + host
        command += " \'su - " + user
#        command += " -c \"" + "sh " + path_script + " &\" \'"
        command += " -c " + " \"" + path_script + "\"  \'"
        command += " >> " + self.COMMAND_OUT_LOG
#        command += " &"      # <- This "&" makes some nodes do not start. Reason unclear! 

        if os.system(command) == 0:  # Successfully executed
            os.system(command)
            print "Turn " + onoff + " command sent: " + command
#            change_state.change_state().change_state(node, onoff) # <- This should be removed
        else:
            print "Turn-off/On command error! Cannot run command: " + command
        
        

    # Checks if an OFF node is ON-able (necessary childs are ON)
    def on_able(self, node):

        if not self.DEP_RUN_ON.has_key(node):
#            print "No RUN-ON-dependency found for node " + node
#            return 0
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
            return 0

        # Need to know if there is RUN_dependencies among nodes_to_off.
        # If so, we should start from the childs
        if self.HAS_RUN_DEP_ON_CHILD[node]:
            print node + " has some child nodes working. Cannot turn off"
            return 0

        if self.HAS_OFF_DEP_ON_CHILD[node]:
            print node + " has some child nodes working. Cannot turn off"
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
#        print self.DEP_RUN_ON
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

        return

if __name__ == "__main__":
    sys.exit(action_on_off().main())
