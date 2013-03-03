#!/usr/bin/env python
import serial
import os.path
import sys
import time
import threading
import datetime

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

    def __init__(self, verbose=False):
        try:
            self.conn = get_connection(verbose=verbose)
        except serial.SerialException:
            if verbose:
                print >> sys.stderr, 'No USB Serial devices found'
            raise serial.SerialException

    def read(self, timeout=None):
        """Read a UID from the serial device, blocking until success or timeout"""
        start_time = time.time()
        while timeout == None or time.time() - start_time < timeout:
            line = self.conn.readline().strip()
            if NULL_READ not in line and LEADING_DATA in line and line != self.last_uid:
                self.last_uid = line
                break
        return line[len(LEADING_DATA):]

class ThreadedUSBSerialReader(threading.Thread):
    stop_scheduled = threading.Event()

    def __init__(self, queue, verbose=False):
        threading.Thread.__init__(self)
        self.reader = USBSerialReader(verbose)
        self.queue = queue
        self.verbose = verbose

    def run(self):
        self.stop_scheduled.clear()
        if self.verbose:
            print >> sys.stderr, 'Threaded reader started'
        while not self.stop_scheduled.is_set():
            card_uid = self.reader.read(timeout=1)
            if card_uid:
                self.queue.put((card_uid, datetime.datetime.now()),)
        if self.verbose:
            print >> sys.stderr, 'Thread reader stopped'

    def stop(self):
        self.stop_scheduled.set()

if __name__ == '__main__':
    r = None
    try:
        r = USBSerialReader()
        print r.read()
    except serial.SerialException:
        print >> sys.stderr, 'No USB Serial devices found'
