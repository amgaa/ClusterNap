#! /usr/bin/env python

import sys
import os
import boto.ec2

def show_help():
    print "Usage:\t%s [REGION] [AWS_ACCESS_KEY] [AWS_SECRET_KEY] [INSTANCE_ID] [0|1|ON|OFF|on|off]" % sys.argv[0]
    print ""
    print "Example:"
    print "To run stopped instance\n\t%s us-west-w AKKLJYRTOB3M7YXBGBKA 6U+ojbLok2wQAMkZM0Z8ajE0axfNLYmj54aZg7Df i-8a7680de 1" % sys.argv[0]
    print "To stop running instance\n\t%s us-west-w AKKLJYRTOB3M7YXBGBKA 6U+ojbLok2wQAMkZM0Z8ajE0axfNLYmj54aZg7Df i-8a7680de 0" % sys.argv[0]
    sys.exit(-1)

def start_instance(conn, INS_ID):
    try: 
        ids = list()
        ids.append(INS_ID)
        ret = conn.start_instances(instance_ids=ids)
        print "Start command is sent to instance \"%s\"" % INS_ID
        sys.exit(0)
    except boto.exception.EC2ResponseError as ex:
        print "Failed to sent start command to instance \"%s\"" % INS_ID
        template = "An exception of type {0} occured. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print message
        sys.exit(1)
    print "UNKNOWN: Unexpected error: " + str(ret)
    sys.exit(1)

def stop_instance(conn, INS_ID):
    try: 
        ids = list()
        ids.append(INS_ID)
        ret = conn.stop_instances(instance_ids=ids)
        print "Stop command is sent to instance \"%s\"" % INS_ID
        sys.exit(0)
    except boto.exception.EC2ResponseError as ex:
        print "Failed to sent stop command to instance \"%s\"" % INS_ID
        template = "An exception of type {0} occured. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print message
        sys.exit(1)
    print "UNKNOWN: Unexpected error: " + str(ret)
    sys.exit(1)

if len(sys.argv) != 6 or sys.argv[5] not in ['0', '1', 'ON', 'On', 'on', 'OFF', 'Off', 'off']:
    show_help()
    sys.exit(-1)

#REGION = "us-west-2"
#ACCESS = "AKIAJYRTOB3M7YXBGBKAZ"
#SECRET = "6U+ojbLok0qQAMkZM0Z8ajE0axfNLYmj54aZg7DfZ"
#INS_ID = "i-8a7550bez"

REGION = sys.argv[1]
ACCESS = sys.argv[2]
SECRET = sys.argv[3]
INS_ID = sys.argv[4]
ON_OFF = sys.argv[5]

conn = boto.ec2.connect_to_region(REGION,
                                  aws_access_key_id = ACCESS,
                                  aws_secret_access_key = SECRET)

if not conn:
    print "UNKNOWN: Failed to connect to region %s with given ACCESS and SECRET KEY: " % REGION
    sys.exit(3)

if ON_OFF in ['1', 'ON', 'On', 'on']:
    start_instance(conn, INS_ID)

if ON_OFF in ['0', 'OFF', 'Off', 'off']:
    stop_instance(conn, INS_ID)

print "Unexpected error!"
sys.exit(1)
