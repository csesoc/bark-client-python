"""
Implements the core of Bark client.
"""

import os

from .lib import SafeWriter, pack_swipe

class BarkClient(object):
    def __init__(self):
        self.conf_dir_ = os.path.expanduser('~/.bark-client/dev')

        self.persistent_store_file_ = self.conf_dir_ + '/swipes'

        # Ensure we create configuration directories.
        try:
            os.makedirs(self.conf_dir_)
        except OSError:
            pass

    def save_persistent_(self, data):
        data = str(data)

        writer = SafeWriter(self.persistent_store_file_)
        writer.write(data)

    def register_swipe(self, **kwargs):
        """
        Saves a single swipe into the client's internal persistent storage.

        Accepts kwargs of 'event_description' and 'swipe_data', both strings.
        """

        packed = pack_swipe(**kwargs)
        self.save_persistent_(packed)

    def upload(self):
        raise Exception('Not implemented')
