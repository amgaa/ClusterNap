#!/usr/bin/env python
# A ClusterNap compatible check_nrpe plugin

import sys
import os
import subprocess 
import socket

clusternap_dir = os.path.dirname(os.path.abspath(__file__)) + "/../state/nodes/"
#clusternap_dir = "/home/amgaa/ClusterNap/state/nodes/"     # <--- For now just use it. 
nodes          = os.listdir(clusternap_dir)
plugin_dir     = "/usr/lib/nagios/plugins/"
orig_plugin    = plugin_dir + "check_nrpe"
args           = sys.argv[1:]
cmd            = orig_plugin

# Get unique service name we are checking
service_name = ""
block = -1
for i in range(0, len(args)):
    if args[i] == "-s":
        service_name = args[i+1]
        block = i

# Erase service name from arguments
if block != -1:
    args.pop(block)
    args.pop(block)

# Run the original check_nrpe command
for arg in args:
    cmd += " " + arg

ret = subprocess.Popen(cmd, shell=True)
ret.wait()

# St values for ClusterNap. 1 is for ON, 0 is for OFF, and -1 is for Unknown states. 
if ret.returncode == 0 or ret.returncode == 1: # OK or WARNING
    val = "1"
elif ret.returncode == 2:                      # CRITICAL
    val = "0"
elif ret.returncode == 3:                      # UNKNOWN
    val = "-1"
else:
    val = "-1"

#Check if service is defined in argument and exists in ClusterNap configuration.
#If so, put the corresponding value to the state config file in ClusterNap.
if service_name != "" and service_name in nodes:
    f=open( clusternap_dir + service_name, "w" )
    f.write( val + "\n" )
    f.close()
else:
    print "Warning in check_nrpe_CN.py. Your service \"" +service_name + "\" is not defined in ClusterNap.\n"

# Exit with same value as check_nrpe
sys.exit(ret.returncode)
