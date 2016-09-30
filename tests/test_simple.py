

REF="/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_red_pins-if00-port0"
DUT="/dev/serial/by-id/usb-libopencm3_usb_to_serial_cdcacm_stm32f103-generic-if00"


import unittest
import serial

# FIXME - oh yeah, if you don't run the reader in a thread/process, you can overflow rx buffers and shit.
# can't rely on the OS to do that!
# this is the whole guts of how this is mean to work!

class Simple(unittest.TestCase):

    def setUp(self):
        """eventually, we'll parameterise this... maybe... someday..."""
        self.ref = serial.Serial(REF, 115200)
        self.dut = serial.Serial(DUT, 115200)

    def tearDown(self):
        self.ref.close()
        self.dut.close()

    def testRX(self):
        sample_data = b"the ref wrote some data for the dut to listen to"
        self.ref.write(sample_data)
        x = self.dut.read(len(sample_data))
        self.assertEquals(x, sample_data)

    def testTX(self):
        sample_data = b"the dut wrote some data and we hope the ref got it"
        self.dut.write(sample_data)
        x = self.ref.read(len(sample_data))
        self.assertEquals(x, sample_data)

