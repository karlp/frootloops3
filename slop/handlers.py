from __future__ import division

import logging
import multiprocessing
import time


class Bidir(multiprocessing.Process):
    """
    Sends data on a port, and collects data on the port
    """
    def __init__(self, port, conn):
        multiprocessing.Process.__init__(self)
        self.port = port
        self.conn = conn

    def run(self):
        # this needs to be write to the serial port _and_ collect it's input, in a shared loop...
        # so, needs to chunk the
        pass