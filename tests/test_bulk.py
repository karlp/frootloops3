from __future__ import division
import unittest
import multiprocessing
import serial
import time

import slop.handlers

REF = "/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_red_pins-if00-port0"
#DUT = "/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_0670FF484849785087085514-if02"
DUT = "/dev/serial/by-id/usb-libopencm3_usb_to_serial_cdcacm_stm32f103-generic-if00"
BAUD = 115200

class Dual(unittest.TestCase):
    def setUp(self):
        """eventually, we'll parameterise this... maybe... someday..."""
        self.ref = serial.Serial(REF, BAUD, timeout=0, write_timeout=0)
        self.dut = serial.Serial(DUT, BAUD, timeout=0, write_timeout=0)
        self.longMessage = True

    def tearDown(self):
        self.ref.close()
        self.dut.close()

    def testSendAndCheck(self):
        dual = slop.handlers.DualSender(self.dut, self.ref)
        sample_data = b"sending messages in both directions is awesome" * 10
        rval = dual.go(sample_data)
        self.assertEquals(len(rval["dut"]), len(sample_data))
        self.assertEquals(len(rval["ref"]), len(sample_data))
        self.assertEquals(sample_data, rval["ref"])
        self.assertEquals(sample_data, rval["dut"])


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


