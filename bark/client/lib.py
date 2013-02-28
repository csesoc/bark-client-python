"""
Various useful things for nicer coding.
"""

import os, fcntl
import struct
import json, requests
from datetime import datetime

SWIPE_FMT_ = '< 64s 64s'

def pack_swipe(event_description=None, swipe_data=None):
    return struct.pack(SWIPE_FMT_, event_description, swipe_data)

def unpack_swipes_from_file(fd):
    """
    Generator of swipes from a given file descriptor.

    Requires `fd' to be locked or otherwise guaranteed to be untruncated as
    this generator is iterated.
    """

    record_size = struct.calcsize(SWIPE_FMT_)
    total_size = os.fstat(fd).st_size

    for _ in xrange(total_size / record_size):
        buf = os.read(fd, record_size)
        unpacked = struct.unpack(SWIPE_FMT_, buf)
        yield dict(zip(
            ['event_description', 'swipe_data'],
            map(
                lambda s: s.strip('\0'), # Silly unpack() pads string with '\0'.
                unpacked)))

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
    device_id = None

    def post_(self, url, **kwargs):
        r = requests.post(
            self.bark_url_ + url,
            data=json.dumps(kwargs),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            })
        return r.json()

    def auth_post_(self, url, **kwargs): 
        r = requests.post(
            self.bark_url_ + url,
            data=json.dumps(kwargs),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'auth_token': self.auth_token_,
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

    def set_device_id(self, device_id):
        self.device_id_ = device_id

    def register_device(self, event_id):
        response = self.auth_post_('/devices', event_id=event_id)

        if response['status'] != 'OK':
            error = 'Bark API call failed.\n' + json.dumps(response, indent=2)
            raise BarkApiException(error)

        return response['id']

    def send_single_swipe(self, swipe):
        assert isinstance(swipe, dict)
        assert self.auth_token_ is not None, 'Set my auth_token first!'
        assert self.device_id_ is not None, 'Need to get a device ID for the event'

        data = {
            'device': self.device_id_,
            'timestamp': str(datetime.now()),
            'uid': swipe['swipe_data'],
        }

        response = self.auth_post_('/swipe', **data)
        if response['status'] != 'OK':
            error = 'Bark API call failed.\n' + json.dumps(response, indent=2)
            raise BarkApiException(error)
