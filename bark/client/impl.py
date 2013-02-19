"""
Implements the core of Bark client.
"""

import getpass, os

from .lib import SafeWriter, pack_swipe
from .lib import BarkApiClient

class BarkClient(object):
    def __init__(self):
        self.conf_dir_ = os.path.expanduser('~/.bark-client/dev')

        self.auth_key_file_ = self.conf_dir_ + '/auth_token'
        self.persistent_store_file_ = self.conf_dir_ + '/swipes'

        self.api = BarkApiClient()

        # Ensure we create configuration directories.
        try:
            os.makedirs(self.conf_dir_)
        except OSError:
            pass

    def save_persistent_(self, data):
        data = str(data)

        writer = SafeWriter(self.persistent_store_file_)
        writer.write(data)

    def get_auth_token_from_file_(self):
        """
        Reads auth_token from locally saved file.
        Returns keystring on success and None on failure.
        """

        key = None
        try:
            key = open(self.auth_key_file_, 'r').read().strip()
        except:
            pass
        return key

    def get_auth_token_from_bark_api_(self, username, password, save=True):
        """
        Connects to the Bark API server and attempts to authenticate.
        Will throw bark.client.lib.BarkApiException if authentication fails.

        If save == True, saves teh token to local file upon success.
        """

        auth_token = self.api.authenticate(username, password)

        if save:
            open(self.auth_key_file_, 'w').write(auth_token)

        return auth_token

    def get_auth_token_(self):
        # Try local file.
        auth_token = self.get_auth_token_from_file_()

        # If failed, try authentication.
        if auth_token is None:
            username = raw_input('Username: ').strip()
            password = getpass.getpass('Password: ')

            auth_token = self.get_auth_token_from_bark_api_(username, password)

        return auth_token

    def register_swipe(self, **kwargs):
        """
        Saves a single swipe into the client's internal persistent storage.

        Accepts kwargs of 'event_description' and 'swipe_data', both strings.
        """

        packed = pack_swipe(**kwargs)
        self.save_persistent_(packed)

    def upload(self):
        raise Exception('Not implemented')
