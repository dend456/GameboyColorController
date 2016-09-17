#! /usr/bin/env python

import time
from . import controller


class Replayer:
    INPUT_BUFFER_SIZE = 512
    INITIAL_BUFFER_SIZE = 512

    def __init__(self, file, serial, button_callback=None, finish_callback=None):
        self.file = file
        self.serial = serial
        self.running = False
        self.button_callback = button_callback
        self.finish_callback = finish_callback

    def stop(self):
        self.running = False

    @staticmethod
    def __text_to_button(button_text):
        button_text = button_text.rstrip()
        buttons = 0
        for i in range(8):
            if button_text[i] == '1':
                buttons |= 1 << i
        return buttons

    def run(self):
        with open(self.file) as inp:
            time.sleep(2)
            current_frame = 0

            self.serial.reset_input_buffer()
            self.serial.write(bytes([controller.Signal.change_mode, controller.Mode.replay]))
            time.sleep(.5)
            self.running = True

            buttons = list(map(Replayer.__text_to_button, inp))
            for button in buttons[:Replayer.INITIAL_BUFFER_SIZE]:
                self.serial.write(bytes([button]))
                if self.button_callback:
                    self.button_callback(button)

            for button in buttons[Replayer.INITIAL_BUFFER_SIZE:]:
                data = None
                while self.running and data != bytes([controller.Signal.send_byte]):
                    data = self.serial.read(1)

                if not self.running:
                    break

                self.serial.write(bytes([button]))
                if self.button_callback:
                    self.button_callback(button)

        self.serial.write(bytes([controller.Signal.finished_replay]))

        while True:
            data = self.serial.read(1)
            if data == bytes([controller.Signal.finished_replay]):
                break

        if self.finish_callback:
            self.finish_callback()
        self.running = False

