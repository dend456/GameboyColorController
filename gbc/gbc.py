#! /usr/bin/env python

import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk
from .controller import GBCController


class GBC:
    class Buttons:
        left = 0b00000001
        down = 0b00000010
        select = 0b00000100
        right = 0b00001000
        up = 0b00010000
        b = 0b00100000
        a = 0b01000000
        start = 0b10000000
        none = 0b00000000
        record = 0b11111111
        reset = start | select | a | b

    def __init__(self, port='COM4', baud=9600):
        self.baud = baud
        self.ports = list(serial.tools.list_ports.comports())
        self.root = tk.Tk()
        self.ser = None
        self.default_port = port
        self.__setup_ui()
        self.controller = GBCController(self)

    def __setup_ui(self):
        self.root.title('GBC')

        ports_panel = tk.Frame(self.root)
        self.ports_box = ttk.Combobox(ports_panel, values=list(reversed([x[0] for x in self.ports])))
        self.ports_box.bind('<<ComboboxSelected>>', self.__port_selected)
        refresh_button = tk.Button(ports_panel, text='Refesh', command=self.__refresh_ports)

        self.ports_box.pack(side='left')
        refresh_button.pack(side='right')
        ports_panel.pack()

        if self.default_port and self.default_port in [x[0] for x in self.ports]:
            self.ports_box.set(self.default_port)
            self.ser = serial.Serial(self.ports_box.get(), baudrate=self.baud, timeout=.1)

    def __refresh_ports(self):
        self.ports = list(serial.tools.list_ports.comports())
        self.ports_box['values'] = list(reversed([x[0] for x in self.ports]))

    def __port_selected(self, event):
        if self.ser and self.ser.isOpen():
            self.ser.close()

        self.ser = serial.Serial(self.ports_box.get(), baudrate=self.baud, timeout=.1)

    def __del__(self):
        if self.ser and self.ser.isOpen():
            self.ser.close()

    def start(self):
        self.root.mainloop()
