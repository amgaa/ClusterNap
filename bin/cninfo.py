#! /usr/bin/python
#

''' 
 Returns: 
            List of OFF-nodes that should be ON: 
            List of ON-nodes that can be OFF: 


 Given the dependencies of all nodes (D), requested nodes (R) and current states of all nodes (S)
 This program gets minimum number of nodes which are required for requested nodes to be ON. 
 It also returns the list of nodes which we can turn-off. 
 However this program does not tell how to turn-on all of requested nodes, (i.e. by what order ...).
 action_on_off.py does this. 
'''

import os, sys, re, pwd, datetime
import itertools
import get_state
import get_conf
import logset

class cninfo:
    def __init__ (self):
        # Get logger
        self.log      = logset.get("cninfo", "event.log")
        self.errorlog = logset.get("cninfo", "error.log")
        self.REQUEST_DIR         = os.path.dirname(os.path.abspath(__file__))
        self.REQUEST_DIR        += "/../requested/nodes/"

        self.NODES_REQUESTED     = os.listdir(self.REQUEST_DIR)
	self.NODES	         = get_conf.get_conf().NODES

        self.STATES              = {}
        self.STATES              = get_state.get_state().STATES.copy()

        self.USER                = pwd.getpwuid(os.getuid())[0]       
        
        self.INFO   = {}
        
        for node in self.NODES.keys():
            self.INFO[node] = self.get_node_info(node)
            
        self.INFO_LIST = self.INFO.items()
        self.INFO_LIST = sorted(self.INFO_LIST, key=lambda element:   (  element[1][0], \
                                                                         element[1][1], \
                                                                         element[1][2], \
                                                                         element[1][3], \
                                                                         element[0]   ) )



    # Returns node's state, requested_or_not, owner_name, and last_requested_date
    def get_node_info(self, node):

        if self.STATES[node] == 1:
            state = "On"
        elif self.STATES[node] == 0:
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
            modified = str(datetime.datetime.fromtimestamp(t))[:-7]

        return state, requested, owner, modified

    # Prints out specific user's request info
    def user_info(self, username):
        
        print " Showing user {0}'s request info".format(username)
        print " ---------------------------------------------------------------------------------------------- "
        print "|   Node name    |    Power state   |   Request state   |   Request user   |   Request date    |"
        print " ---------------------------------------------------------------------------------------------- "
        for line in self.INFO_LIST:
            if username == line[1][2]:
                print "|{:16s}|{:18s}|{:19s}|{:18s}|{:19s}|".format(line[0], line[1][0], line[1][1], line[1][2], line[1][3] )
        print " ----------------------------------------------------------------------------------------------\n"
        

    # All info of the system
    def all_info(self):
        print "ClusterNap: System's node request info:"
        print " ---------------------------------------------------------------------------------------------- "
        print "|   Node name    |    Power state   |   Request state   |   Request user   |   Request date    |"
        print " ---------------------------------------------------------------------------------------------- "
        for line in self.INFO_LIST:
            print "|{:16s}|{:18s}|{:19s}|{:18s}|{:19s}|".format(line[0], line[1][0], line[1][1], line[1][2], line[1][3] )
        print " ----------------------------------------------------------------------------------------------\n"


    def show_help(self):
        print "Usage information: "
        print "To see your own request info"
        print "      Usage: {}\n".format(sys.argv[0])
        print "To see all system's request info"
        print "      Usage: {} -a\n".format(sys.argv[0])
        print "To see specific user's request info"
        print "      Usage: {} -u <Username>\n".format(sys.argv[0])
        print "For help"
        print "      Usage: {} -h\n".format(sys.argv[0])


    def main(self, argv):

        self.args = argv

        if len(self.args) == 3 and self.args[1] == '-u':
            return self.user_info(self.args[2])
        if len(self.args) == 2 and self.args[1] == '-a':
            return self.all_info()
        if len(self.args) == 2 and self.args[1] == '-h':
            return self.show_help()
        if len(self.args) == 1:
            return self.user_info(self.USER)

        return self.show_help()



        return

if __name__ == "__main__":
    sys.exit(cninfo().main(sys.argv))
