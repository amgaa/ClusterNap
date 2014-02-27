#! /usr/bin/env python
#
''' 

'''
import sys
import cntools

def show_help():
#    msg  = "Usage: {0} <qsub_arguments>\n".format(sys.argv[0])
    msg  = "Usage: %s <qsub_arguments>\n" % (sys.argv[0])
    msg += "For more information on <qsub_arguments>, please refer to 'qsub -h'"
    print msg


def main(argv, stdin):

    args = argv[1:]
    if len(args) == 0 and stdin.isatty(): #stdin.isatty() returns "false" if there is no data 
        show_help()
        exit(1)

    if      ['-h']     in args or\
            ['--help'] in args or\
            ['-help']  in args:
        return show_help()

    if len(args) == 1 and \
            args in [['-h'], ['--help'], ['-help']]:
        return show_help()

    return cntools.cnqsub(args, stdin)


if __name__ == "__main__":
    sys.exit(main(sys.argv, sys.stdin))
