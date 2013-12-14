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

max_wait = 900
rel_after_ssh   = False
rel_after_scp   = False
rel_after_rsync = False

class cnssh:
    def __init__ (self):
        # Get logger
        self.log      = logset.get("cnssh_event", "event.log")
        self.errorlog = logset.get("cnssh_error", "error.log")
        self.INFO     = cninfo.cninfo().INFO.copy()
        self.USER         = pwd.getpwuid(os.getuid())[0]

    def cnssh(self, args):
        hostname = self.get_hostname(args)
        # TODO: If host is given by its IP, we should search the hostname of that ip

        if not hostname in self.INFO.keys():
            msg = "{0} is not defined in ClusterNap. Error".format(hostname)
            print msg
            self.errorlog.error(self.USER + ": " + msg)
            return 1

        state = get_state.get_state().node_state(hostname)
        cnreq.cnreq().request_node(hostname)# Request it anyway
        if state == 1 and self.try_ssh(args) == 0:
            if rel_after_ssh:
                cnrel.cnrel().release_node(hostname)
            return 0

        # If host is in OFF or UNKNOWN state
        # Request it
        print "We are waking up {0}. Please be patient.".format(hostname)
        print "It might take several minutes."
        time_passed = 0
        while state != 1 and time_passed < max_wait: 
            time.sleep(1)
            time_passed += 1
            state = get_state.get_state().node_state(hostname)
        
        if time_passed >= max_wait or state != 1:
            msg = "Sorry. Could not wake up '{0}' in {1} seconds.".format(hostname, max_wait)
            print msg
            self.log.warning(self.USER + ": " + msg)
            return 1

        if state == 1 and self.try_ssh(args) == 0:
            if rel_after_ssh:
                cnrel.cnrel().release_node(hostname)  # Release after connection??
            return 0

        msg = "Unexpected error."
        print msg
        self.errorlog.error(self.USER + ": " + msg)
        return 1
    
    def cnscp(self, args):
        hostname = self.get_hostname(args)
        # TODO: If host is given by its IP, we should search the hostname of that ip

        if not hostname in self.INFO.keys():
            msg = "{0} is not defined in ClusterNap. Error".format(hostname)
            print msg
            self.errorlog.error(self.USER + ": " + msg)
            return 1

        state = get_state.get_state().node_state(hostname)
        cnreq.cnreq().request_node(hostname)# Request it anyway
        if state == 1 and self.try_scp(args) == 0:
            if rel_after_scp:
                cnrel.cnrel().release_node(hostname)
            return 0

        # If host is in OFF or UNKNOWN state
        # Request it
        print "We are waking up {0}. Please be patient.".format(hostname)
        print "It might take several minutes."
        time_passed = 0
        while state != 1 and time_passed < max_wait: 
            time.sleep(1)
            time_passed += 1
            state = get_state.get_state().node_state(hostname)
        
        if time_passed >= max_wait or state != 1:
            msg = "Sorry. Could not wake up '{0}' in {1} seconds.".format(hostname, max_wait)
            print msg
            self.log.warning(self.USER + ": " + msg)
            return 1

        if state == 1 and self.try_scp(args) == 0:
            if rel_after_scp:
                cnrel.cnrel().release_node(hostname)  # Release after connection??
            return 0

        msg = "Unexpected error."
        print msg
        self.errorlog.error(self.USER + ": " + msg)
        return 1

    def cnrsync(self, args):
        hostname = self.get_hostname(args)
        # TODO: If host is given by its IP, we should search the hostname of that ip

        if not hostname in self.INFO.keys():
            msg = "{0} is not defined in ClusterNap. Error".format(hostname)
            print msg
            self.errorlog.error(self.USER + ": " + msg)
            return 1

        state = get_state.get_state().node_state(hostname)
        cnreq.cnreq().request_node(hostname)# Request it anyway
        if state == 1 and self.try_rsync(args) == 0:
            if rel_after_rsync:
                cnrel.cnrel().release_node(hostname)
            return 0

        # If host is in OFF or UNKNOWN state
        # Request it
        print "We are waking up {0}. Please be patient.".format(hostname)
        print "It might take several minutes."
        time_passed = 0
        while state != 1 and time_passed < max_wait: 
            time.sleep(1)
            time_passed += 1
            state = get_state.get_state().node_state(hostname)
        
        if time_passed >= max_wait or state != 1:
            msg = "Sorry. Could not wake up '{0}' in {1} seconds.".format(hostname, max_wait)
            print msg
            self.log.warning(self.USER + ": " + msg)
            return 1

        if state == 1 and self.try_rsync(args) == 0:
            if rel_after_rsync:
                cnrel.cnrel().release_node(hostname)  # Release after connection??
            return 0

        msg = "Unexpected error."
        print msg
        self.errorlog.error(self.USER + ": " + msg)
        return 1


    def try_ssh(self, args):
        cmd = "/usr/bin/ssh"
        for arg in args:
            cmd += " " + arg

        print "Connecting through ssh."
        if not os.system(cmd) == 0: # Failed to connect
            msg = "Failed to execute '{0}'. Will try again in 5 seconds".format(cmd)
            print msg
            self.errorlog.error(self.USER + ": " + msg)
            time.sleep(5)
            if not os.system(cmd) == 0: 
                msg = "Sorry. Command '{0}' failed!".format(cmd)
                print msg
                self.errorlog.error(self.USER + ": " + msg)
                return 1
        else:
            return 0                # Succeeded
        

    def try_scp(self, args):
        cmd = "/usr/bin/scp"
        for arg in args:
            cmd += " " + arg
        print "Trying scp."
        if not os.system(cmd) == 0: # Failed to connect
            msg = "Failed to execute '{0}'. Will try again in 5 seconds".format(cmd)
            print msg
            self.errorlog.error(self.USER + ": " + msg)
            time.sleep(5)
            if not os.system(cmd) == 0: 
                msg = "Sorry. Command '{0}' failed!".format(cmd)
                print msg
                self.errorlog.error(self.USER + ": " + msg)
                return 1
        else:
            return 0                # Succeeded

    def try_rsync(self, args):
        cmd = "/usr/bin/rsync"
        for arg in args:
            cmd += " " + arg

        print "Connecting ..."
        if not os.system(cmd) == 0: # Failed to connect
            msg = "Failed to execute '{0}'. Will try again in 5 seconds".format(cmd)
            print msg
            self.errorlog.error(self.USER + ": " + msg)
            time.sleep(5)
            if not os.system(cmd) == 0: 
                msg = "Sorry. Command '{0}' failed!".format(cmd)
                print msg
                self.errorlog.error(self.USER + ": " + msg)
                return 1
        else:
            return 0                # Succeeded

    def show_help(self):
        msg  = "Usage: {0} <openssh_arguments>\n".format(sys.argv[0])
        msg += "For more information <openssh_arguments>, please refer to 'ssh -h'"
        print msg
        return 

    # TODO (new): Lets make convention that we always use username, 
    # and do not use -l option. Instead lets use user@hostname.
    # TODO: We should validate the hostname!
    def get_hostname(self, args):
        tmp_args = args[:]

#        for arg in args:
#            if arg == '-l':
#                msg = "Please do not use option '-l <user>'. Instead, use '<user>@<hostname>'. "
#                print msg
#                self.log.info(self.USER + ": " + msg)
#                exit(1)
            
        for arg in args:
            if '@' in arg:
                arg = arg.split('@')[1]
                arg = arg.split(':')[0]
                if self.is_hostname(arg):
                    return arg

                msg = "Could not parse hostname from the args: " + " ".join(args)
                print msg
                self.errorlog.error(self.USER + ": " + msg)
                exit(1)
        msg = "Wrong arguments: " + " ".join(args)
        msg += "\nArguments should contain at least username and hostname."
        print msg
        self.errorlog.error(self.USER + ": " + msg)
        exit(1)


    def is_hostname(self, hostname):
        if len(hostname) > 255:
            return False
        if hostname[-1] == ".":
            hostname = hostname[:-1] # strip exactly one dot from the right, if present
        allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split("."))


    def main(self, argv):

        args = argv[1:]

        if len(args) == 0:
            self.show_help()
            exit(1)
        if      ['-h'] in args or\
                ['--help'] in args or\
                ['-help'] in args:
            return self.show_help()
        
        if len(args) == 1 and \
                args in [['-h'], ['--help'], ['-help']]:
            return self.show_help()
        
        return self.cnssh(args)

if __name__ == "__main__":
    sys.exit(cnssh().main(sys.argv))
