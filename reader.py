#!/usr/bin/env python
import serial
import os.path
import sys
import time

SERIAL_PORT_BASE = '/dev/ttyUSB' 
MAX_PORT_ATTEMPTS = 8
BAUD_RATE = 112500
TIMEOUT = 3

NULL_READ = '---'
LEADING_DATA = 'UID: '

def get_connection(verbose=False):
    conn = None
    port_attempts = [SERIAL_PORT_BASE + str(x) for x in xrange(MAX_PORT_ATTEMPTS)]
    for port in port_attempts:
        if os.path.exists(port):
            try:
                conn = serial.Serial(port, BAUD_RATE, timeout=TIMEOUT)
                break
            except serial.SerialException:
                if verbose:
                    print >> sys.stderr, port + ' exists but is not readable'
                    print >> sys.stderr, 'Try chmod o+r ' + port
                    print >> sys.stderr, 'Ensure current user is in the \'dialout\' group'
                continue
    if not conn:
        raise serial.SerialException
    return conn

class USBSerialReader:
    conn = None
    last_uid = ''

    def __init__(self):
        try:
            self.conn = get_connection(verbose=True)
        except serial.SerialException:
            print >> sys.stderr, "No USB Serial devices found"
            sys.exit()

    def read(self, timeout=None):
        """Read a UID from the serial device, blocking until success or timeout"""
        start_time = time.time()
        while (timeout == None or time.time() - start_time < timeout):
            line = self.conn.readline().strip()
            if NULL_READ not in line and LEADING_DATA in line and line != self.last_uid:
                self.last_uid = line
                break
        return self.last_uid[len(LEADING_DATA):]

if __name__ == "__main__":
    r = USBSerialReader()
    print r.read()
