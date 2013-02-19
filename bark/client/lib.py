"""
Various useful things for nicer coding.
"""

import os, fcntl
import struct
import json, requests
from datetime import datetime

def pack_swipe(event_description=None, swipe_data=None):
    return struct.pack('< 64s 64s', event_description, swipe_data)

class LockedFile(object):
    """
    Provides an interface for gaining exclusive lock on a file. May block.

    Use like so:

        with LockedFile(filename, flags, mode) as fd:
            ... # operate on `fd'

    Params flags and mode are optional.
    """

    def __init__(
            self,
            filename,
            flags=os.O_APPEND | os.O_CREAT | os.O_WRONLY,
            mode=0600):
        self.filename_ = filename
        self.flags_ = flags
        self.mode_ = mode

    def __enter__(self):
        # Open...
        self.fd_ = os.open(
            self.filename_,
            self.flags_,
            self.mode_)

        # ...and lock.
        fcntl.flock(self.fd_, fcntl.LOCK_EX)

        return self.fd_

    def __exit__(self, *args, **kwargs):
        # Unlock and close.
        fcntl.flock(self.fd_, fcntl.LOCK_UN)
        os.close(self.fd_)

class SafeWriter(object):
    """
    Atomic file writer. Should never corrupt data.
    It will create and append to an existing file.
    """

    def __init__(self, filename):
        self.filename_ = filename

    def write(self, data):
        with LockedFile(self.filename_) as fd:
            old_size = os.fstat(fd).st_size

            try:
                nbytes = os.write(fd, data)

                # Just in case.
                assert nbytes == len(data), 'write() did not write all bytes'
            except Exception, e:
                print 'Could not write out data, corruption imminent. '\
                    'Old filesize=%r' % old_size
                raise e

class BarkApiException(Exception):
    pass

class BarkApiClient(object):
    bark_url_ = 'http://localhost:5000'
    auth_token_ = None

    def post_(self, url, **kwargs):
        r = requests.post(
            self.bark_url_ + url,
            data=json.dumps(kwargs),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            })
        return r.json()

    def set_auth_token(self, auth_token):
        self.auth_token_ = auth_token

    def authenticate(self, username, password):
        response = self.post_('/login', username=username, password=password)

        if response['status'] != 'OK':
            error = 'Bark API call failed.\n' + json.dumps(response, indent=2)
            raise BarkApiException(error)

        return response['auth_token']

    def send_single_swipe(self, swipe):
        assert isinstance(swipe, dict)
        assert self.auth_token_ is not None, 'Set my auth_token first!'

        data = {
            'auth_token': self.auth_token_,
            'device': 'bark.client.lib.BarkApiClient test client',
            'timestamp': str(datetime.now()),
            'event_description': swipe['event_description'],
            'uid': swipe['swipe_data'],
        }

        response = self.post_('/swipe/', **data)
        if response['status'] != 'OK':
            error = 'Bark API call failed.\n' + json.dumps(response, indent=2)
            raise BarkApiException(error)
