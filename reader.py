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

class USBSerialReader:
    s = None
    last_uid = ''

    def __init__(self):
        port_attempts = [SERIAL_PORT_BASE + str(x) for x in xrange(MAX_PORT_ATTEMPTS)]
        for port in port_attempts:
            if os.path.exists(port):
                try:
                    self.s = serial.Serial(port, BAUD_RATE, timeout=TIMEOUT)
                    break
                except serial.SerialException:
                    print >> sys.stderr, port + ' exists but is not readable'
                    print >> sys.stderr, 'Try chmod o+r ' + port
                    print >> sys.stderr, 'Ensure current user is in the \'dialout\' group'
                    continue

        if not self.s:
            print >> sys.stderr, "No USB Serial devices found"
            sys.exit()

    def read(self, timeout=10):
        """Read a UID from the serial device, blocking until success"""
        start_time = time.time()
        while (time.time() - start_time < timeout):
            line = self.s.readline().strip()
            if NULL_READ not in line and LEADING_DATA in line and line != self.last_uid:
                self.last_uid = line
                break
        return line[len(LEADING_DATA):]

if __name__ == "__main__":
    r = USBSerialReader()
    print r.read()
