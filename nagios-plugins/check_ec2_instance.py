#! /usr/bin/env python

import sys
import os
import boto.ec2

def show_help():
    print "Usage:\t%s [REGION] [AWS_ACCESS_KEY] [AWS_SECRET_KEY] [INSTANCE_ID]" % sys.argv[0]
    print ""
    print "Example:\n\t%s us-west-w AKKLJYRTOB3M7YXBGBKA 6U+ojbLok2wQAMkZM0Z8ajE0axfNLYmj54aZg7Df i-8a7680de" % sys.argv[0]
    sys.exit(-1)


if len(sys.argv) != 5:
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

conn = boto.ec2.connect_to_region(REGION,
                                  aws_access_key_id = ACCESS,
                                  aws_secret_access_key = SECRET)

if not conn:
    print "UNKNOWN: Failed to connect to region %s with given ACCESS and SECRET KEY: " % REGION
    sys.exit(3)

try: 
    ret = conn.get_all_reservations(INS_ID)[0].instances[0].state_code 
    if ret == 16: #running
        print "OK: Running"
        sys.exit(0)
    if ret in [48, 80]:
        print "CRITICAL: one of (terminated, stopped)"
        sys.exit(2)
    if ret in [0, 32, 64]:
        print "UNKNOWN: one of (pending, shutting-down, stopping)"
        sys.exit(3)
except boto.exception.EC2ResponseError as ex:
    print "UNKNOWN: Failed to get information of instance \"%s\" with given ACCESS and SECRET KEY" % INS_ID
    template = "An exception of type {0} occured. Arguments:\n{1!r}"
    message = template.format(type(ex).__name__, ex.args)
    print message
    sys.exit(3)

print "UNKNOWN: Unexpected error: " + str(ret)
sys.exit(3)
