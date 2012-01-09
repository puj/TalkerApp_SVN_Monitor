#!/usr/bin/python

import pysvn
import urllib2
import time, ConfigParser as cfg

def sendMessage(author,time, revision, message):
    
    # Create the message
    my_str = talker_format_string.replace('%r',revision).replace('%a',author).replace('%m',message)
    
    print "Sending message " + my_str + " to " + talker_room_url
    
    # JSONifiy -- probably a lib for this in python, unecessary?
    JSONdata = '{"message":"' + str(my_str) + '"}'
    
    # Setup Request headers
    headers = {'Connection': 'Keep-Alive', 'Accept-Encoding' : 'application/json' , 'Accept' : 'application/json',  'Content-Type' : 'application/json' , 'X-Talker-Token' : talker_token}
    
    # Create request
    req = urllib2.Request(talker_room_url, "", headers)
    req.add_data(JSONdata)
    req.header_items()
    
    # Send request, ignore response
    response = urllib2.urlopen(req)


def getConfig():
    # Read config and setup global variables
    global  svn_root, svn_user, svn_pass, svn_poll_interval, \
            talker_room_url, talker_format_string, talker_token

    # Enforcing config file format and name
    config_file = 'svnMonitorTalkerApp.cfg'
    config_svn = 'svn'
    config_talker = 'talker'

    try:
        parser = cfg.ConfigParser()
        parser.read(config_file)
        
        # Get the SVN options
        svn_root = parser.get(config_svn, 'server')
        svn_user = parser.get(config_svn, 'user')
        svn_pass = parser.get(config_svn, 'pass')
        svn_poll_interval = parser.get(config_svn, 'pollInterval')
        
        #Get the Talker App options
        talker_room_url = parser.get(config_talker, 'roomUrl');
        talker_format_string = parser.get(config_talker, 'formatString');
        talker_token = parser.get(config_talker, 'talkerToken');
        
    except BaseException as e:
        print "Error parsing config file '%s':" % config_file        
        exit()

def getCredentials(realm, username, may_save):
    # Credentials callback for SVN
    return True, svn_user, svn_pass, False


latestRevisionNumber = 0
def discover_changes():
    global latestRevisionNumber
    
    
    # Should this connection remain open between polls? Can it?
    client = pysvn.Client()
    client.callback_get_login = getCredentials
    
    # Find the last change to the repository
    log = client.log(
        svn_root, 
        discover_changed_paths=True,
        limit=1
        )

    # Should only have 1 entry in log 
    for entry in log:
        # We have a new revision
        if(latestRevisionNumber != entry.revision.number):
            latestRevisionNumber = entry.revision.number
            sendMessage(str(entry.author),str(entry.date), str(entry.revision.number),str(entry.message))

if __name__ == '__main__':
    getConfig()
    print 'Monitoring SVN repository: %s' % svn_root
    
    while True:
        print 'Polling %s ...' % svn_root
        discover_changes()
        time.sleep(float(svn_poll_interval))