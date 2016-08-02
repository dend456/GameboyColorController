#! /usr/bin/env python

import time


class Replayer:
    def __init__(self, file, serial, button_callback=None, finish_callback=None):
        self.file = file
        self.serial = serial
        self.running = False
        self.button_callback = button_callback
        self.finish_callback = finish_callback

    def stop(self):
        self.running = False

    def run(self):
        with open(self.file) as inp:
            time.sleep(2)

            self.running = True
            start_time = time.perf_counter()
            for line in inp:
                button_text, t = line.split(' ')
                t = float(t)

                buttons = 0
                for i in range(8):
                    if button_text[i] == '1':
                        buttons |= 1 << i

                while time.perf_counter() - start_time < t and self.running:
                    pass

                if not self.running:
                    break

                self.serial.write(bytes([buttons]))
                if self.button_callback:
                    self.button_callback(buttons)

        self.serial.write(bytes([0]))
        if self.finish_callback:
            self.finish_callback()
        self.running = False

