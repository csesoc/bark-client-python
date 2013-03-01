#!/usr/bin/env python
"""
test_ldap.py

"""

import sys
import os
import getpass
from unsw_ldap import LdapLookup

def main():
   print 'Enter your student id'
   student_id = sys.stdin.readline().strip()
   print 'Enter password'
   password = getpass.getpass()
   print 'Enter zid'
   zid = sys.stdin.readline().strip()
   l = LdapLookup(student_id, password)
   print l.get_user(zid)

if __name__ == '__main__':
   main()
