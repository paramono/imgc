#!/usr/bin/env python3

import sys
import threading 

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import N, S, E, W

import imgc

class BaseFrame(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master)
        self.__dict__.update(kwargs)
        self.pack()
        self.create_widgets()


class SetupTab(BaseFrame):

    def get_images_string(self):
        # this is not working because imgh is created
        # just before image processing
        try:
            return "{} images to process".format(self.parent.imgh.imgs_total)
        except AttributeError:
            return "Press 'Run' to continue"

    def update(self):
        self.images_lbl['text'] = self.get_images_string()

    def create_widgets(self):
        for i in range(2):
            self.columnconfigure(i, pad=4)

        for i in range(5):
            self.rowconfigure(i, pad=3)

        self.size_lbl = tk.Label(self, text="Image size")
        self.size_lbl.grid(row=0, column=0, sticky=E)

        self.size = tk.StringVar(value="1000x", name="Size")
        self.size_entry = tk.Entry(self, textvariable=self.size)
        self.size_entry.grid(row=0, column=1, sticky=E)

        self.quality_lbl = tk.Label(self, text="JPEG Quality")
        self.quality_lbl.grid(row=1, column=0, sticky=E)

        self.quality = tk.IntVar(value=90, name="Quality")
        self.quality_entry = tk.Entry(self, textvariable=self.quality)
        self.quality_entry.grid(row=1, column=1, sticky=E)

        self.workers_lbl = tk.Label(self, text="Workers")
        self.workers_lbl.grid(row=2, column=0, sticky=E)

        self.workers = tk.IntVar(value=4, name="Workers")
        self.workers_entry = tk.Entry(self, textvariable=self.workers)
        self.workers_entry.grid(row=2, column=1, sticky=E)

        self.images_lbl = tk.Label(self, text=self.get_images_string())
        self.images_lbl.grid(row=3, column=0, columnspan=2, sticky=E+W)

        self.run_btn = tk.Button(self)
        self.run_btn["text"] = "Run"
        self.run_btn["command"] = self.process_images
        self.run_btn.grid(row=4, column = 0, columnspan=2)


    def process_images(self):
        args = ["size", "quality", "workers"]
        kwargs = {arg:getattr(self, arg).get() for arg in args}
        kwargs.update({"src_images": self.src_images})

        self.parent.imgh = imgc.ImageHandler(**kwargs)
        self.parent.notebook.select(1)
        self.parent.step = 100.0/self.parent.imgh.imgs_total
        self.parent.imgh.on_image_processed = self.parent.tab1.on_image_processed
        self.parent.imgh.run()


class ProgressTab(BaseFrame):
    def create_widgets(self):
        self.status_lbl = tk.Label(self, text="Waiting...")
        self.status_lbl.pack(side="top")

        self.pb = ttk.Progressbar(self, orient="horizontal", mode="determinate")
        self.pb.pack(expand=False, fill=tk.BOTH, side="top")

        self.stop_btn = tk.Button(self)
        self.stop_btn["text"] = "Stop"
        self.stop_btn["command"] = self.stop
        self.stop_btn.pack(side="top")

    def on_image_processed(self, done, total):
        percentage = done/total*100
        self.status_lbl['text'] = "{}/{} | {:4.1f}%".format(done, total, percentage)
        self.pb['value'] = percentage

    def stop(self):
        self.parent.imgh.terminate_pool()
        self.parent.notebook.select(0)

        # self.imgh


class ImgcWrap(BaseFrame):

    def create_widgets(self):
        self.master.title("imgc wrapper")
        self.master.resizable(0,0)

        self.notebook = ttk.Notebook(self)
        config = {
            'src_images': getattr(self, 'src_images', None)
        }

        self.tab_options = [
            (SetupTab, "Options", 'normal', config),
            (ProgressTab, "Progress", 'hidden', config)
        ]

        style = ttk.Style()
        style.layout('TNotebook.Tab', [])

        for i, data in enumerate(self.tab_options):
            tab, desc, state, args = data
            pattern = "tab%d" % i
            setattr(self, pattern, tab(self.notebook, **args))
            t = getattr(self, pattern)
            t.parent = self
            self.notebook.add(t, text=desc)
        self.notebook.pack()

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        try: self.imgh.terminate_pool()
        except AttributeError: pass
        self.master.destroy()


if __name__ == '__main__':
    root = tk.Tk()

    args = sys.argv[1:]
    app = ImgcWrap(master=root, src_images=args)

    root.mainloop()
