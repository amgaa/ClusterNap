#!/usr/bin/env python

import os, sys, re, pwd, datetime, grp
import itertools
import get_state
import get_conf
import cninfo
import logset

class cnrel:
    def __init__(self):
        self.log          = logset.get("cnrel", "event.log")
        self.errorlog     = logset.get("cnrelerr", "error.log")
        self.REQUEST_DIR  = os.path.dirname(os.path.abspath(__file__))
        self.REQUEST_DIR += "/../requested/nodes/"
        self.USER         = pwd.getpwuid(os.getuid())[0]
#        self.INFO         = cninfo.cninfo().INFO.copy()
#        self.INFO_LIST    = cninfo.cninfo().INFO_LIST[:]

#        self.INFO         = cninfo.cninfo().get_info()
#        self.INFO_LIST    = cninfo.cninfo().get_info_list()
        
    def release_all(self):
        INFO = cninfo.cninfo().get_info()
        for node in INFO.keys():
            if INFO[node][2] == self.USER:
                self.release_node(node)
        return

    def release_node(self, node):
        INFO = cninfo.cninfo().get_info()

        # If node is not defined in ClusterNap, say so. return
        if not INFO.has_key(node):
#            msg = "'{0}': Cannot release. Not defined in ClusterNap".format(node)
            msg = "'%s': Cannot release. Not defined in ClusterNap" % (node)
            print msg
            self.log.warning(self.USER + ": " + msg)
            return 1
        
        # If not requested, say so request
        if INFO[node][1] == "Free":
#            msg = "'{0}': Cannot release. Already released".format(node)
            msg = "'%s': Cannot release. Already released" % (node)
            print msg
            self.log.warning(self.USER + ": " + msg)
            return 0

        # If the user is "root", do whatever he pleases!
        if self.USER == "root":
            os.remove(self.REQUEST_DIR + node)
            if os.path.exists(self.REQUEST_DIR + node):
#                msg = "'{0}': Unexpected error!".format(node)
                msg = "'%s': Unexpected error!" % (node)
                print msg
                self.errorlog.error(self.USER + ": " + msg)
#                exit(1)
                return 1

#            msg = "'{0}': released!".format(node)
            msg = "'%s': released!" % (node)
            print msg
            self.log.info(self.USER + ": " + msg)
            return 0
 
        # If requested
        if INFO[node][1] == "Requested":
            # if requested by the user itself, release
            if self.USER == INFO[node][2]:
                os.remove(self.REQUEST_DIR + node)
                if os.path.exists(self.REQUEST_DIR + node):
#                    msg = "'{0}': Unexpected error!".format(node)
                    msg = "'%s': Unexpected error!" % (node)
                    print msg
                    self.errorlog.error(self.USER + ": " + msg)
#                    exit(1)
                    return 1

#                msg = "'{0}': released".format(node)
                msg = "'%s': released" % (node)
                print msg
                self.log.info(self.USER + ": " + msg)
                return 0

            # Someone else requested
#            msg = "'{0}': Cannot release. Someone else requested".format(node)
            msg = "'%s': Cannot release. Someone else requested" % (node)
            print msg
            self.log.warn(self.USER + ": " + msg)
            return 1


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
#        msg1 = "Usage: {0} release <nodes to release>\n".format(sys.argv[0])
        msg1 = "Usage: %s release <nodes to release>\n" % (sys.argv[0])
#        msg2 = "Example: \n\tcommand \"{0} foo[00-02] bar\"\n".format(sys.argv[0])
        msg2 = "Example: \n\tcommand \"%s foo[00-02] bar\"\n" % (sys.argv[0])
        msg3 = "will try to release nodes 'foo00', 'foo01', 'foo02', and 'bar'"
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
        if args == ['-a'] or args == ['--all'] or args == ['-all']:
            return self.release_all()

        nodes = self.get_nodes(args)
        for node in nodes:
            self.release_node(node)
        return

if __name__ == "__main__":
    sys.exit(cnrel().main(sys.argv))
