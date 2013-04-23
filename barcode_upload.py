import sys
import getpass
import iso8601

from bark_api_client import BarkAPIClient

if len(sys.argv) != 2:
    print "Usage: %s event_file" % sys.argv[0]
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

if raw_input ('Proceed with upload? (y/N): ') != 'y':
    sys.exit() 

with open(sys.argv[1], 'r') as f:
    for line in f:
        uid, isotime = line.strip().split('|')
        if not bark_client.is_known(uid):
            bark_client.create_identity(uid, 'z' + uid[2:9])
        bark_client.register_swipe(uid, iso8601.parse_date(isotime))
