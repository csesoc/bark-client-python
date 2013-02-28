#!/usr/bin/env python
import getpass
import bark_api as api
import sys
import datetime

from reader import USBSerialReader
from unsw_ldap import LdapLookup

ldap = LdapLookup()

def handle_swipe(reader, auth_token, device_id, event_id):
    swipe = reader.read()
    timestamp = datetime.datetime.now().isoformat()
    print swipe

    zid = raw_input("Cardholder Z-id:")
    print "Looking up details of " + zid
    user = ldap.get_user(zid)
    
    print user['displayName']
    print user['school']
    print user['faculty']

    enrol = raw_input("Add cardholder to society and upload swipe? [Y/N]")
    if enrol == 'Y':
        api.create_identity(auth_token, zid)
        api.post_swipe(auth_token, device_id, event_id, timestamp, swipe)    

print "Bark API Login"
username = raw_input("Username: ")
password = getpass.getpass()

print "UNSW LDAP Login (Zid + Zpass). Don't get this wrong..."
zid = raw_input("Zid: ")
zpass = getpass.getpass()

print "Connecting to serial reader"
reader = USBSerialReader()

auth_token = api.get_auth_token(username, password)

events = api.get_events(auth_token)
print 'Select Event:'
for x in range(len(events)):
    print str(x) + ': ' + events[x]['name']

event_number = int(raw_input())
event_id = events[event_number]['id']
print 'Event Id:', event_id

device_id = api.register_device(auth_token, event_id)
print 'Device Id:', device_id

while(True):
    act = raw_input('(s)wipe, (q)uit?')
    
    if act == 'q':
        break;

    elif act == 's':
        handle_swipe(reader, auth_token, device_id, event_id)
