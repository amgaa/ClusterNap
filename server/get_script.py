#! /usr/bin/python
# -*- coding: utf-8 -*-

''' 
This program gets the configurations of nodes from corresponding files.

Returns a hash table of nodes {node_name: {'host':  "client-host" , 
                                           'path':  "'path/to/script'", 
                                           'user':  "user" 
                                           }}
'''

import sys, os, re
import itertools
import time

class get_script:

    def __init__(self):
        self.CONFDIR           = os.path.dirname(os.path.abspath(__file__))
        self.CONFDIR          += "/config/"
        self.SCRIPTDIR         = self.CONFDIR + "scripts/"
        self.PHYS_SCRIPT       = self.SCRIPTDIR + "physical/"
        self.SERV_SCRIPT       = self.SCRIPTDIR + "service/"

        self.PHYS_SCRIPT_ON    = self.PHYS_SCRIPT + "on/"
        self.PHYS_SCRIPT_OFF   = self.PHYS_SCRIPT + "off/"
        self.PHYS_SCRIPT_STATE = self.PHYS_SCRIPT + "state/"

        self.SERV_SCRIPT_ON    = self.SERV_SCRIPT + "on/"
        self.SERV_SCRIPT_OFF   = self.SERV_SCRIPT + "off/"
        self.SERV_SCRIPT_STATE = self.SERV_SCRIPT + "state/"

        self.PHYS_SCRIPTS_ON    = list()
        self.PHYS_SCRIPTS_OFF   = list()
        self.PHYS_SCRIPTS_STATE = list()

        self.SERV_SCRIPTS_ON    = list()
        self.SERV_SCRIPTS_OFF   = list()
        self.SERV_SCRIPTS_STATE = list()

        self.PHYS_SCRIPTS_ON    = os.listdir( self.PHYS_SCRIPT_ON    )
        self.PHYS_SCRIPTS_OFF   = os.listdir( self.PHYS_SCRIPT_OFF   )
        self.PHYS_SCRIPTS_STATE = os.listdir( self.PHYS_SCRIPT_STATE )

        self.SERV_SCRIPTS_ON    = os.listdir( self.SERV_SCRIPT_ON    )
        self.SERV_SCRIPTS_OFF   = os.listdir( self.SERV_SCRIPT_OFF   )
        self.SERV_SCRIPTS_STATE = os.listdir( self.SERV_SCRIPT_STATE )

        self.PHYS_SCRIPTS_ON    = [item for item in self.PHYS_SCRIPTS_ON    if item[-3:] == '.on'] 
        self.PHYS_SCRIPTS_OFF   = [item for item in self.PHYS_SCRIPTS_OFF   if item[-4:] == '.off']
        self.PHYS_SCRIPTS_STATE = [item for item in self.PHYS_SCRIPTS_STATE if item[-6:] == '.state']

        self.SERV_SCRIPTS_ON    = [item for item in self.SERV_SCRIPTS_ON    if item[-3:] == '.on']
        self.SERV_SCRIPTS_OFF   = [item for item in self.SERV_SCRIPTS_OFF   if item[-4:] == '.off']
        self.SERV_SCRIPTS_STATE = [item for item in self.SERV_SCRIPTS_STATE if item[-6:] == '.state']


    # Returns { node_name: {'host': "client-host", 'user':"user", 'path':"path"} }
    def get_phys_on(self):
        script = {}
        for conf_file in self.PHYS_SCRIPTS_ON:
            script.update( self.get_script( self.PHYS_SCRIPT_ON + conf_file) )
        return script

    def get_phys_off(self):
        script = {}
        for conf_file in self.PHYS_SCRIPTS_OFF:
            script.update( self.get_script( self.PHYS_SCRIPT_OFF + conf_file) )
        return script

    def get_phys_state(self):
        script = {}
        for conf_file in self.PHYS_SCRIPTS_STATE:
            script.update( self.get_script( self.PHYS_SCRIPT_STATE + conf_file) )
        return script

    def get_serv_on(self):
        script = {}
        for conf_file in self.SERV_SCRIPTS_ON:
            script.update( self.get_script( self.SERV_SCRIPT_ON + conf_file) )
        return script

    def get_serv_off(self):
        script = {}
        for conf_file in self.SERV_SCRIPTS_OFF:
            script.update( self.get_script( self.SERV_SCRIPT_OFF + conf_file) )
        return script

    def get_serv_state(self):
        script = {}
        for conf_file in self.SERV_SCRIPTS_STATE:
            script.update( self.get_script( self.SERV_SCRIPT_STATE + conf_file) )
        return script

    # Returns  hash table of: script[name] = {'host': "", 'user':"", 'path':""}
    def get_script(self, filepath):
        f = open(filepath, "r")
        script = {}
        name = ""

        for line in f:
            line = line.strip()

            # Ignore comment-outed or empty line
            if line[:1] == "" or line[:1] == "#": 
                continue

            head, body = line.split(":")
            head = head.strip()

            if head == "Name": 
                name = body.strip()
                script[name] = {'host': "", 'user':"", 'path':""}

            elif head == "Host/user/path":
                host, user, script_path = body.split(",")
                if script.has_key(name):
                    script[name]['host']        = host.strip()
                    script[name]['user']        = user.strip()
                    script[name]['path'] = script_path.strip()
                else:
                    print "Script host name error: " + name

        return script
        
    def main(self, argv):
        print self.get_phys_on()
        print self.get_phys_off()
        print self.get_phys_state()
        print self.get_serv_on()
        print self.get_serv_off()
        print self.get_serv_state()
        return
    
if __name__ == "__main__":
    sys.exit(get_script().main(sys.argv))
