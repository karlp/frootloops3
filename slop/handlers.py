from __future__ import division

import logging
import multiprocessing
import time
import threading


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

def tsender(port, data):
    # FIXME - get the writer shit from frootloop2 maybe?
    print("starting tsender with port", port)
    n = port.write(data)
    print("wrote " , n, "vs lendat of ", len(data))

class DualSender():
    def __init__(self, dut, ref):
        # dut.timeout = 0
        # dut.write_timeout = 0
        # ref.timeout = 0
        # ref.write_timeout = 0
        self.dut = dut
        self.ref = ref

    def go(self, data):
        t1 = threading.Thread(target=tsender, args=(self.dut, data,))
        t2 = threading.Thread(target=tsender, args=(self.ref, data,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()



