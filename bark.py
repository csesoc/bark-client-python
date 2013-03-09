#!/usr/bin/env python
import getpass
from Queue import Queue
import sys

from reader import ThreadedUSBSerialReader
import unsw_ldap
from bark_api_client import BarkAPIClient

class BadCardError(Exception):
    pass

def get_student_info(ldap_client):
    student_number = raw_input('Student Number: ')
    try:
        user = ldap_client.get_user(student_number)
        print user['display_name']
        print user['school']
        print user['faculty']
        return student_number
    except unsw_ldap.LDAPError:
        print 'Error retreiving LDAP Data'
        return student_number
    except unsw_ldap.UserNotFoundError:
        print 'Student not found'
        return None

def get_student_number(ldap_client):
    student_number = get_student_info(ldap_client)
    if not student_number:
        retry = raw_input('Retry fetching data? (Y/n): ')
        if retry == '' or retry == 'Y' or retry == 'y':
            student_number = get_student_info(ldap_client)
    return student_number

def handle_unknown_card(ldap_client, bark_client, card_uid):
    student_number = get_student_number(ldap_client)
    if student_number:
        add = raw_input('Add to Bark group? (Y/n):')
        if add == 'Y' or add == 'y' or add == '':
            bark_client.create_identity(card_uid, student_number)
            print 'User added.'
        else:
            print 'User not added. Swipe skipped'
            raise BadCardError
    else:
        print 'No student number provided. Anonymous Swipe saved'

def handle_swipe(ldap_client, bark_client, card_uid, timestamp):
    if not bark_client.is_known(card_uid):
        print ' - Unknown Card'
        try:
            handle_unknown_card(ldap_client, bark_client, card_uid)
        except BadCardError:
            print 'Bad card. Swipe not saved'
            return
    else:
        print ' - OK'
        
    bark_client.register_swipe(card_uid, timestamp)

def swipe_loop(card_queue, ldap_client, bark_client):
    while True:
        print "Listening for cards..."

        while card_queue.empty():
            pass

        if not card_queue.empty():
            card_uid, timestamp = card_queue.get()
            print card_uid,
            handle_swipe(ldap_client, bark_client, card_uid, timestamp)

        # Add delayed uploading here

if __name__ == '__main__':
    print 'Connecting to serial reader...',
    try:
        card_queue = Queue() 
        reader = ThreadedUSBSerialReader(card_queue, verbose=True)
        print 'connected'
    except:
        print 'Error connecting to serial reader. Exiting.'
        sys.exit()

    print 'Bark API Login'
    username = raw_input('Username: ')
    password = getpass.getpass()
    bark_client = BarkAPIClient(username, password)

    print "UNSW LDAP Login (Zid + Zpass). Don't get this wrong..."
    zid = raw_input('Zid: ')
    zpass = getpass.getpass()
    ldap_client = unsw_ldap.UnswLdapClient(zid, zpass)

    events = bark_client.get_events()
    print 'Select Event:'
    for x in range(len(events)):
        print str(x) + ': ' + events[x]['name']

    event_number = int(raw_input())
    event_id = events[event_number]['id']
    bark_client.set_event(event_id)
    print 'Selected: ' + events[event_number]['name']

    try:
        reader.start()
        swipe_loop(card_queue, ldap_client, bark_client)

    except KeyboardInterrupt:
        reader.stop()
