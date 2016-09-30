from __future__ import division
import unittest
import multiprocessing
import serial
import time

from slop.watcher import WatcherProcess
import slop.handlers

REF = "/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_red_pins-if00-port0"
#DUT = "/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_0670FF484849785087085514-if02"
DUT = "/dev/serial/by-id/usb-libopencm3_usb_to_serial_cdcacm_stm32f103-generic-if00"
BAUD = 115200

class Threaded(unittest.TestCase):
    def setUp(self):
        """eventually, we'll parameterise this... maybe... someday..."""
        self.ref = serial.Serial(REF, BAUD)
        self.dut = serial.Serial(DUT, BAUD)
        self.longMessage = True

    def tearDown(self):
        self.ref.close()
        self.dut.close()

    def testBulk_BIDIR(self):
        # ok, magically make two threads, have one slowly write all the data to one side, the other write from the other
        # and. I dunno, magically figure it out....
        data_send_ref = b"sending from the REF"
        data_send_dut = b"the dut merrily sends this"
        refMan = Bidir(self.ref, data_send_ref) # Could put sending model in here...
        dutMan = Bidir(self.dut, data_send_dut)

        # start two processes
        proc1 = refMan.time_limited(expected_rx_time_window)
        proc2 = dutMan.time_limited(expected_rx_time_window)

        proc1.join()
        proc2.join()

        # get data back out of refMan/dutMan to validate they got what they expected....

        # need to go read allll of the python multiprocessing again I think.



        lc, rc = multiprocessing.Pipe()
        pp = WatcherProcess(self.dut, rc)
        self.dut.flushInput()
        pp.start()

        data = b"The jetset silver robot hammered rapidly on the machinery.\n\r"*1000
        ll = len(data)
        lc.send_bytes(data)

        start = time.time()
        self.ref.write(data)
        total = time.time() - start
        print("Wrote %d bytes in %f seconds, ~bps = %f" % (ll, total, ll/total))
        print("Rough words per minute: %f" % (len(data.split()) / total *60))

        time.sleep(1) # Just needs to be long enough to let it run _at_all_  Can't I make the join() handle this properly?
        pp.join()


class Dual(unittest.TestCase):
    def setUp(self):
        """eventually, we'll parameterise this... maybe... someday..."""
        self.ref = serial.Serial(REF, BAUD)
        self.dut = serial.Serial(DUT, BAUD)
        self.longMessage = True


    def tearDown(self):
        self.ref.close()
        self.dut.close()

    def testSendNoCheck(self):
        dual = slop.handlers.DualSender(self.dut, self.ref)
        sample_data = b"sending messages in both directions is awesome"
        dual.go(sample_data)


class Bulk(unittest.TestCase):
    def setUp(self):
        """eventually, we'll parameterise this... maybe... someday..."""
        self.ref = serial.Serial(REF, BAUD)
        self.dut = serial.Serial(DUT, BAUD)
        self.longMessage = True

    def tearDown(self):
        self.ref.close()
        self.dut.close()

    def testRX(self):
        # At 1000, we run into outbound buffering problems!
        sample_data = b"the ref wrote some data for the dut to listen to" * 100
        self.ref.write(sample_data)
        t = len(sample_data) * 10 / BAUD
        print("Setting up to wait for %f" % t)
        self.dut.timeout = t * 1.5
        x = self.dut.read(len(sample_data))
        self.assertEquals(len(sample_data), len(x))
        self.assertEquals(x, sample_data)

    def testTX(self):
        sample_data = b"the dut wrote some data and we hope the ref got it" * 1000
        self.dut.write(sample_data)
        t = len(sample_data) * 10 / BAUD
        print("Setting up to wait for %f" % t)
        self.dut.timeout = t * 1.5
        x = self.ref.read(len(sample_data))
        self.assertEquals(len(sample_data), len(x))
        self.assertEquals(x, sample_data)


