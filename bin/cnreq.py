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
#        self.INFO         = cninfo.cninfo().INFO.copy()
#        self.INFO_LIST    = cninfo.cninfo().INFO_LIST[:]


    def request_node(self, node):
        # If node is not defined in ClusterNap, say so. return
        INFO         = cninfo.cninfo().get_info()
        if not INFO.has_key(node):
#            msg = "'{0}': not defined in ClusterNap. Request cannot be done!".format(node)
            msg = "'%s': not defined in ClusterNap. Request cannot be done!" % (node)
            print msg
            self.log.warn(self.USER + ": " + msg)
            return 1

        # If the user is "root", do whatever he pleases!
        if self.USER == "root":
            uid = pwd.getpwnam("root").pw_uid
            gid = grp.getgrnam("root").gr_gid
            if not open(self.REQUEST_DIR + node, 'a'):
#                msg = "'{0}': Request error!".format(node)
                msg = "'%s': Request error!" % (node)
                print msg
                self.errorlog.error(self.USER + ": " + msg)
#                exit(1)
                return 1

            os.chown(self.REQUEST_DIR + node, uid, gid)
#            msg = "'{0}': request done!".format(node)
            msg = "'%s': request done!" % (node)
            print msg
            self.log.info(self.USER + ": " + msg)
            return 0
 
        # If not requested, do request
        if INFO[node][1] == "Free":
            if not open(self.REQUEST_DIR + node, 'a'):
#                msg = "'{0}': Request error!".format(node)
                msg = "'%s': Request error!" % (node)
                print msg
                self.errorlog.error(self.USER + ": " + msg)
#                exit(1)
                return 1

#            msg = "'{0}': request done!".format(node)
            msg = "'%s': request done!" % (node)
            print msg
            self.log.info(self.USER + ": " + msg)
            return 0

        # If already requested, say so
        if INFO[node][1] == "Requested":
            # Requested by the user itself
            if self.USER == INFO[node][2]:
#                msg = "'{0}': You already requested".format(node)
                msg = "'%s': You already requested" % (node)
                print msg
                self.log.info(self.USER + ": " + msg)
                return 0

            # Someone else requested
#            msg = "'{0}': Someone else already requested".format(node)
            msg = "'%s': Someone else already requested" % (node)
            print msg
            self.log.info(self.USER + ": " + msg)
            return 0


    def get_nodes(self, arglist):
        nlist = list() # node list
        for arg in arglist:
            self.check_arg(arg) # Checks if arg is written correctly
            nlist += self.get_multiple(arg) 
        return nlist

    # Should be further fixed. Checks more
    def check_arg(self, arg):
        if arg.startswith("-"):
#            msg = "Error in argument. Wrong argument: '{0}'".format(arg)
            msg = "Error in argument. Wrong argument: '%s'" % (arg)
            print msg
            self.errorlog.error(self.USER + ": " + msg)
            exit(1)

    # Input example: foo[00-02, AA]
    # Return: ['foo00', 'foo01', 'foo02', 'fooAA']
    def get_multiple(self, arg):
        nlist = list()
        expr = self.get_expr(arg)
        if not expr:
            nlist.append(arg)
            return nlist

        items = self.get_items(expr)
        for item in items:
            nlist.append(re.sub("\[(.+?)\]", item, arg ) )
        return nlist

    # Input ex: "120-123, 145, 147"
    # return  : ["120", "121", "122", "123", "145", "147"]    
    def get_items(self, exprs):
        if not exprs:
            return
        
        itemlist = list()
        itemstr = map( str.strip, exprs.split(","))

        for items in itemstr:
            items = map(str.strip, items.split("-"))

            if len(items) == 1:
                itemlist.append(items[0]) # Can be digit and string

            elif         len(items) == 2    \
                     and items[0].isdigit() \
                     and items[1].isdigit():    # can only be integer
                for i in range(int(items[0]), int(items[1]) + 1 ):
                    itemlist.append(str(i).zfill(len(items[1])))
            else:
#                msg = "Error in argument. Unknown expression: '{0}'".format(exprs)
                msg = "Error in argument. Unknown expression: '%s'" % (exprs)
                print msg
                self.errorlog.error(self.USER + ": " + msg)
                exit(1)
                
        return itemlist


    def get_expr(self, arg):
        expr = re.findall(r"\[(.+?)\]", arg)
        if expr == []: #empt
            return 0
        if len(expr) != 1:
#            msg = "Wrong argument in '{0}'.".format(arg)
            msg = "Wrong argument in '%s'." % (arg)
            print msg
            self.errorlog.error(self.USER + ": " + msg)
            exit(1)
        
        return expr[0]

    def show_help(self):
#        msg1 = "Usage: {0} request < nodes to request>\n".format(sys.argv[0])
        msg1 = "Usage: %s request < nodes to request>\n" % (sys.argv[0])
#        msg2 = "Example: \n\tcommand \"{0} foo[00-02] bar\"\n".format(sys.argv[0])
        msg2 = "Example: \n\tcommand \"%s foo[00-02] bar\"\n" % (sys.argv[0])
        msg3 = "will try to request nodes 'foo00', 'foo01', 'foo02', and 'bar'"
        print msg1
        print msg2
        print msg3
        return 

    def main(self, argv):
        args = argv[1:]

        if  len(args)==0          or \
                args == ['-h']    or \
                args == ['-help'] or \
                args == ['--help']:
            return self.show_help()
    
        nodes = self.get_nodes(args)
        for node in nodes:
            self.request_node(node)
        return

if __name__ == "__main__":
    sys.exit(cnreq().main(sys.argv))
