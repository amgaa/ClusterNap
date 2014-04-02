ClusterNap
==========

ClusterNap is a simple, configurable power controller tool for IT infrastructures. 

Well there are plenty of other power controller tools for IT infras. How is ClusterNap different from them? 

1) **Dependency-awareness**. When there are complex dependencies among the IT resources, it is not always clear how we should turn-on/off those resources (by *resource*, we mean any thing, like servers, switches, RAIDS, services, instances ...). ClusterNap takes care of it.  
2) **It is generic**. Other tools are mainly focused on "servers only". ClusterNap is not. It controls servers, switches, RAIDs, VMs, instances, services... pretty much whatever a user can imagine as a node.


ClusterNap controls the power states of your nodes (servers, VMs, switches, RAIDS, cloud instances, *whatever you can imagine*) in your system. 
After simply configuring node dependencies, ON/OFF commands for each node, and setting up node state update module, all you have to do is just tell the ClusterNap which nodes you need. It will take care of the rest; for example, what other nodes it should turn-on/off in order to turn-on/off you requested/derequested nodes. Moreover, ClusterNap knows exactly in what order it should take turn-on/off actions for the nodes while keeping the system graceful. 



CASE 1:
 For example, you have a worker node called *worker1* and it is connected to central filesystem node called *master*. In most cases, if you want to use node *worker1*, then node *master* has to be ON ***before*** we turn-ON *worker1*. In ClusterNap language, we call this situation "*worker1* is ***RUN-dependent*** on *master*". 

For now, it might be easy for you to figure out that you should first turn-ON *master* and then *worker1*. Now, let's consider you have hundreds of nodes with very *complex* ***RUN dependency***!! Not a funny job to do by your hand, is it? ClusterNap deals with this situation. 


Getting started
===============

How to install
--------------
ClusterNap runs on Linux (checked on Debian and Ubuntu) computer (however, it controls any computer or resource). 
It is very easy to install. Just clone the repository and add symbolic link of ClusterNap's daemon **clusternapd** and user interface tool **cntools** to your path. 

```
$ git clone https://github.com/amgaa/ClusterNap.git
$ ln -s /path/to/ClusterNap/bin/clusternapd /usr/local/bin/clusternapd
$ ln -s /path/to/ClusterNap/bin/cntools /usr/local/bin/cntools
```

Now, you can use **cntools** from your command line. Try following: 

```
$ cntools info
 --------------------------------------------------------------------------------- 
|   Node name    | Power state | Request state | Request user |   Request date    |
 --------------------------------------------------------------------------------- 
|localhost       |On           |Requested      |amgaa         |2014-01-20 15:55:29|
 ---------------------------------------------------------------------------------
```
and you will see something like above. What it says is that you have configured only one node which is called ***localhost***. Moreover, from the table above, we know node ***localhost***'s 
present power state is ***On***, 
it's been already ***requested*** 
and user ***amgaa*** requested it 
at ***2014-01-20 15:55:29***. 

While you never configured any node yet, somehow you see there is node here. It is because *localhost* is preconfigured, and you can see how it is configured in ClusterNap/config/localhost.conf. 

If you have come to this point, you most probably are wondering how to add new nodes to ClusterNap. Easy, you see next section. 



Configuring nodes (servers, VMs, cloud instances, switches, RAIDS)
------------------------------------------------------------------
Configuration files have to be written in *ClusterNap/config/* folder. Each configuration file should have **.conf** extension. As long as config files have *.conf* extension, you can have several or single config file. To keep the convenience, we advise you to divide your config files into several files such as *servers.conf*, *switches.conf*, *commands.conf* etc.

Now let's see how we might configure some servers. Say you have a cluster with 100 worker nodes with hostname of ***worker_node000 - worker_node099***. 
Moreover, let's consider your worker\_nodes are all connected to filesystem node ***filesystem\_node***

```
define node{
        name:                   worker_node[000-099]
        run_dependencies:       filesystem_node
        on_dependencies:        management_node | filesystem_node
        off_dependencies:       management_node | filesystem_noe
        on_command:             management_node, root, ipmi!10.1.2.[100-199] | \
                                filesystem_node, root, ipmi!10.1.2.[100-199]
        off_command:            management_node, root, ssh_shutdown!worker_node[000-099] | \
                                filesystem_node, root, ssh_shutdown!worker_node[000-099]
}
```
 Here, above configuration says, *worker\_node000 ~ worker\_node100* are all RUN-dependent on *filesystem_node*. 
Also on the line containing *on\_dependencies*, we see that  we can turn-on *worker\_node000 ~ worker\_node100* when one of *management\_node* or *filesystem\_node* is ON. Vertical bar "|" shows logical **OR** expression. 
The same goes to *off\_dependency*.  

In the line where *on_command* is written, it says "to make these nodes ON, ClusterNap should execute **ipmi** command with the argument of *10..1.2.100* (to 199) on the node management node as a user *root*. **Or** on the node filesystem_node". Same analogy applies to *off_command*.


Following show how we define the commands which change node's state. For example the command **ipmi** which turns on nodes is define as below. It takes one argument from the node definition, and runs the comman ```ipmitool``` with other certain options such as ipmi password, execution user, desired action (chassis power on etc...). 

```
define_command {
       name:            ssh_shutdown
       command_line:    ssh $ARG1 shutdown -h now
}

define command {
       name:            ipmi
       command_line:    ipmitool -I lanplus -H $ARG1 -P IPMI_PASSWORD -U root chassis power on
}

```


Following is an example of adding RAIDs and switches to ClusterNap.

```
define node{
    name:             raid_A
    run_dependencies: switch_A
    on_dependencies:  localhost
    off_dependencies: localhost
    on_command:       localhost, root, snmp_on!snmp_ip!snmp_port_no
    off_command:      localhost, root, snmp_off!snmp_ip!snmp_port_no
    }

define node{
    name:             switch_A
    run_dependencies:
    on_dependencies:  localhost
    off_dependencies: localhost
    on_command:       localhost, root, snmp_on!snmp_ip!snmp_port_no
    off_command:      localhost, root, snmp_off!snmp_ip!snmp_port_no
    }

define command {
    name:             snmp_off
    command_line:     snmpset -c comm_str -v 2c $ARG1 .1.3.6.1.4.1.13742.4.1.2.2.1.3.$ARG2 i 0
    }

define_command {
    name:             snmp_on
    command_line:     snmpset -c comm_str -v 2c $ARG1 .1.3.6.1.4.1.13742.4.1.2.2.1.3.$ARG2 i 1
    }         
```

And, you can also easily control Amazon's instances from ClusterNap too. An example is:

```
define node{
    name:                ec2-instant
    run_dependencies:    localhost
    on_dependencies:     localhost
    off_dependencies:    localhost
    on_command:          localhost, amgaa, ctl_ec2_inst\
                         !ap-northeast-1 (or other region)\
                         !EC2-ACCESS-KEY \
                         !EC2-SECRET-KEY \
                         !instant-ID \
                         !on
    off_command:         localhost, amgaa, ctl_ec2_inst \
                         !ap-northeast-1 (or other region)\
                         !EC2-ACCESS-KEY \
                         !EC2-SECRET-KEY \
                         !instant-ID \
                         !off
   }
   
define command{
   name:           ctl_ec2_inst
   command_line:  /path/to/ClusterNap/plugins/ctl_ec2_instance.py \
                                            $ARG1 $ARG2 $ARG3 $ARG4 $ARG5
   }
```

How nodes' states are being updated (for now)
---------------------------------------------

To work properly, the power states of nodes must be updated constantly and correctly. 
The power state of each node is represented a file in the directory   ```/path/to/ClusterNap/state/node/```. 
There are files generated automatically with the same name of each nodes defined in the ```config/``` directory. 
Inside these files in the ```state/nodes/``` directory, either **1**, **0**, or **-1** should be written. When the node is ON, it should be **1**, when OFF **0**, when UNKNOWN **-1** should be written inside these files. To update nodes' states means, therefore, to update these files. 


**Using Torque to update node states**  

When the node names match with the host names used in Torque resource manager, we can use Torque as node state updater. ClusterNap uses Torque's ```$ pbsnodes``` command and updates its nodes' statuses. 
To use Torque, we should just set environment variable ```CHECK_TORQUE``` to ```True``` when we start ```clusternapd```. Therefore, it is as simple as executing following command:
```
$ CHECK_TORQUE=True clusternapd start
```


**Using Nagios to update node states**  

When the user uses Nagios resource monitoring system, it is also good idea to take the advantage of its scalable resource checking engine. Nagios uses either its default or user defined plugins to check its resources. Just by changing those plugins or using the plugins we provide (in the directory ```/path/to/ClusterNap/plugins/```), we can make Nagios to update ClusterNap's nodes' statuses. Following is an example of how we use ClusterNap's plugins in Nagios' config file (Remember it is **NOT** ClusterNap's config file, but Nagios'. Nagios3's config files, for example, reside in ```/etc/nagios3/conf.d/``` directory by default).


```
define command{
        command_name            check_host_CN
        command_line            /path/to/ClusterNap/plugins/check_ping_CN.py\
                                                                  -H $HOSTADDRESS$ \
                                                                  -w 5000,100%     \                                               
                                                                  -c 5000,100%     \                                               
                                                                  -p 1
        }

define command{
        command_name            check_ec2_instance
        command_line            /path/to/ClusterNap/plugins/check_ec2_instance_CN.py \
                                                                        $ARG1$ $ARG2$ $ARG3$ \
                                                                            $ARG4$ -H $ARG5$
        }

define host{
        use                     generic-host
        host_name               worker001
        alias                   worker001
        address                 192.168.0.1
        check_command           check_host_CN
        }

define host{
        use                     generic-host
        host_name               ec2-instant
        alias                   ec2-instant
        address                 0
        check_commandcheck_ec2_instance!ap-northeast-1!\
                                        EC2-ACCESS-KEY!\
                                        EC2-SECRET-KEY!\
                                        instant-ID!\
                                        ec2-instant
        }

```


cntools (ClusterNap's user interface tool)
------------------------------------------
To see general info 
```
$ cntools info
```
or just ```$ cntools i```. For more help on info try ```$ cntools info -h```. 

To request a node 
```
$ cntools request nodename
```
or just ```$ cntools req nodename ```. For more exciting features of requesting nodes, try ```$ cntools request -h```.


Similarly, to release a node 
```
$ cntools release nodename
```
or just ```$ cntools rel nodename ```. For more exciting features of releasing nodes, try ```$ cntools release -h```.

To see what other interesting things cntools can do, try 

```
$ cntools -h
```


API
---
ClusterNap has API for python. Following is an example of using the API,
```
$ python
>>> import cntools
>>> cn = cntools.clusternap()
>>> cn.request('nodeA')
>>> cn.release('nodeB')
...

```
To see the more information, about the API functions

```
>>> help(cn)

```

The ```help(cn)``` will display the API functions and their roles.

Logging and troubleshooting
---------------------------

When there is a trouble, best way to track the problem is to see logs. ClusterNap records all logs in ```/path/to/ClusterNap/logs/``` directory. There are two types of log files in this directory. First one is **event** log which has the name in ```YYYY-MM-DD_event.log``` format. Another one is **error** log which has the name in ```YYYY-MM-DD_error.log```. Event log records every action ClusterNap takes such as sending ON/OFF commands, releasing/requesting nodes. On the other hand, Error log records errors such as configuration error, unknown node request error. One can easily see the ClusterNap action from the log files using ```$ tail``` command in real time. To track the events, for instance, one could do following:

```
$ tail -f /path/to/ClusterNap/logs/2014-05-15_event.log
```

and to track error logs,

```
$ tail -f /path/to/ClusterNap/logs/2014-05-15_error.log
```



If you have any ideas regarding this tool, contact to:  
  
***amgaa.hpc [at] gmail [dot] com***
