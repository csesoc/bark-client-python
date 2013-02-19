"""
Various useful things for nicer coding.
"""

import os, fcntl
import struct

def pack_swipe(event_description=None, swipe_data=None):
    return struct.pack('< 64s 64s', event_description, swipe_data)

class SafeWriter(object):
    """
    Atomic file writer. Should never corrupt data.
    It will create and append to an existing file.
    """

    def __init__(self, filename):
        self.filename_ = filename

        try:
            os.makedirs(os.path.dirname(filename))
        except OSError:
            pass

    def write(self, data):
        # Open the file and obtain exclusive lock on it.
        # May block.
        fd = os.open(
            self.filename_,
            os.O_APPEND | os.O_CREAT | os.O_WRONLY,
            0600)
        fcntl.flock(fd, fcntl.LOCK_EX)
        old_size = os.fstat(fd).st_size

        try:
            nbytes = os.write(fd, data)

            # Just in case.
            assert nbytes == len(data), 'write() did not write all bytes'
        except Exception, e:
            print 'Could not write out data, corruption imminent. '\
                'Old filesize=%r' % old_size
            raise e
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
