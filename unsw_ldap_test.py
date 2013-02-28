#!/usr/bin/env python
"""
test_ldap.py

"""

import sys
import os
import getpass
from unsw_ldap import ldapLookup

def main():
   print 'Enter your student id'
   student_id = sys.stdin.readline().strip()
   print 'Enter password'
   password = getpass.getpass()
   print 'Enter zid'
   zid = sys.stdin.readline().strip()
   l = ldapLookup()
   print l.get_user(student_id,password,zid)

if __name__ == '__main__':
   main()
