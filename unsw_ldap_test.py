#!/usr/bin/env python
"""
test_ldap.py

"""

import sys
import os
import getpass
import unsw_ldap

def main():
   print 'Enter your student id'
   student_id = sys.stdin.readline().strip()
   print 'Enter password'
   password = getpass.getpass()
   print 'Enter zid'
   zid = sys.stdin.readline().strip()
   l = unsw_ldap.UnswLdapClient(student_id, password)
   print l.get_user(zid)
   print 'Enter a barcode'
   barcode = sys.stdin.readline().strip()
   print l.get_user_by_barcode(barcode)

if __name__ == '__main__':
   main()
