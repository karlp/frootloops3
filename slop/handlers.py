from __future__ import division

import threading
import select

def tsender(port, data):
    # FIXME - get the writer shit from frootloop2 maybe?
    print("starting tsender with port", port)
    tx_len = len(data)
    while tx_len > 0:
        n = port.write(data)
        tx_len -= n
        data = data[n:]
        #print("wrote ", n, "remainging: ", tx_len)

class DualSender():
    def __init__(self, dut, ref):
        dut.nonblocking()
        ref.nonblocking()
        self.dut = dut
        self.ref = ref

    def go(self, data):
        t1 = threading.Thread(target=tsender, args=(self.dut, data,))
        t2 = threading.Thread(target=tsender, args=(self.ref, data,))
        t1.start()
        t2.start()
        # grab the events from dut and ref and read them here.
        # FIXME be more pythonic (zip or somethign to make this shit?)
        inputs = [self.dut.fileno(), self.ref.fileno()]
        print("watching inputs: ", inputs)
        map = {}
        map[self.dut.fileno()] = {"port": self.dut, "rxb": "", "waiting": True}
        map[self.ref.fileno()] = {"port": self.ref, "rxb": "", "waiting": True}
        while any(map[q]["waiting"] for q in map.keys()):
            readable, writable, exceptional = select.select(inputs, [], inputs)
            for fd in readable:
                here = map[fd]
                newd = here["port"].read(here["port"].in_waiting)
                here["rxb"] += newd
                print("received ", len(newd), " on fd ", fd)
                if len(here["rxb"]) == len(data):
                    here["waiting"] = False
            for x in exceptional:
                raise RuntimeError("exceptional case on fd!")
        t1.join()
        t2.join()

        return {
            "dut": map[self.dut.fileno()]["rxb"],
            "ref": map[self.ref.fileno()]["rxb"]
        }




