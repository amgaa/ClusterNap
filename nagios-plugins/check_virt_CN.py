#!/usr/bin/env python
#Checks status os MV on libvirt. 
# returns 0, if the state is "running" or "blocked"
#         1, if "paused"
#         2, if "shutdown", "shut off" or "crashed"


import sys
import os
import subprocess

if len(sys.argv) != 2:
    print "Usage: ./check_virt_CN.py VM_name" 
    sys.exit(3)

hostname = sys.argv[1]
virsh    = "/usr/bin/virsh"
command  = virsh + " domstate " + hostname


clusternap_dir = os.path.dirname(os.path.abspath(__file__)) + "/../state/nodes/"
#clusternap_dir = "/home/amgaa/ClusterNap/state/nodes/"     # <--- For now just use it. 
nodes          = os.listdir(clusternap_dir)

#Get stdout of command
ret = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
ret.wait() #Wait for the process to finish
stdout = ret.stdout.readline().strip()

# Set the values to Nagios, ClusterNap and stdout
if stdout == "running" or stdout == "blocked":
    val="1"
    exitval=0
    print "OK"
elif stdout == "paused":
    val="1"
    exitval=1
    print "WARNING"
elif stdout == "shutdown" or stdout == "shut off" or stdout == "crashed":
    val="0"
    exitval=2
    print "CRITICAL"
else:
    val="-1"
    exitval=3
#    os.system("whoami")
    print command + " " + stdout + " Error: error checking VM status with check_virt_CN.py plugin"


#Write to corresponding ClusterNap state file.
if hostname != "" and hostname in nodes:
    f=open(clusternap_dir + hostname, "w")
    f.write(val + "\n")
    f.close()

sys.exit(exitval)

