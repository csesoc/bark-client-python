import ldap
import sys

# Domain specific configuration
LDAP_URL = 'ad.unsw.edu.au'
LDAP_USERNAME_EXT = '@ad.unsw.edu.au'
BASE_DN = "OU=IDM_People,OU=IDM,DC=ad,DC=unsw,DC=edu,DC=au"

# General configuration
TIMEOUT = 5

def get_ldap_connection(zid, zpass):
    conn = ldap.open(LDAP_URL)
    conn.protocol_version = ldap.VERSION3
    conn.set_option(ldap.OPT_NETWORK_TIMEOUT, TIMEOUT)
    upn = zid + LDAP_USERNAME_EXT
    conn.bind_s(upn, zpass)
    return conn

def query_user(ldap_conn, zid):
    searchScope = ldap.SCOPE_SUBTREE
    retrieveAttributes = ['cn', 'displayNamePrintable', 'givenName', 'sn', 'mail','extensionAttribute10','extensionAttribute11', 'displayName']
    searchFilter = "cn=" + zid
    ldap_result = ldap_conn.search(BASE_DN, searchScope, searchFilter, retrieveAttributes)
    result_type, result_data = ldap_conn.result(ldap_result, 0)
    try:
        user_dn,attr_results = result_data[0]
        details = {}
        details['given_name'] = attr_results['givenName'][0]
        details['last_name'] = attr_results['sn'][0]
        details['email'] = attr_results['mail'][0]
        details['faculty'] = attr_results['extensionAttribute10'][0]
        details['school'] = attr_results['extensionAttribute11'][0]
        details['display_name'] = attr_results['displayName'][0]
    except (IndexError, KeyError):
        raise UserNotFoundError

    return details

def handle_ldap_error():
    if verbose:
        print >> sys.stdout, 'Problem connecting to LDAP server'

class LDAPError(Exception):
    pass

class UserNotFoundError(LDAPError):
    pass

class UnswLdapClient():
    conn = None

    def __init__(self, zid, zpass, verbose=False):
        self.user_zid = zid
        self.user_zpass = zpass

        try:
            self.conn = get_ldap_connection(zid, zpass)
        except (LDAPError, ldap.SERVER_DOWN), e:
            # We'll handle the problem when we come to it
            handle_ldap_error()
            pass

    def get_user(self, zid):
        result = None
        if self.conn is not None:
            try:
                result = query_user(self.conn, zid)
            except ldap.LDAPError:
                handle_ldap_error()
                result = None
         
        if result == None:
            try:
                self.conn = get_ldap_connection(self.user_zid, self.user_zpass)
                result = query_user(self.conn, zid)
            except ldap.LDAPError:
                handle_ldap_error()
                result = None

        if result == None:
            raise LDAPError

        return result
