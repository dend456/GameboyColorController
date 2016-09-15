#! /usr/bin/env python

import tkinter as tk
from tkinter import filedialog
import time
from threading import Thread
from . import gbc
from .recorder import Recorder
from .replay import Replayer


class GBCController(tk.Frame):
    def __init__(self, system):
        self.system = system
        self.root = system.root
        self.__setup_ui()
        self.buttons = 0
        self.recorder = None
        self.replayer = None
        self.keymap = {'a': (self.left, gbc.GBC.Buttons.left),
                       'w': (self.up, gbc.GBC.Buttons.up),
                       'd': (self.right, gbc.GBC.Buttons.right),
                       's': (self.down, gbc.GBC.Buttons.down),
                       'k': (self.b, gbc.GBC.Buttons.b),
                       'l': (self.a, gbc.GBC.Buttons.a),
                       'n': (self.select, gbc.GBC.Buttons.select),
                       'm': (self.start, gbc.GBC.Buttons.start)}

    def __setup_ui(self):
        dpad_panel = tk.Frame(self.root)
        buttons_panel = tk.Frame(self.root)
        ab_panel = tk.Frame(buttons_panel)
        ss_panel = tk.Frame(buttons_panel)

        self.left = tk.Button(dpad_panel, text='←', width=4, height=2, font=('Helvetica', 22))
        self.up = tk.Button(dpad_panel, text='↑', width=4, height=2, font=('Helvetica', 22))
        self.right = tk.Button(dpad_panel, text='→', width=4, height=2, font=('Helvetica', 22))
        self.down = tk.Button(dpad_panel, text='↓', width=4, height=2, font=('Helvetica', 22))

        self.b = tk.Button(ab_panel, text='B', width=8, height=4)
        self.a = tk.Button(ab_panel, text='A', width=8, height=4)

        self.select = tk.Button(ss_panel, text='Select')
        self.start = tk.Button(ss_panel, text='Start')

        self.left.bind('<ButtonPress-1>', lambda e: self.__button_press(gbc.GBC.Buttons.left))
        self.left.bind('<ButtonRelease-1>', lambda e: self.__button_release(gbc.GBC.Buttons.left))
        self.up.bind('<ButtonPress-1>', lambda e: self.__button_press(gbc.GBC.Buttons.up))
        self.up.bind('<ButtonRelease-1>', lambda e: self.__button_release(gbc.GBC.Buttons.up))
        self.down.bind('<ButtonPress-1>', lambda e: self.__button_press(gbc.GBC.Buttons.down))
        self.down.bind('<ButtonRelease-1>', lambda e: self.__button_release(gbc.GBC.Buttons.down))
        self.right.bind('<ButtonPress-1>', lambda e: self.__button_press(gbc.GBC.Buttons.right))
        self.right.bind('<ButtonRelease-1>', lambda e: self.__button_release(gbc.GBC.Buttons.right))

        self.b.bind('<ButtonPress-1>', lambda e: self.__button_press(gbc.GBC.Buttons.b))
        self.b.bind('<ButtonRelease-1>', lambda e: self.__button_release(gbc.GBC.Buttons.b))
        self.a.bind('<ButtonPress-1>', lambda e: self.__button_press(gbc.GBC.Buttons.a))
        self.a.bind('<ButtonRelease-1>', lambda e: self.__button_release(gbc.GBC.Buttons.a))

        self.select.bind('<ButtonPress-1>', lambda e: self.__button_press(gbc.GBC.Buttons.select))
        self.select.bind('<ButtonRelease-1>', lambda e: self.__button_release(gbc.GBC.Buttons.select))
        self.start.bind('<ButtonPress-1>', lambda e: self.__button_press(gbc.GBC.Buttons.start))
        self.start.bind('<ButtonRelease-1>', lambda e: self.__button_release(gbc.GBC.Buttons.start))

        self.root.bind('<Key>', self.__keypress)
        self.root.bind('<KeyRelease>', self.__keypress)

        self.left.grid(column=0, row=5, columnspan=4, rowspan=4)
        self.up.grid(column=5, row=0, columnspan=4, rowspan=4)
        self.right.grid(column=9, row=5, columnspan=4, rowspan=4)
        self.down.grid(column=5, row=9, columnspan=4, rowspan=4)

        self.b.pack(side='left', padx=10, pady=10)
        self.a.pack(side='right', padx=10, pady=10)
        self.select.pack(side='left', padx=10, pady=10)
        self.start.pack(side='right', padx=10, pady=10)

        self.record = tk.Button(text='Record', command=self.__record_pressed)
        self.replay = tk.Button(text='Replay', command=self.__replay_pressed)
        self.reset = tk.Button(text='Reset', command=self.__reset_pressed)

        ab_panel.pack(side='top')
        ss_panel.pack(side='bottom')

        dpad_panel.pack(side='left', padx=10, pady=10)
        buttons_panel.pack(side='right', padx=10, pady=10)
        self.record.pack()
        self.replay.pack()
        self.reset.pack()

    def __keypress(self, event):
        ub, button = self.keymap.get(event.char, (None, None))
        if button:
            if event.type == '2':
                self.__button_press(button)
                ub.configure(background='red')
            elif event.type == '3':
                self.__button_release(button)
                ub.configure(background='white')

    def __button_release(self, button):
        old = self.buttons
        self.buttons &= ~button
        if old != self.buttons and self.system.ser:
            self.system.ser.write(bytes([self.buttons]))

    def __button_press(self, button):
        if self.replayer or self.recorder:
            return
        old = self.buttons
        self.buttons |= button
        if old != self.buttons and self.system.ser:
            self.system.ser.write(bytes([self.buttons]))

    def __reset_pressed(self):
        self.buttons = 0
        for k, button in self.keymap.items():
            button[0].configure(background='white')
        if self.system.ser:
            self.system.ser.write(bytes([gbc.GBC.Buttons.reset]))
            time.sleep(.1)
            self.system.ser.write(bytes([gbc.GBC.Buttons.none]))

    def __record_pressed(self):
        if self.recorder:
            self.recorder.stop()
            self.recorder = None
            self.record.configure(foreground='black')
        elif self.system.ser:
            file = tk.filedialog.asksaveasfilename(filetypes=(('Replay', '*.rep'),), defaultextension='.rep')
            if file:
                self.recorder = Recorder(file, self.system.ser)
                self.record.configure(foreground='red')
                Thread(target=self.recorder.run, daemon=True).start()

    def __replay_pressed(self):
        if self.replayer:
            self.replayer.stop()
            self.replayer = None
            self.replay.configure(text='Replay')
            for k, b in self.keymap.items():
                    b[0].configure(background='white')
        elif self.system.ser:
            file = tk.filedialog.askopenfilename(filetypes=(('Replay', '*.rep'),))
            if file:
                self.replayer = Replayer(file, self.system.ser, button_callback=self.__replay_button_callback, finish_callback=self.__replay_finish_callback)
                self.replay.configure(text='Stop')
                Thread(target=self.replayer.run, daemon=True).start()

    def __replay_finish_callback(self):
        if self.replayer:
            self.replayer.stop()
            self.replayer = None
            self.replay.configure(text='Replay')
            for k, b in self.keymap.items():
                    b[0].configure(background='white')

    def __replay_button_callback(self, buttons):
        for k, b in self.keymap.items():
            if buttons & b[1]:
                b[0].configure(background='red')
            else:
                b[0].configure(background='white')


