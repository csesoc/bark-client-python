#!/usr/bin/env python
import getpass
from Queue import Queue
import sys

from reader import ThreadedUSBSerialReader
import unsw_ldap
from bark_api_client import BarkAPIClient

if __name__ == '__main__':

    if len(sys.argc) < 2:
        print 'No swipe file provided. Exiting'
        sys.exit()

    print 'Bark API Login'
    username = raw_input('Username: ')
    password = getpass.getpass()
    bark_client = BarkAPIClient(username, password)

    events = bark_client.get_events()
    print 'Select Event:'
    for x in range(len(events)):
        print str(x) + ': ' + events[x]['name']

    event_number = int(raw_input())
    event_id = events[event_number]['id']
    bark_client.set_event(event_id)
    print 'Selected: ' + events[event_number]['name']

    filehandle = open(sys.argv[1], 'r')
    swipes = pickle.load(filehandle)

    for swipe in swipes:
        bark_client.upload_swipe(swipe['card_uid', swipe['timestamp'])

    print 'Done'
