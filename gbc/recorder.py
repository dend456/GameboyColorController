#! /usr/bin/env python

import time
from . import gbc


class Recorder:
    def __init__(self, file, serial):
        self.file = file
        self.serial = serial
        self.running = False

    def stop(self):
        self.running = False

    def run(self):
        with open(self.file, 'wb') as out:
            self.running = True
            start_time = None
            self.serial.write(bytes([gbc.GBC.Buttons.record]))
            while self.running:
                inp = self.serial.read()
                if len(inp) == 0:
                    continue
                buttons = int.from_bytes(inp, byteorder='big')
                if not start_time:
                    start_time = time.perf_counter()
                t = time.perf_counter() - start_time
                buttons_text = bytes('{:08b} {}'.format(buttons, t), 'utf-8')
                out.write(b'%s\n' % buttons_text)
            self.serial.write(bytes([gbc.GBC.Buttons.record]))