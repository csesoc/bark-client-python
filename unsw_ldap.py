import ldap

class LdapLookup():

    def __init__(self, zid, zpass):
        self.user_zid = zid
        self.user_zpass = zpass

    def get_user(self, zid):
        try:
            l = ldap.open("ad.unsw.edu.au")
            l.protocol_version = ldap.VERSION3

            upn = self.user_zid + '@ad.unsw.edu.au'

            l.bind_s(upn, self.user_zpass)

            baseDN = "OU=IDM_People,OU=IDM,DC=ad,DC=unsw,DC=edu,DC=au"
            searchScope = ldap.SCOPE_SUBTREE
            retrieveAttributes = ['cn', 'displayNamePrintable', 'givenName', 'sn', 'mail','extensionAttribute10','extensionAttribute11', 'displayName']
            searchFilter = "cn=" + zid

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
            print e
            return None
