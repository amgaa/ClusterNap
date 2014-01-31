ClusterNap
==========

ClusterNap is a simple, configurable power control tool for IT infrastructures. 

ClusterNap controls the power states of your nodes (servers, VMs, switches, RAIDS, cloud instances, *whatever you can imagine*) in your system. 
After simply configuring node dependencies and ON/OFF commands for each node, all you have to do is just tell the ClusterNap which nodes you need. It will take care of the rest; for example, what other nodes it should turn-on/off in order to turn-on/off you requested/derequested nodes. Moreover, ClusterNap knows exactly in what order it should take turn-on/off actions for the nodes while keeping the system graceful. 



CASE 1:
 For example, you have a worker node called *worker1* and it is connected to central filesystem node called *master*. In most cases, if you want to use node *worker1*, then node *master* has to be ON ***before*** we turn-ON *worker1*. In ClusterNap language, we call this situation "*worker1* is ***RUN-dependent*** on *master*". 

For now, it might be easy for you to figure out that you should first turn-ON *master* and then *worker1*. Now, let's consider you have hundreds of nodes with very *complex* **RUN dependency**!! Not a funny job to do by your hand, is it? ClusterNap deals with this situation. 


 CASE 2:
 
 
 CASE 3: 
 

 CASE 4:
 
 
 

How to install
==============
ClusterNap runs on Linux computer (however, it controls any computer or resource). 
It is very easy to install. Just clone the repository and add symbolic link of ClusterNap's daemon **clusternapd** and user interface tool **cntools** to your path. 

```
$ git clone https://github.com/amgaa/ClusterNap.git
$ ln -s PATH=$PATH:/path/to/ClusterNap/bin/clusternapd /usr/local/bin/clusternapd
$ ln -s PATH=$PATH:/path/to/ClusterNap/bin/cntools /usr/local/bin/cntools
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
==================================================================
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


cntools (ClusterNap's user interface tool)
==========================================

To be continued soon ...


