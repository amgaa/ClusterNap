#! /usr/bin/env python
#
''' 

'''
import sys
import cntools

def show_help():
#    msg  = "Usage: {0} ssh <openssh_arguments>\n".format(sys.argv[0])
    msg  = "\nUsage: %s <nodename> <power_state>\n\n\n" % (sys.argv[0])
    msg += "This command changes a node's power state information \n"
    msg += "in ClusterNap into given state. Remember this command \n"
    msg += "DOES NOT literally changes (i.e., turns-on/off) a node's\n"
    msg += "REAL power state. Rather, it changes a node's state \n"
    msg += "information in ClusterNap.\n\n"
    msg += "For example:\n"
    msg += "                  %s nodeA on\n\n" %(sys.argv[0])
    msg += "will changes nodeA's state information in ClusterNap to \"ON\" \n"
    msg += "so that it will be seen as \"ON\" when you do \"cntools info\"\n"
    msg += "But it will not actually changes nodeA's real power state.\n"
    print msg


def main(argv):

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

    return cntools.setstate(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
