#!/usr/bin/env python

import os

if not os.system("/usr/bin/ssh hongo-charlie") == 0:
    print "hello"
else:
    print "Finished"
