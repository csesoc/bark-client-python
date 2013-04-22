#!/usr/bin/env python
from os import sys
import getpass
import datetime

import unsw_ldap

# Global flag for LDAP lookup on every scan
ldap_disabled = False

def get_student_number(barcode):
    return barcode[2:9]

if len(sys.argv) < 2:
    print "Usage %s student_number_file" % sys.argv[0]
    sys.exit()

# Do general setup, get an LDAP connection
print "UNSW LDAP Login"
zid = raw_input('Zid: ')
zpass = getpass.getpass()
ldap = unsw_ldap.UnswLdapClient(zid, zpass)

# Read currently seen users from file
try:
    with open(sys.argv[1]) as f:
        seen = set([x.split('|')[0] for x in f])
except IOError:
    seen = set()

print seen

# Readloop
running = True
while (running):
    try:
        print 'Listening for barcodes'
        while (1):
            barcode = sys.stdin.readline().strip()
            if barcode not in seen:
                seen.add(barcode)
                with open(sys.argv[1], 'a') as f:
                    f.write(barcode.strip() + '|' + datetime.datetime.now().isoformat() + '\n')
                if not ldap_disabled:
                    print 'Fetching LDAP record for barcode: ' + barcode
                    try:
                        print ldap.get_user_by_barcode(barcode)
                    except:
                        print 'Error retrieving LDAP data'
                        print 'LDAP Disabled (ctrl-c to re-enable)'
                        ldap_disabled = True

            else:
                print '#' * 10, "Multiple Scans!", '#' * 10
    except KeyboardInterrupt:
        print 'Listening paused'
        action = raw_input('re-enable (l)dap, (q)uit? All other input restarts: ')
        if action == 'l':
            ldap_disabled = False
        elif action == 'q':
            sys.exit()
