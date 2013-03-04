import ldap
from ldap import LDAPError
import sys

LDAP_URL = 'ad.unsw.edu.au'
LDAP_USERNAME_EXT = '@ad.unsw.edu.au'
TIMEOUT = 5

def get_ldap_connection(zid, zpass):
    conn = ldap.open(LDAP_URL)
    conn.protocol_version = ldap.VERSION3
    conn.set_option(ldap.OPT_NETWORK_TIMEOUT, TIMEOUT)
    upn = self.user_zid + LDAP_USERNAME_EXT
    conn.bind_s(upn, self.user_zpass)
    return conn

class UnswLdapClient():
    conn = None

    def __init__(self, zid, zpass, verbose=False):
        self.user_zid = zid
        self.user_zpass = zpass

        try:
            self.conn = get_ldap_connection(zid, zpass)
        except (LDAPError, ldap.SERVER_DOWN), e:
            # We'll handle the problem when we come to it
            if verbose:
                print >> sys.stdout, 'Problem connecting to LDAP server'
            pass

    def get_user(self, zid):
        baseDN = "OU=IDM_People,OU=IDM,DC=ad,DC=unsw,DC=edu,DC=au"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ['cn', 'displayNamePrintable', 'givenName', 'sn', 'mail','extensionAttribute10','extensionAttribute11', 'displayName']
        searchFilter = "cn=" + zid

        try:

            ldap_result = l.search(baseDN, searchScope, searchFilter, retrieveAttributes)
            result_type, result_data = l.result(ldap_result, 0)

            user_dn,attr_results = result_data[0]

            details = {}
            details['givenName'] = attr_results['givenName'][0]
            details['lastname'] = attr_results['sn'][0]
            details['email'] = attr_results['mail'][0]
            details['faculty'] = attr_results['extensionAttribute10'][0]
            details['school'] = attr_results['extensionAttribute11'][0]
            details['displayName'] = attr_results['displayName'][0]

            return details

        except ldap.LDAPError, e:
            raise LDAPError

