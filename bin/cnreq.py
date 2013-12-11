#!/usr/bin/env python

import os, sys, re, pwd, datetime, grp
import itertools
import get_state
import get_conf
import cninfo
import logset

class cnreq:
    def __init__(self):
        self.log          = logset.get("cnreq", "event.log")
        self.errorlog     = logset.get("cnreqerr", "error.log")
        self.REQUEST_DIR  = os.path.dirname(os.path.abspath(__file__))
        self.REQUEST_DIR += "/../requested/nodes/"
        self.USER         = pwd.getpwuid(os.getuid())[0]
        self.INFO         = cninfo.cninfo().INFO.copy()
        self.INFO_LIST    = cninfo.cninfo().INFO_LIST[:]


    def request_node(self, node):
        # If node is not defined in ClusterNap, say so. return
        if not self.INFO.has_key(node):
            msg = "'{0}': not defined in ClusterNap. Request for this node cannot be done!".format(node)
            print msg
            self.log.warn(self.USER + ": " + msg)
            return

        # If the user is "root", do whatever he pleases!
        if self.USER == "root":
            uid = pwd.getpwnam("root").pw_uid
            gid = grp.getgrnam("root").gr_gid
            if not open(self.REQUEST_DIR + node, 'a'):
                msg = "'{0}': Request error!".format(node)
                print msg
                self.errorlog.error(self.USER + ": " + msg)
                exit(1)

            os.chown(self.REQUEST_DIR + node, uid, gid)
            msg = "'{0}': request done!".format(node)
            print msg
            self.log.info(self.USER + ": " + msg)
            return
 
        # If not requested, do request
        if self.INFO[node][1] == "Free":
            if not open(self.REQUEST_DIR + node, 'a'):
                msg = "'{0}': Request error!".format(node)
                print msg
                self.errorlog.error(self.USER + ": " + msg)
                exit(1)

            msg = "'{0}': request done!".format(node)
            print msg
            self.log.info(self.USER + ": " + msg)
            return

        # If already requested, say so
        if self.INFO[node][1] == "Requested":
            # Requested by the user itself
            if self.USER == self.INFO[node][2]:
                msg = "'{0}': You already requested this node".format(node)
                print msg
                self.log.info(self.USER + ": " + msg)
                return

            # Someone else requested
            msg = "'{0}': Someone else already requested this node".format(node)
            print msg
            self.lof.info(self.USER + ": " + msg)
            return

    def get_nodes(self, nlist):
        
        return nlist
    
    def main(self, argv):
#        print self.INFO
        args = argv[1:]
        nodes = self.get_nodes(args)
        for node in nodes:
            self.request_node(node)
        return



if __name__ == "__main__":
    sys.exit(cnreq().main(sys.argv))
