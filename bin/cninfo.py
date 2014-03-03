#! /usr/bin/env python2.7
#
''' 
Shows  ClusterNap nodes' current information. 
Which nodes are ON/OFF/Requested( by whom, when)

'''
import os, sys, re, pwd, datetime
import itertools
import get_state
import get_conf
import logset

class cninfo:
    def __init__ (self):
        # Get logger
        self.log      = logset.get("cninfo_event", "event.log")
        self.errorlog = logset.get("cninfo_error", "error.log")
        self.REQUEST_DIR         = os.path.dirname(os.path.abspath(__file__))
        self.REQUEST_DIR        += "/../requested/nodes/"
        self.NODES_REQUESTED     = os.listdir(self.REQUEST_DIR)
	self.NODES	         = get_conf.get_conf().NODES
#        self.STATES              = {}
#        self.STATES              = get_state.get_state().STATES.copy()
        self.USER                = pwd.getpwuid(os.getuid())[0]       
 #       self.INFO   = {}
        
#        for node in self.NODES.keys():
#            self.INFO[node] = self.get_node_info(node)
            
#        self.INFO_LIST = self.INFO.items()
#        self.INFO_LIST = sorted(self.INFO_LIST, key=lambda element:   (  element[1][0], \
#                                                                         element[1][1], \
#                                                                         element[1][2], \
#                                                                         element[1][3], \
#                                                                         element[0]   ) )


    def clusternapd_running(self):
        pid_file = "/tmp/clusternapd.pid"

        # if PID file does not exist
        if not os.path.isfile(pid_file):
            return False

        # get PID of clusternapd
        f = open(pid_file, 'r')
        pid = int(f.readline().strip()) 
        f.close()

        # PID exists
        try:
            os.kill(pid, 0)
            return True  
        except OSError:
            return False

        
    def get_nodes(self):
        return get_conf.get_conf().NODES

    
    def get_commands(self):
        return get_conf.get_conf().COMMANDS

    def get_types(self):
        return get_conf.get_conf().TYPES

    def get_info(self):
        INFO   = {}
        for node in self.NODES.keys():
            INFO[node] = self.get_node_info(node)
        return INFO

    def get_info_list(self):
        INFO = self.get_info()
        INFO_LIST = INFO.items()
        INFO_LIST = sorted(INFO_LIST, key=lambda element:   (  element[1][0], \
                                                                         element[1][1], \
                                                                         element[1][2], \
                                                                         element[1][3], \
                                                                         element[0]   ) )
        return INFO_LIST


    # Returns node's state, requested_or_not, owner_name, and last_requested_date
    def get_node_info(self, node):
        STATES              = {}
        STATES              = get_state.get_state().STATES.copy()
        if STATES[node] == 1:
            state = "On"
        elif STATES[node] == 0:
            state = "Off"
        else:
            state = "Unknown"

        requested = "Free"
        owner = "N/A"
        modified = "N/A"

        if node in self.NODES_REQUESTED:
            requested = "Requested"
            # Get owner name
            st = os.stat(self.REQUEST_DIR + node)
            uid = st.st_uid
            info = pwd.getpwuid(uid)
            owner = info.pw_name
            # Get last modified date (Last requested date)
            t = os.path.getmtime(self.REQUEST_DIR + node)
            modified = str(datetime.datetime.fromtimestamp(t))[:19]

        return state, requested, owner, modified

    def print_info(self):
        state = "NOT RUNNING"
        pid   = "N/A" 
        if self.clusternapd_running():
            pid_file = "/tmp/clusternapd.pid"
            f = open(pid_file, 'r')
            pid = f.readline().strip()
            f.close()
            state = "RUNNING"

        print "clusternapd: %s" % (state)
        print "pid: %s\n" % (pid)


    def print_list(self, lis):
        print " --------------------------------------------------------------------------------- "
        print "|   Node name    | Power state | Request state | Request user |   Request date    |"
        print " --------------------------------------------------------------------------------- "
        for line in lis:
#            print "|{:16s}|{:13s}|{:15s}|{:14s}|{:19s}|".format(line[0], line[1][0], line[1][1], line[1][2], line[1][3] )
            print "|%-16s|%-13s|%-15s|%-14s|%-19s|" % (line[0], line[1][0], line[1][1], line[1][2], line[1][3] )
        print " ---------------------------------------------------------------------------------\n"


    def show_help(self):
#        print " Usage:  {} info [-u <username>] [-r <free|requested|f|r> ] [-s <on|off|unknown|un|u>]  [-n <nodename*>]\n".format(sys.argv[0])
        print " Usage:  %s info [-u <username>] [-r <free|requested|f|r> ] [-s <on|off|unknown|un|u>]  [-n <nodename*>]\n" % (sys.argv[0])

    # If any user is define in the argument, take that
    def get_user(self, arglist):
        name = ""
        for i in range(1, len(arglist)):
            if arglist[i] == "-u" and i < len(arglist)-1:
                if arglist[i+1].startswith("-"):
                    print "Wrong username: "
                    self.show_help()
                    exit(1)
                name = arglist[i+1]
                arglist.pop(i)
                arglist.pop(i)
                break
        return arglist, name
                   
    # Power state
    def get_pstate(self, arglist):
        pstate = ""
        ons    = ["on", "On", "ON"]
        offs   = ["off", "Off", "OFF"]
        uns    = ["unknown", "Unknown", "UNKNOWN", "U", "u"]
        states = ons + offs + uns
        for i in range(1, len(arglist)):
            if arglist[i] == "-s" and i < len(arglist)-1:
                if not arglist[i+1].startswith("-"):
                    if not arglist[i+1] in states:
                        print "Wrong Power state: " + arglist[i+1]
                        self.show_help()
                        exit(1)
                    if arglist[i+1] in ons:
                        pstate = "On"
                    elif arglist[i+1] in offs:
                        pstate = "Off"
                    else:
                        pstate = "Unknown"
                    arglist.pop(i)
                    arglist.pop(i)
                    break
        return arglist, pstate

    # Request state
    def get_rstate(self, arglist):
        rstate = ""
        frees = ["Free","FREE", "free", "f", "F"]
        reqds = ["Requested", "REQUESTED","requested", "r", "R"]
        states = frees + reqds

        for i in range(1, len(arglist)):
            if arglist[i] == "-r" and i < len(arglist)-1:
                if not arglist[i+1].startswith("-"):
                    if not arglist[i+1] in states:
                        print "Wrong request state: " + arglist[i+1]
                        self.show_help()
                        exit(1)
                    if arglist[i+1] in frees:
                        rstate = "Free"
                    else:
                        rstate = "Requested"
                    arglist.pop(i)
                    arglist.pop(i)
                    break
        return arglist, rstate

    def get_node(self, arglist):
        nname = ""
        for i in range(1, len(arglist)):
            if arglist[i] == "-n" and i < len(arglist)-1:
                if arglist[i+1].startswith("-"):
                    print "Wrong node name: " + arglist[i+1]
                    self.show_help()
                    exit(1)
                nname = arglist[i+1]
                arglist.pop(i)
                arglist.pop(i)
                break
        return arglist, nname

    def get_list(self, info_list, user, pstate, rstate, node):
        tmp_list = list()
        for line in info_list:
            if node in line[0] and \
                    ( pstate == line[1][0] or pstate == "" ) and \
                    ( rstate == line[1][1] or rstate == "" ) and \
                    ( user ==  line[1][2] or user == ""):
                tmp_list.append(line)

        return tmp_list

    def main(self, argv):

#        info_list = self.INFO_LIST[:]
        info_list = self.get_info_list()
        user   = "" # user name
        pstate = "" # power state
        rstate = "" # request state
        node   = "" # node name

        argv, user   = self.get_user(argv)
        argv, pstate = self.get_pstate(argv)
        argv, rstate = self.get_rstate(argv)
        argv, node   = self.get_node(argv)

        if len(argv) != 1:
            self.show_help()
            exit(1)

        info_list = self.get_list(info_list, user, pstate, rstate, node)
        self.print_info()
        self.print_list(info_list)

        return

if __name__ == "__main__":
    sys.exit(cninfo().main(sys.argv))
