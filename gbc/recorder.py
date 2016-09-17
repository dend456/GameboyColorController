#! /usr/bin/env python

from . import controller


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
            self.serial.reset_input_buffer()
            self.serial.write(bytes([controller.Signal.change_mode, controller.Mode.record]))
            while self.running:
                inp = self.serial.read()
                if len(inp) == 0:
                    continue
                buttons = int.from_bytes(inp, byteorder='big')

                buttons_text = bytes('{:08b}'.format(buttons), 'utf-8')
                out.write(b'%s\n' % buttons_text)
            self.serial.write(bytes([controller.Signal.change_mode, controller.Mode.freeplay]))
