ClusterNap
==========

ClusterNap is a simple, configurable power control tool for IT infrastructures. 

ClusterNap controls the (power, run) states of your nodes(physical servers, VMs, switches, RAIDS, services) in your system. 
After simply configuring node dependencies and ON/OFF commands for each node, all you have to do is just tell the ClusterNap which nodes you need and which you do not. It will take care of the rest; for example, what other nodes it should turn-on/off in order to turn-on/off you requested/derequested nodes. Moreover, ClusterNap knows exactly in what order it should take turn-on/off actions for the nodes while keeping the system graceful. 



How to install
==============
It is easy to install. Just clone the repository and add ClusterNap's bin/ directory to your PATH. 

```
git clone https://github.com/amgaa/ClusterNap.git

export PATH=$PATH:/path/to/ClusterNap/bin/
```


Configuring nodes (servers, VMs, cloud instances, switches, RAIDS)
==================================================================

```
define node{
        name:                   worker_node[000-100]
        run_dependencies:       filesystem_node
        on_dependencies:        management_node | filesystem_node
        off_dependencies:       management_node | filesystem_noe
        on_command:             management_node, root, ipmi!10.1.2.[100-200] | \
                                filesystem_node, root, ipmi!10.1.2.[100-200]
        off_command:            management_node, root, ssh_shutdown!worker_node[000-100] | \
                                filesystem_node, root, ssh_shutdown!worker_node[000-100]
}


define_command {
       name:            ssh_shutdown
       command_line:    ssh $ARG1 shutdown -h now
}

define command {
       name:            ipmi
       command_line:    ipmitool -I lanplus -H $ARG1 -P IPMI_PASSWORD -U root chassis power on
}

```


cntools (ClusterNap's user interface tool)


