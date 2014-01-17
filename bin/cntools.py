#! /usr/bin/env python
#
''' 
ClusterNap tools. 1.0.0


As of 2014 Jan, ssh scp, rsync, qsub are included. 

'''
import os, sys, re, pwd, datetime, time
import subprocess
import itertools
import get_state
import get_conf
import logset
import cninfo, cnreq, cnrel

# Get logger
log         = logset.get("cntools_event", "event.log")
errorlog    = logset.get("cntools_error", "error.log")
#INFO        = cninfo.cninfo().INFO.copy()
USER        = pwd.getpwuid(os.getuid())[0]
RELEASE     = os.getenv('RELEASE', False)
MAX_WAIT    = os.getenv('MAX_WAIT', 900)
PBS_RELEASE = os.getenv('PBS_RELEASE', False)


# Chech Env var RELEASE
if isinstance(RELEASE, basestring):
    if RELEASE in ['TRUE', 'True', 'true', '1']:
        RELEASE = True
    elif RELEASE in ['FALSE', 'False', 'false', '0']:
        RELEASE = False
    else:
        msg = "Environment variable RELEASE has given wrong value: " + RELEASE
        msg += "\nWill be set to default value 'False'"
        log.warn(USER + ": " + msg)
        print msg
        RELEASE = False

# Check Env var RELEASE
if isinstance(PBS_RELEASE, basestring):
    if PBS_RELEASE in ['TRUE', 'True', 'true', '1']:
        PBS_RELEASE = True
    elif PBS_RELEASE in ['FALSE', 'False', 'false', '0']:
        PBS_RELEASE = False
    else:
        msg = "Environment variable PBS_RELEASE has given wrong value: " + PBS_RELEASE
        msg += "\nWill be set to default value 'False'"
        log.warn(USER + ": " + msg)
        print msg
        PBS_RELEASE = False

# Check Env var MAX_WAIT
if isinstance(MAX_WAIT, basestring):
    if MAX_WAIT.isdigit() and int(MAX_WAIT) > 0:
        MAX_WAIT = int(MAX_WAIT)
    else:
        msg =  "Environment variable MAX_WAIT has given wrong value: " + MAX_WAIT
        msg += "\nWill be set to default value 900 seconds"
        log.warn(USER + ": " + msg)
        print msg
        MAX_WAIT = 900

def get_info():
#    return cninfo.cninfo().INFO.copy()
    return clusternap().get_info()

def cnssh(args):
    INFO = get_info()
    # Check if <user> is written correctly
    for arg in args:
        if arg == '-l':
            msg = "Please do not use option '-l <user>'. Instead, use '<user>@<hostname>'. "
            print msg
            log.info(USER + ": " + msg)
            return 1

    hostname = get_hostname(args)
    # TODO: If host is given by its IP, we should search the hostname of that ip

    if not hostname in INFO.keys():
        msg = "{0} is not defined in ClusterNap. Error".format(hostname)
        print msg
        errorlog.error(USER + ": " + msg)
        return 1

    state = get_state.get_state().node_state(hostname)
    cnreq.cnreq().request_node(hostname)# Request it anyway
    if state == 1:
        if try_ssh(args) == 0:
            if RELEASE:
                cnrel.cnrel().release_node(hostname)
            return 0
        else:
            return 1

    # If host is in OFF or UNKNOWN state
    # Request it
    print "We are waking up {0}. Please be patient.".format(hostname)
    print "It might take several minutes."
    time_passed = 0
    while state != 1 and time_passed < MAX_WAIT: 
        time.sleep(1)
        time_passed += 1
        state = get_state.get_state().node_state(hostname)
    
    if time_passed >= MAX_WAIT or state != 1:
        msg = "Sorry. Could not wake up '{0}' in {1} seconds.".format(hostname, MAX_WAIT)
        print msg
        log.warning(USER + ": " + msg)
        return 1

    if state == 1:
        if try_ssh(args) == 0:
            if RELEASE:
                cnrel.cnrel().release_node(hostname)  # Release after connection??
            return 0
        else:
            return 1

    msg = "Unexpected error."
    print msg
    errorlog.error(USER + ": " + msg)
    return 1

def cnscp(args):
    hostname = get_hostname(args)
    INFO = get_info()
    # TODO: If host is given by its IP, we should search the hostname of that ip

    if not hostname in INFO.keys():
        msg = "{0} is not defined in ClusterNap. Error".format(hostname)
        print msg
        errorlog.error(USER + ": " + msg)
        return 1

    state = get_state.get_state().node_state(hostname)
    cnreq.cnreq().request_node(hostname)# Request it anyway
    if state == 1:
        if try_scp(args) == 0:
            if RELEASE:
                cnrel.cnrel().release_node(hostname)
            return 0
        else:
            return 1

    # If host is in OFF or UNKNOWN state
    # Request it
    print "We are waking up {0}. Please be patient.".format(hostname)
    print "It might take several minutes."
    time_passed = 0
    while state != 1 and time_passed < MAX_WAIT: 
        time.sleep(1)
        time_passed += 1
        state = get_state.get_state().node_state(hostname)
    
    if time_passed >= MAX_WAIT or state != 1:
        msg = "Sorry. Could not wake up '{0}' in {1} seconds.".format(hostname, MAX_WAIT)
        print msg
        log.warning(USER + ": " + msg)
        return 1

    if state == 1:
        if  try_scp(args) == 0:
            if RELEASE:
                cnrel.cnrel().release_node(hostname)  # Release after connection??
            return 0
        else:
            return 1

    msg = "Unexpected error."
    print msg
    errorlog.error(USER + ": " + msg)
    return 1

def cnrsync(args):
    hostname = get_hostname(args)
    INFO = get_info()
    # TODO: If host is given by its IP, we should search the hostname of that ip

    if not hostname in INFO.keys():
        msg = "{0} is not defined in ClusterNap. Error".format(hostname)
        print msg
        errorlog.error(USER + ": " + msg)
        return 1

    state = get_state.get_state().node_state(hostname)
    cnreq.cnreq().request_node(hostname)# Request it anyway
    if state == 1:
        if try_rsync(args) == 0:
            if RELEASE:
                cnrel.cnrel().release_node(hostname)
            return 0
        else:
            return 1

    # If host is in OFF or UNKNOWN state
    # Request it
    print "We are waking up {0}. Please be patient.".format(hostname)
    print "It might take several minutes."
    time_passed = 0
    while state != 1 and time_passed < MAX_WAIT: 
        time.sleep(1)
        time_passed += 1
        state = get_state.get_state().node_state(hostname)
    
    if time_passed >= MAX_WAIT or state != 1:
        msg = "Sorry. Could not wake up '{0}' in {1} seconds.".format(hostname, MAX_WAIT)
        print msg
        log.warning(USER + ": " + msg)
        return 1

    if state == 1:
        if try_rsync(args) == 0:
            if RELEASE:
                cnrel.cnrel().release_node(hostname)  # Release after connection??
            return 0
        else:
            return 1

    msg = "Unexpected error."
    print msg
    errorlog.error(USER + ": " + msg)
    return 1


def try_ssh(args):
    cmd = "/usr/bin/ssh"
    for arg in args:
        cmd += " " + arg

    print "Connecting through ssh."
    if not os.system(cmd) == 0: # Failed to connect
        msg = "Failed to execute '{0}'. Will try again in 5 seconds".format(cmd)
        print msg
        errorlog.error(USER + ": " + msg)
        time.sleep(5)
        if not os.system(cmd) == 0: 
            msg = "Sorry. Command '{0}' failed!".format(cmd)
            print msg
            errorlog.error(USER + ": " + msg)
            return 1
        else:
            return 0            # succeeded
    else:
        return 0                # Succeeded
    

def try_scp(args):
    cmd = "/usr/bin/scp"
    for arg in args:
        cmd += " " + arg
    print "Trying scp."
    if not os.system(cmd) == 0: # Failed to connect
        msg = "Failed to execute '{0}'. Will try again in 5 seconds".format(cmd)
        print msg
        errorlog.error(USER + ": " + msg)
        time.sleep(5)
        if not os.system(cmd) == 0: 
            msg = "Sorry. Command '{0}' failed!".format(cmd)
            print msg
            errorlog.error(USER + ": " + msg)
            return 1
        else: 
            return 0               
    else:
        return 0                # Succeeded

def try_rsync(args):
    cmd = "/usr/bin/rsync"
    for arg in args:
        cmd += " " + arg

    print "Connecting ..."
    if not os.system(cmd) == 0: # Failed to connect
        msg = "Failed to execute '{0}'. Will try again in 5 seconds".format(cmd)
        print msg
        errorlog.error(USER + ": " + msg)
        time.sleep(5)
        if not os.system(cmd) == 0: 
            msg = "Sorry. Command '{0}' failed!".format(cmd)
            print msg
            errorlog.error(USER + ": " + msg)
            return 1
        else:
            return 0            # Succeeded
    else:
        return 0                # Succeeded

# Returns all jobs returned by qstat -f
# Returns list of a dictionary [{'Job Id': ID }, {'Resource_List.host': hostnames}, {'job_state': jobs_state}]
def torque_jobs():
    cmd = "qstat -f"
    ret = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    ret.wait()
    jobs = ret.communicate()[0].split("\n\n")
    jobs = [job for job in jobs if job != ''] # exclude empty item
    jobs = map(str.splitlines, jobs)
    ret_jobs = {}

    for job in jobs:
        # Get necessary values: Job Id, job_state, hostnames etc.
        key_words = ['Job Id', 'job_state', 'Resource_List.host', 'Resource_List.nodes']
        job = [line for line in job if any(word in line for word in key_words) ]
        job = [re.split(':|=', line)             for line in job]
        job = [{line[0].strip():line[1].strip()} for line in job ]    
        
        if job != [] and job[0].has_key('Job Id'):
            ret_jobs[job[0]['Job Id']] = {}
            for item in job:
                ret_jobs[job[0]['Job Id']].update(item)

    return ret_jobs
    
# Returns name of nodes requested by jobs which have state of Q or R or ...
def qsub_nodes():
    important_states = ['Q', 'E', 'R', 'T']
    jobs = torque_jobs()
    request_nodes = list()
    
    for key, val in jobs.items(): # 
        # Job is finished or has not SPECIFIED necessary node name
        if val['job_state'] not in important_states:
            del jobs[key]

    for key, val in jobs.items():
        if val.has_key('Resource_List.host'):
            nodes = val['Resource_List.host'].split('+')
            nodes = map(str.strip, nodes)
            for node in nodes:
                if node not in request_nodes:
                    request_nodes.append(node)

        # Syntax of Resource_List.nodes: 
        # {<node_count> | <hostname>} [:ppn=<ppn>][:gpus=<gpu>] [:<property>[:<property>]...] [+ ...]
        nodes = val['Resource_List.nodes'].split('+')
        nodes = map(str.strip, nodes)
        for node in nodes:
            node = node.split(':')[0]
            if not node.isdigit()and node not in request_nodes:
                request_nodes.append(node)

    return request_nodes

# Returns all nodes defined in torque
def torque_nodes():
    nodes = list()
    cmd            = "pbsnodes -l all"
    ret = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    ret.wait()

    for pair in ret.communicate()[0].splitlines():
        node, value = map( str.strip, pair.split() )
        nodes.append(node)
        
    return nodes



# If any node in argument "nodes" list is not requested in clusternap, 
# request that node.
def check_and_request(nodes):
    INFO = get_info()
    for node in nodes:
        if not INFO.has_key(node):
            msg = "node '{0}' is not defined in ClusterNap.".format(node)
            log.warning(USER + ": " + msg)

    for node, val in INFO.items():
        if node in nodes and  val[1] == 'Free':
                cnreq.cnreq().request_node(node)


# If any node in argument "nodes" list is requested in clusternap, 
# release that node.
def check_and_release(nodes):
    INFO = get_info()
    for node in nodes:
        if not INFO.has_key(node):
            msg = "node '{0}' is not defined in ClusterNap.".format(node)
            log.warning(USER + ": " + msg)
#    log.info("Release node passed: " + str(nodes))        
    for node, val in INFO.items():
        if node in nodes and  val[1] == 'Requested':
#            log.info("Will release: " + node)
            cnrel.cnrel().release_node(node)

# Checks requested hosts in qsub -f. 
# If those nodes are not requested in ClusterNap, request them.
# Checks all other non-requested nodes in "pbsnodes -l all". 
# If any of these nodes are requested in ClusterNap, release them.
def action_pbsnodes(pbs_release):
    qnodes = qsub_nodes()
    tnodes = torque_nodes()
    check_and_request(qnodes)
#    log.info("ACTION_PBSNODES called")
#    log.info("PBS_RELEASE VALUE is: "  + str(pbs_release))
#    log.info("qsub nodes: " + str(qnodes))
#    log.info("torque nodes: " + str(tnodes))
    if pbs_release:
        rel_nodes = [node for node in tnodes if not node in qnodes]
#        log.info("release nodes are: " + str(rel_nodes))
        check_and_release(rel_nodes)
    return

# Check clusternap nodes and unless included in "nodes" release them
# def check_and_release(nodes):

# Runs qsub command. 
# After submitting job by qsub, checks nodes 
# and if any qsub requested node is not requested in clusternap, request it. 
def cnqsub(args, stdin):
    qsub = "qsub" #It maybe should be absolute path 
    cmd = qsub
    for arg in args:
        cmd += " " + arg

#    ret = subprocess.Popen(cmd, shell=True, stdin=stdin, stdout=subprocess.PIPE)
    ret = subprocess.Popen(cmd, shell=True, stdin=stdin)
    ret.wait()
    action_pbsnodes(PBS_RELEASE)

    return 


# TODO (new): Lets make convention that we always use username, 
# and do not use -l option. Instead lets use user@hostname.
def get_hostname( args):
    tmp_args = args[:]

    for arg in args:
        if '@' in arg:
            arg = arg.split('@')[1]
            arg = arg.split(':')[0]
            if is_hostname(arg):
                return arg

            msg = "Could not parse hostname from the args: " + " ".join(args)
            print msg
            errorlog.error(USER + ": " + msg)
            exit(1)
    msg = "Wrong arguments: " + " ".join(args)
    msg += "\nArguments should contain at least username and hostname."
    print msg
    errorlog.error(USER + ": " + msg)
    exit(1)


def is_hostname( hostname):
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def show_help_main():
    msg  = "Usage: {0} [OPTIONS] [ARGUMENTS]\n".format(sys.argv[0])
    msg += "OPTIONS:\n"
    msg += "\tinfo    -- shows clusternap nodes information.\n"
    msg += "\trelease -- releases node from ClusterNap.\n"
    msg += "\trequest -- requests node to ClusterNap.\n"
    msg += "\tssh     -- connects to clusternap node by ssh. If node in question is not requested, request its.\n"
    msg += "\tscp     -- scp to clusternap node. If node in question is not requested, requests it.\n"
    msg += "\trsync   -- rsync to clusternap node. If node in question is not requested, requests it.\n"
    msg += "\tqsub    -- submits job by qsub. If requested resource (clusternap node) is not requested, request it.\n"
    print msg
    return 

def show_help_ssh():
    msg  = "Usage: {0} ssh <openssh_arguments>\n".format(sys.argv[0])
    msg += "For more information on <openssh_arguments>, please refer to 'ssh -h'"
    print msg
    return

def show_help_scp():
    msg  = "Usage: {0} <scp_arguments>\n".format(sys.argv[0])
    msg += "For more information on <scp_arguments>, please refer to 'scp -h'"
    print msg
    return

def show_help_rsync():
    msg  = "Usage: {0} rsync <rsync_arguments>\n".format(sys.argv[0])
    msg += "For more information on <rsync_arguments>, please refer to 'rsync -h'"
    print msg
    return

def show_help_qsub():
    msg  = "Usage: {0} qsub <qsub_arguments and stdin >\n".format(sys.argv[0])
    msg += "For more information on <qsub_arguments and stdin >, please refer to 'man qsub'"
    print msg
    return

def main(argv, stdin):

    args = argv[1:]

    if len(args) == 0:
        show_help_main()
        exit(1)

#    if      ['-h'] in args or\
#            ['--help'] in args or\
#            ['-help'] in args:
#        return show_help()
    
    if len(args) == 1 and \
            args in [['-h'], ['--help'], ['-help']]:
        return show_help_main()
    
    arg_info = ['info', '--info', 'i', '--i']
    arg_rel  = ['release', 'rel', '--release', '--rel']
    arg_req  = ['request', 'req', '--request', '--req']
    arg_ssh  = ['ssh', '--ssh', 'cnssh', '--cnssh']
    arg_scp  = ['scp', '--scp', 'cnscp', '--cnscp']
    arg_rsync= ['rsync', '--rsync', 'cnrsync', '--cnrsync']
    arg_qsub = ['qsub', '--qsub', 'cnqsub', '--cnqsub']

    if args[0] not in arg_info + arg_rel + arg_req + arg_ssh + arg_scp + arg_rsync + arg_qsub:
        print "Wrong option: Please see help"
        return show_help_main()
    
    # INFO
    if args[0] in arg_info:
        return cninfo.cninfo().main(args)

    # RELEASE
    if args[0] in arg_rel:
        return cnrel.cnrel().main(args)

    # REQUEST
    if args[0] in arg_req:
        return cnreq.cnreq().main(args)

    helpkeys = ['-h', '-help', '--help', 'help','--help']

    # SSH
    if args[0] in arg_ssh:
        args = args[1:]
        if any(word in args for word in helpkeys) or len(args) == 0:
            return show_help_ssh()
        return cnssh(args)

    # SCP
    if args[0] in arg_scp:
        args = args[1:]
        if any(word in args for word in helpkeys) or len(args) == 0:
            return show_help_scp()
        return cnscp(args)

    # RSYNC
    if args[0] in arg_rsync:
        args = args[1:]
        if any(word in args for word in helpkeys) or len(args) == 0:
            return show_help_rsync()
        return cnrsync(args)
    
    # QSUB
    if args[0] in arg_qsub:
        args = args[1:]
        if len(args) == 0 and stdin.isatty(): # stdin.isatty() returns false if there is data 
            return show_help_qsub()
        if any(word in args for word in helpkeys):
            return show_help_qsub()
        return cnqsub(args, stdin)


class clusternap(object):
    """ API of ClusterNap """
    
    def __init__(self):
        pass
    
    def get_info(self):
        """ 
        Returns information of all nodes defined in ClusterNap.
         dictionary of nodes and their info:
         example:
                    {nodename:[powerstate, request_state, request_user, request_date]}
        """
        return cninfo.cninfo().get_info()

    def get_nodes_conf(self):
        """
        Returns list of ClusterNap defined nodes.
        CAUTIONS: Maybe, we should not disclose this information to users!!!!
        """
        return get_conf.get_conf().get_nodes_conf()
       
#    def get_commands_conf(self):
#        """
#        Returns list of ClusterNap defined commands.
#        CAUTIONS: Maybe, we should not disclose this information to users!!!!
#        """
#        return cninfo.cninfo().get_commands()
#        return get_conf.get_conf().COMMANDS
#        return get_conf.get_conf().get_commands_conf()

#    def get_types_conf(self):
#        """
#        Returns list of ClusterNap defined commands.
#        """
#        return get_conf.get_conf().get_types_conf()

#    def get_configs(self):
#        """
#        Returns dictionary of configs:
#        {
#         'nodes'   :{dict of nodes' configs}, 
#         'commands':{dict of commands configs}, 
#         'types'   :{dict of types' configs}
#         }
#        """

#        configs = {}

#        configs['nodes']    = {}
#        configs['commands'] = {}
#        configs['types']    = {}

#        configs['nodes'].update(self.get_nodes_conf())
#        configs['commands'].update(self.get_commands_conf())
#        configs['types'].update(self.get_types_conf())

#        return configs
        
#    def update_configs(self, configs):
#        """
#        Gets dictionary of configs.
#        Updates config files according that dictionary. 
#        If it seems some configs are deleted in the input dictionary,
#        in config files, that configs should be commented out (not deleted). 
#        """

#        return get_conf.get_conf().update_configs(config)
        
    def get_node_info(self, nodename):
        """
        returns info of given node.
        info: power state, 
              request state, 
              requested username(if requested), 
              requested date (if requested)
        """
        return cninfo.cninfo().get_node_info(nodename)

    def get_power_state(self, nodename):
        """ 
        Returns powerstate of given node. 
        Return value, one of: 'On', 'Off', 'Unknown'
        """
        return cninfo.cninfo().get_node_info(nodename)[0]

    def get_request_state(self, nodename):
        """
        Returns one of 'Free' or 'Requested'
        """
        return cninfo.cninfo().get_node_info(nodename)[1]

    def get_request_user(self, nodename):
        """
        If fiven node is reserved, returns who reserved that node.
        Else, returns 'N/A'
        """
        return cninfo.cninfo().get_node_info(nodename)[2]


    def get_request_date(self, nodename):
        """
        If node is requested, returns the date of reservation.
        Else, returns 'N/A'. 
        """
        return cninfo.cninfo().get_node_info(nodename)[3]

    def get_dependency(self, nodename, dep_type):
        """
        Returns OFF dependency of a given node.
        arg1: node name
        arg2: dependency type. One of 'on', 'off', 'run'
        Dependency is in Conjunctive Normal Form (CNF).
        Example: (nodeA and nodeB) or (nodeC) .... is represented as
        [['nodeA', 'nodeB'], ['nodeC']]
        """
        on  = ['on',  'ON',  'On',  'on_dependency' ]
        off = ['off', 'OFF', 'Off', 'off_dependency']
        run = ['run', 'RUN', 'Run', 'run_dependency']

        if dep_type in on:
            dep_type = 'on'
        elif dep_type in off:
            dep_type = 'off'
        elif dep_type in run:
            dep_type = 'run'
        else:
            print "Unknown dependency type give: " + str(dep_type)
            return 1
            
        dep_type = dep_type + "_dependencies"
 
        try:
            dep = list()
            tmp = self.get_nodes_conf()[nodename][dep_type]
            dep = map(str.strip,  tmp.strip().split('|') )
            dep = [map(str.strip, clause.split(',')) for clause in dep]
            return dep
        except KeyError:
            print "Error occured. Unknown node? "
            return 1


    def release(self, nodename):
        """
        Try to release given node.
        If successfully released or node is already released, return 0
        If could not release for some reason (someone else requested, etc.), return 1
        """
        return cnrel.cnrel().release_node(nodename)

    def request(self, nodename):
        """
        Try to request given node.
        If successfully requested or node is already requested, return 0
        If could not request for some reason, return 1
        """
        return cnreq.cnreq().request_node(nodename)

    def set_power_state(self, nodename, state):
        """ 
        Sets power state of given node.
        The argument "state" is a string of either 
                   "on"      (or one of 'ON',       1, 'On'     ), 
                   "off"     (or one of 'OFF',      0, 'Off'    ), 
                   "unknown" (or one of 'UNKNOWN', -1, 'Unknown')

        CAUTIONS: Setting power states to a node might cause serious malfunction in the system.
                  Be very careful!!!!
        """
        return get_state.get_state().set_state(nodename, state)

    def set_dependency(self, nodename, dep_type, dependency):
        """
        Sets dependency for a node. Overwrites old dependency. 
        arg1: node name. For example, 'nodeA'
        arg2: which dependency? one of ('on', 'off', 'run')
        arg3: dependency list in CNF. For example, [['nodeA', 'nodeB'], ['nodeC', 'nodeA'], ['nodeF']]
        """
        try:
            return get_conf.get_conf().set_dependency(nodename, dep_type, dependency)
        except Exception as m:
            print m
            print "Some error occured setting dependency for node '" + nodename + "'. Please check you node and dependency values!"          
            return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv, sys.stdin))
