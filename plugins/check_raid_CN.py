#!/usr/bin/env python

import sys
import os
import subprocess 
import socket


clusternap_dir = os.path.dirname(os.path.abspath(__file__)) + "/../state/nodes/"
nodes          = os.listdir(clusternap_dir)
plugin_dir     = "/usr/lib/nagios/plugins/"
orig_plugin    = plugin_dir + "check_raid"
args           = sys.argv[1:]
cmd            = orig_plugin

for arg in args:
    cmd += " " + arg

# Get host we are checking
for i in range(0, len(args)):
    if args[i] == "-H":
        hostaddress = args[i+1]

host = ""
host = socket.gethostbyaddr(hostaddress)[1][0]

# ret = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
ret = subprocess.Popen(cmd, shell=True)
ret.wait()

# St values for ClusterNap. 1 is for ON, 0 is for OFF, and -1 is for Unknown states.
if ret.returncode == 0 or ret.returncode == 1: # OK or WARNING
    val = "1"
elif ret.returncode == 2:                      # CRITICAL                                       
    val = "0"
elif ret.returncode == 3:                      # UNKNOWN
#    val = "-1"
    val = "0"     #UNKNOWN state just messes things up too much. 
else:
#    val = "-1"
    val = "0"	  #UNKNOWN state just messes things up too much.

# Check if host is defined in argument and exists in ClusterNap configuration.
# If so, put the corresponding value to the state config file in ClusterNap.
if host != "" and host in nodes:
#    print "Host found and its name is " + host
    f=open( clusternap_dir + host, "w" )
    f.write( val + "\n" )
    f.close()

# Exit with the same status as original check_ping
sys.exit(ret.returncode)
