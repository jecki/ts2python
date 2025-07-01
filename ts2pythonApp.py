#!/usr/bin/env python3

"""ts2pythonApp.py - a simple GUI for the compilation of ts2python-files"""

import sys
import os
import threading

import tkinter as tk
import webbrowser
from tkinter import ttk
from tkinter import filedialog, messagebox, scrolledtext


try:
    scriptdir = os.path.dirname(os.path.realpath(__file__))
except NameError:
    scriptdir = ''
if scriptdir and scriptdir not in sys.path: sys.path.append(scriptdir)

import ts2pythonParser


class ts2pythonApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title('ts2python App')
        self.minsize(640, 400)
        self.geometry("960x680")
        self.option_add('*tearOff', False)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # window content resizes with window:
        # win = self.winfo_toplevel()
        # win.rowconfigure(0, weight=1)
        # win.columnconfigure(0, weight=1)
        # self.rowconfigure(0, weight=1)
        # self.columnconfigure(1, weight=1)

        if 'html' in ts2pythonParser.targets or 'HTML' in ts2pythonParser.targets:
            self.target = 'html'
        elif len(ts2pythonParser.targets) == 1:
            self.target = list(ts2pythonParser.targets)[0]
        else:
            self.target = ''

        # widget-variables
        self.num_sources = 0
        self.num_compiled = 0
        self.progress = tk.IntVar()
        self.progress.set(0)

        self.source_modified_sentinel = 0

        self.create_widgets()
        self.connect_events()
        self.place_widgets()

        self.lock = threading.Lock()
        self.worker = None
        self.cancel_flag = False

        self.outdir = ''
        self.names = []

        self.deiconify()

    def create_widgets(self):
        self.pick_source_info = ttk.Label(text="Paste source code below or...")
        self.pick_source = ttk.Button(text="Pick Source file(s)...",
                                      command=self.on_pick_source)
        self.source_info = ttk.Label(text='Source:')
        self.source_undo = ttk.Button(text="Undo", command=self.on_source_undo)
        self.source_clear = ttk.Button(text="Clear source", command=self.on_clear_source)
        self.source = scrolledtext.ScrolledText(undo=True)
        self.result_info = ttk.Label(text='Result:')
        self.result = scrolledtext.ScrolledText()
        self.errors_info = ttk.Label(text='Errors:')
        self.errors = scrolledtext.ScrolledText()
        self.progressbar = ttk.Progressbar(orient="horizontal", variable=self.progress)
        self.cancel = ttk.Button(text="Cancel", command=self.on_cancel)
        self.cancel['state'] = tk.DISABLED
        self.message = ttk.Label(text='')
        self.exit = ttk.Button(text="Quit", command=self.on_close)

    def connect_events(self):
        self.source.bind("<<Modified>>", self.on_source_change)

    def place_widgets(self):
        padW = dict(sticky=(tk.W,), padx="5", pady="5")
        padE = dict(sticky=(tk.E,), padx="5", pady="5")
        padWE = dict(sticky=(tk.W, tk.E), padx="5", pady="5")
        padAll = dict(sticky=(tk.N, tk.S, tk.W, tk.E), padx="5", pady="5")
        padNW = dict(sticky=(tk.W, tk.N), padx="5", pady="5")
        self.pick_source_info.grid(row=0, column=2, **padW)
        self.pick_source.grid(row=0, column=3, **padW)
        self.source_info.grid(row=1, column=0, **padW)
        self.source_undo.grid(row=1, column=4, **padE)
        self.source_clear.grid(row=1, column=5, **padE)
        self.source.grid(row=2, column=0, columnspan=6, **padAll)
        self.result_info.grid(row=3, column=0, **padW)
        self.result.grid(row=4, column=0, columnspan=6, **padAll)
        self.errors_info.grid(row=5, column=0, **padW)
        self.errors.grid(row=6, column=0, columnspan=6, **padAll)
        self.progressbar.grid(row=7, column=0, columnspan=5, **padWE)
        self.cancel.grid(row=7, column=5, **padE)
        self.message.grid(row=8, column=0, columnspan=5, **padWE)
        self.exit.grid(row=8, column=5, **padE)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(6, weight=2)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(4, weight=1)

    def clear_result(self):
        with self.lock:
            self.errors.delete("1.0", tk.END)
            self.update()

    def log_callback(self, txt):
        self.errors.insert(tk.END, txt + '\n')
        self.errors.yview_moveto(1.0)
        self.num_compiled += 1
        self.progress.set(min(100, int(100 * self.num_compiled / self.num_sources)))
        self.update()

    def cancel_callback(self) -> bool:
        with self.lock:
            res = self.cancel_flag
        return res

    def poll_worker(self):
        self.update_idletasks()
        if self.worker and self.worker.is_alive():
            self.after(1000, self.poll_worker)
        else:
            self.cancel['stat'] = tk.DISABLED
            if self.cancel_flag:
                self.errors.yview_moveto(1.0)
                with self.lock:  self.cancel_flag = False
            else:
                self.errors.insert(tk.END, "Compilation finished.\n")
                self.errors.insert(tk.END, f"Results written to {self.outdir}.\n")
                if len(self.names) == 1:
                    basename = os.path.splitext(os.path.basename(self.names[0]))[0]
                    for msgtype in ('_ERRORS.txt', '_WARNINGS.txt'):
                        msgfile = os.path.join(self.outdir, basename + msgtype)
                        if os.path.exists(msgfile):
                            with open(msgfile, 'r', encoding='utf-8') as f:  msg = f.read()
                            lines = msg.split('\n')
                            leadout = '...\n' if len(lines) > 20 else '\n'
                            msg = '\n'.join([msgtype[1:-4] ] + lines[:20] + [leadout])
                            self.errors.insert(tk.END, msg)
                            break
                else:
                    self.errors.insert(tk.END,
                        f"Errors (if any) written to {self.outdir}.\n")
                if self.target == 'html':
                    html_name = os.path.splitext(os.path.basename(self.names[0]))[0] + '.html'
                    html_name = os.path.join(self.outdir, html_name)
                    self.errors.insert(tk.END, html_name + "\n")
                    webbrowser.open('file://' + os.path.abspath(html_name)
                                    if sys.platform == "darwin" else html_name)
                else:
                    webbrowser.open('file://' + os.path.abspath(self.outdir)
                                    if sys.platform == "darwin" else self.outdir)
            self.worker = None

    def on_pick_source(self):
        if not self.worker or self.on_cancel():
            self.progress.set(0)
            self.names = list(tk.filedialog.askopenfilenames(
                title="Chose files to parse/compile",
                filetypes=[('All', '*')]
            ))
            if self.names:
                self.num_sources = len(self.names)
                self.num_compiled = 0
                self.outdir = os.path.join(os.path.dirname(self.names[0]), 'ts2python_output')
                if not os.path.exists(self.outdir):  os.mkdir(self.outdir)
                with self.lock:  self.cancel_flag = False
                self.worker = threading.Thread(
                    target = ts2pythonParser.batch_process,
                    args = (self.names, self.outdir),
                    kwargs = dict([('log_func', self.log_callback),
                                   ('cancel_func', self.cancel_callback)]))
                self.worker.start()
                self.cancel['stat'] = tk.NORMAL
                self.after(1000, self.poll_worker)

    def on_clear_source(self):
        self.source.delete('1.0', tk.END)
        self.source_modified_sentinel = 2

    def on_source_change(self, event):
        if self.source_modified_sentinel: # ignore call due to change of emit_modified
            self.source_modified_sentinel -= 1
            if self.source_modified_sentinel > 0:
                self.source.edit_modified(False)
        else:
            txt = self.source.get("1.0", tk.END)
            self.source_modified_sentinel = 1
            self.source.edit_modified(False)

    def on_source_undo(self):
        self.source.edit_undo()
        txt = self.source.get("1.0", tk.END)
        self.source_modified_sentinel = 2

    def on_cancel(self) -> bool:
        if self.worker:
            if tk.messagebox.askyesno(
                title="Cancel?",
                message="A parsing/compilation-process is still under way!\n"
                        "Cancel running process?"):
                if self.worker:
                    with self.lock:  self.cancel_flag = True
                    self.errors.insert(tk.END, "Canceling reaming tasks...\n")
                    self.update()
                    self.update_idletasks()
                    self.worker.join(5.0)
                    if not self.worker.is_alive():
                        self.errors.insert(tk.END, "Stopped.\n")
                        self.cancel_flag = False
                    self.errors.yview_moveto(1.0)
                    return True
                else:
                    with self.lock:  self.cancel_flag = False
                    return False
        return True

    def on_close(self):
        if self.on_cancel():
            if self.worker and self.worker.is_alive():
                self.errors.insert(tk.END, "Killing still running processes!\n")
                self.errors.yview_moveto(1.0)
            self.destroy()
            self.quit()


if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()

    if not ts2pythonParser.main(called_from_app=True):
        app = ts2pythonApp()
        app.mainloop()

