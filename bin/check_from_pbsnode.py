#!/usr/bin/env python
'''
Checks nodes' states from pbsnodes command and updates them.
'''

import sys
import os
import subprocess 
import socket

def cn_state(pbs_state):
#    if pbs_state in ["active", "all", "busy", "free", "up"]:
#        return "1"
#    if pbs_state in ["OFFLINE", "DOWN", "offline", "down"]:
#        return "0"
#    if pbs_state in ["UNKNOWN", "unknown"]:
#        return "-1"

    if any(state in pbs_state for state in ["active", "all", "busy", "free", "up"]):
        return "1"
    if any(state in pbs_state for state in ["OFFLINE", "DOWN", "offline", "down"]):
        return "0"
#    if any(state in pbs_state for state in ["UNKNOWN", "unknown"]):
    return "-1"

#    print "cn_state: Unexpected error converting pbsnode's state to clusternap's state"
#    exit(1)

def main():
    clusternap_dir = os.path.dirname(os.path.abspath(__file__)) + "/../state/nodes/"
    cn_nodes       = os.listdir(clusternap_dir)
    pbs_nodes      = {}
    cmd            = "pbsnodes -l all"
    
    # ret = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    ret.wait()

    for pair in ret.communicate()[0].splitlines():
        node, value = map( str.strip, pair.split() )
        pbs_nodes[node] = value

    for node in pbs_nodes:
        if node in cn_nodes:
            state = cn_state(pbs_nodes[node])
            f=open( clusternap_dir + node, "w" )
            f.write( state + "\n" )
            f.close()

if __name__ == "__main__":
    sys.exit(main())
