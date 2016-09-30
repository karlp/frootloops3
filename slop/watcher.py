from __future__ import division

import logging
import multiprocessing
import time


class WatcherProcess(multiprocessing.Process):
    """
    collects data on a port, overcoming buffering limits with a single read(bignumber) call
    gets told on it's process input what data it's meant to be looking for...
    """
    def __init__(self, port, conn):
        multiprocessing.Process.__init__(self)
        self.l = logging.getLogger(__name__)
        self.conn = conn
        self.port = port
        self.alive = multiprocessing.Event()
        self.alive.set()

    def run(self):
        expected = ""
        matching = 0
        while self.alive.is_set():
            if not self.conn.poll(0.5):
                #self.l.debug("waiting for more data....")
                print("waiting for more data")
                continue
            newd = self.conn.recv_bytes()
            expected += newd
            self.l.debug("Still watching for: %s", expected[matching:])
            #print("Still watching for: %s" % expected[matching:])
            while matching < len(expected):
                rdata = self.port.read()
                #print("rx port: %s, expecting: %s" % (rdata, expected[matching]))
                if rdata == expected[matching]:
                    matching += 1
                    # TODO - can we push a status here somehow, to get a "byets outstanding" count?
                else:
                    raise ValueError("data corruption")
            print("Received %d new bytes successfully, total: %d" % (len(newd), len(expected)))
            time.sleep(0.5)

    def join(self, timeout=None):
        print("joining and exiting...")
        self.alive.clear()
        multiprocessing.Process.join(self, timeout)



