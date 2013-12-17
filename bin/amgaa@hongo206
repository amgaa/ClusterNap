#! /usr/bin/env python
#
''' 

'''
import os, sys, re, pwd, datetime, time
import itertools
import get_state
import get_conf
import logset
import cninfo, cnreq, cnrel

# Get logger
log      = logset.get("cntools_event", "event.log")
errorlog = logset.get("cntools_error", "error.log")
INFO     = cninfo.cninfo().INFO.copy()
USER     = pwd.getpwuid(os.getuid())[0]
RELEASE  = os.getenv('RELEASE', False)
MAX_WAIT = os.getenv('MAX_WAIT', 900)
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

# Chech Env var MAX_WAIT
if isinstance(MAX_WAIT, basestring):
    if MAX_WAIT.isdigit() and int(MAX_WAIT) > 0:
        MAX_WAIT = int(MAX_WAIT)
    else:
        msg =  "Environment variable MAX_WAIT has given wrong value: " + MAX_WAIT
        msg += "\nWill be set to default value 900 seconds"
        log.warn(USER + ": " + msg)
        print msg
        MAX_WAIT = 900


def cnssh(args):

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

def show_help():
    msg  = "Usage: {0} <openssh_arguments>\n".format(sys.argv[0])
    msg += "For more information <openssh_arguments>, please refer to 'ssh -h'"
    print msg
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


def main( argv):

    args = argv[1:]

    if len(args) == 0:
        show_help()
        exit(1)
    if      ['-h'] in args or\
            ['--help'] in args or\
            ['-help'] in args:
        return show_help()
    
    if len(args) == 1 and \
            args in [['-h'], ['--help'], ['-help']]:
        return show_help()
    
    return cnssh(args)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
