#! /usr/bin/env python
#
''' 

'''
import sys
import cntools

def show_help():
#    msg  = "Usage: {0} ssh <openssh_arguments>\n".format(sys.argv[0])
    msg  = "Usage: %s ssh <openssh_arguments>\n" % (sys.argv[0])
    msg += "For more information on <openssh_arguments>, please refer to 'ssh -h'"
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

    return cntools.cnssh(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
