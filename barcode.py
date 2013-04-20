#!/usr/bin/env python
from os import sys
import getpass

import unsw_ldap

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
        seen = set(f)
except IOError:
    seen = set()

# Readloop
while (1):
    barcode = sys.stdin.readline()
    sn = get_student_number(barcode)
    print 'Student Number:', sn
    if barcode not in seen:
        seen.add(barcode)
        with open(sys.argv[1], 'a') as f:
            f.write(barcode)
        try:
            print ldap.get_user(sn)
        except:
            print 'Error retrieving LDAP data'

    else:
        print '#' * 80
        print
        print 'Double Scan'
        print
        print '#' * 80

