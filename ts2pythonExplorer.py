#!/usr/bin/env python3

"""ts2pythonExplorer.py - a simple GUI for the compilation of ts2python-snippets"""

import sys
import os
import re
import threading
from typing import cast, Tuple

import tkinter as tk
import webbrowser
from tkinter import ttk
from tkinter import filedialog, messagebox, scrolledtext, font

from DHParser import set_preset_value
from DHParser.error import Error, ERROR
from DHParser.configuration import read_local_config, get_config_values, \
    dump_config_data, access_presets, finalize_presets, set_preset_value
from DHParser.nodetree import Node, EMPTY_NODE
from DHParser.pipeline import PipelineResult
from DHParser.testing import merge_test_units
from DHParser.toolkit import MultiCoreManager

try:
    scriptdir = os.path.dirname(os.path.realpath(__file__))
except NameError:
    scriptdir = ''
if scriptdir and scriptdir not in sys.path: sys.path.append(scriptdir)

import ts2pythonParser


class TextLineNumbers(tk.Canvas):
    """See https://stackoverflow.com/questions/16369470/tkinter-adding-line-number-to-text-widget
    and https://stackoverflow.com/questions/24896747/how-to-display-line-numbers-in-tkinter-text-widget
    """
    def __init__(self, text_widget, **kwargs):
        super().__init__(width=40, **kwargs)
        self.first_line = ""
        self.last_line = ""
        self.text_widget = text_widget
        self.text_widget.bind('<KeyRelease>', self.redraw) # This is insufficient and does not work under all OSs
        self.text_widget.bind('<MouseWheel>', self.redraw)
        self.text_widget.bind('<B1-Motion>', self.redraw)
        self.text_widget.bind('<Button-1>', self.redraw)
        self.text_widget.bind('<Configure>', self.redraw)
        self.text_widget['yscrollcommand'] = self.yscrollcommand
        self.text_widget.vbar['command'] = self.yview
        self.redraw()

    def yview(self, *args):
        self.redraw()
        self.text_widget.yview(*args)

    def yscrollcommand(self, *args):
        self.redraw()
        return self.text_widget.vbar.set(*args)

    def redraw_needed(self):
        """-> index of the last line"""
        first = self.text_widget.index("@0,0")
        ysize = self.text_widget.winfo_height()
        last = self.text_widget.index(f"@0,{ysize}")
        if first != self.first_line or last != self.last_line:
            return first, last
        return "", ""

    def redraw(self, event=None):
        first, last = self.redraw_needed()
        if first:
            self.first_line = first
            self.last_line = last
            self.delete("all")
            i = first
            self.first_line = float(i)
            while True:
                dline = self.text_widget.dlineinfo(i)
                if dline is None:
                    break
                y = dline[1]
                linenum = str(i).split(".")[0]
                self.create_text(2, y, anchor="nw", text=linenum)
                i = self.text_widget.index(f"{i}+1line")


DEMO_TS = """// This is just an example. You can replace it by your own Typescript-code
// or just click "compile" below to see how this interface look as Python-code.

interface CodeAction {
  title: string;
  kind?: CodeActionKind;
  diagnostics?: Diagnostic[];
  isPreferred?: boolean;
  disabled?: {
    reason: string;
  };
  edit?: WorkspaceEdit;
  command?: Command;
  data?: any;
}"""


class ts2pythonApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title('ts2python Explorer')
        self.minsize(800, 680)
        self.geometry("960x880")
        self.option_add('*tearOff', False)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # window content resizes with window:
        # win = self.winfo_toplevel()
        # win.rowconfigure(0, weight=1)
        # win.columnconfigure(0, weight=1)
        # self.rowconfigure(0, weight=1)
        # self.columnconfigure(1, weight=1)

        # (widget-)variables
        self.num_sources = 0
        self.num_compiled = 0
        self.progress = tk.IntVar()
        self.progress.set(0)

        self.source_modified_sentinel = 0
        self.source_paste = False
        self.python_version = tk.StringVar(value="3.11")
        self.preambel = ''
        self.set_presets(version=(3, 11))
        self.render_anonymous = tk.StringVar(value="as local class (!)")
        self.root_parser = "document"
        self.compilation_units = 0
        self.outdir = ''
        self.names = []
        self.all_results: PipelineResult = {}
        self.error_list = []

        # widgets
        self.targets = [j.dst for j in ts2pythonParser.junctions]
        self.targets.sort(key=lambda s: s in ts2pythonParser.targets)
        self.compilation_target = list(ts2pythonParser.targets)[0]
        self.target_name = tk.StringVar(value=self.compilation_target)
        self.target_format = tk.StringVar(value="SXML")

        self.default_font = font.nametofont("TkDefaultFont")
        font_properties = self.default_font.actual()
        family, size = font_properties['family'], font_properties['size']
        self.bold_label = ttk.Style()
        self.bold_label.configure("Bold.TLabel", font=(family, size, "bold"))
        self.green_label = ttk.Style()
        self.green_label.configure("Green.TLabel", foreground="green")
        self.red_label = ttk.Style()
        self.red_label.configure("Red.TLabel", foreground="red")
        self.grey_label = ttk.Style()
        self.grey_label.configure("Grey.TLabel", foreground="grey")
        self.black_label = ttk.Style()
        self.black_label.configure("Black.TLabel", foreground="black")
        self.bold_button = ttk.Style()
        self.bold_button.configure("BoldRed.TButton", font=(family, size, "bold"),
                                   foreground="red")
        self.normal_button = ttk.Style()
        self.normal_button.configure("NormalBlack.TButton", font=(family, size, "bold"),
                                     foreground="black")

        self.create_widgets()
        self.source.insert(tk.END, DEMO_TS)
        self.connect_events()
        self.place_widgets()

        # multicore/-threading environement
        self.lock = threading.Lock()
        self.worker = None
        self.mc_manager = MultiCoreManager()
        # self.mc_manager.start()
        self.cancel_event = self.mc_manager.Event()

        self.deiconify()

    def create_widgets(self):
        # self.header = ttk.Label(text="")
        combo_width = 12
        self.pick_source_info = ttk.Label(text="Paste your source code below or...", style="Green.TLabel")
        self.pick_source = ttk.Button(text="Pick Source file(s)...",
                                      command=self.on_pick_source)
        self.source_info = ttk.Label(text='Source:', style="Bold.TLabel")
        self.source_undo = ttk.Button(text="Undo", command=self.on_source_undo)
        self.source_clear = ttk.Button(text="Clear source", command=self.on_clear_source)
        self.source_clear['state'] = tk.DISABLED

        self.source = scrolledtext.ScrolledText(undo=True)
        self.line_numbers = TextLineNumbers(self.source)

        self.options_label = ttk.Label(text="Options:", style="Bold.TLabel")
        self.python_version_label = ttk.Label(text="Python-version compatibility:")
        self.python_version_selector = ttk.Combobox(self,
            values=('3.14 or higher', '3.13 or higher', '3.12 or higher',
                    '3.11 or higher', '3.10 or higher', '3.9 or higher',
                    '3.8 or higher', '3.7 or higher'),
            textvariable=self.python_version, width=combo_width)
        self.render_anonymous_label = ttk.Label(text="Handling of anonymous types:")
        self.render_anonymous_table = {'as toplevel class': 'toplevel',
                                       'as local class (!)': 'local',
                                       'as inline type': 'type',
                                       'as function call': 'functional'}
        self.render_anonymous_selector = ttk.Combobox(
            self, values = tuple(self.render_anonymous_table.keys()),
            textvariable=self.render_anonymous, width=combo_width)

        self.compile = ttk.Button(text="Generate Python Code", style="BoldRed.TButton",
                                  command=self.on_compile)
        self.compile['state'] = tk.NORMAL  # tk.DISABLED
        self.target_label = ttk.Label(text="Compilation stage:")
        self.target_stage = ttk.Combobox(self,
            values=self.targets, textvariable=self.target_name, width=combo_width)
        self.output_label = ttk.Label(text="Output format:")
        self.output_choice = ttk.Combobox(
            self, values=['XML', 'SXML', 'sxpr', 'xast', 'ndst', 'tree'],
            textvariable=self.target_format, width=combo_width)
        if self.target_name.get() not in ('AST', 'CST'):
            self.output_choice['state'] = tk.DISABLED
        self.result_info = ttk.Label(text='Result:', style="Bold.TLabel")

        self.result = scrolledtext.ScrolledText()
        # self.result['state'] = tk.DISABLED

        self.export_config = ttk.Button(text="Export configuration...",
                                        command=self.on_export_config)
        self.save_result = ttk.Button(text="Save result...",
                                      command=self.on_save_result)
        self.save_result['state'] = tk.DISABLED
        self.export_test = ttk.Button(text="Export as test case...",
                                      command=self.on_export_test)
        self.export_test['state'] = tk.DISABLED

        self.errors_info = ttk.Label(text='Errors:', style="Bold.TLabel")

        self.errors = scrolledtext.ScrolledText()
        # self.errors['state'] = tk.DISABLED

        self.progressbar = ttk.Progressbar(orient="horizontal",
                                           variable=self.progress)
        self.cancel = ttk.Button(text="Cancel", command=self.on_cancel)
        self.cancel['state'] = tk.DISABLED

        self.message = ttk.Label(text='', style="Black.TLabel")
        self.exit = ttk.Button(text="Quit", command=self.on_close)

        self.menubar = tk.Menu(self)
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(menu=self.file_menu, label="File")
        self.file_menu.add_command(label="Load Typescript code...", command=self.on_pick_source)
        self.file_menu.add_command(label="Save Python code...", command=self.on_save_result)
        self.file_menu.entryconfig("Save Python code...", state=tk.DISABLED)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_close)
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(menu=self.help_menu, label="Help")
        self.help_menu.add_command(label="ts2python Docs", command=self.open_docs)
        self.help_menu.add_command(label="ts2python Sources", command=self.open_github)
        self.help_menu.add_command(label="License Info", command=self.open_license)
        self.help_menu.add_separator()
        self.help_menu.add_command(label="About...", command=self.on_about)
        self.config(menu=self.menubar)
        # win = tk.Toplevel(self)
        # win['menu'] = self.menubar

    def connect_events(self):
        self.source.bind("<<Modified>>", self.on_source_change)
        self.source.bind("<Control-v>", self.on_source_insert, add="+")
        self.source.bind("<Command-v>", self.on_source_insert, add="+")
        self.source.bind("<KeyRelease>", self.on_source_key, add="+")
        self.source.bind("<Button-1>", self.on_source_mouse, add="+")
        self.python_version_selector.bind("<<ComboboxSelected>>",
                                          self.on_version_selector)
        self.render_anonymous_selector.bind("<<ComboboxSelected>>",
                                            self.on_anonymous_selector)
        self.target_stage.bind("<<ComboboxSelected>>", self.on_target_stage)
        self.output_choice.bind("<<ComboboxSelected>>", self.on_output_choice)
        self.errors.bind('<KeyRelease>', self.on_errors_key)
        # self.errors.bind('<MouseWheel>', self.on_errors_mouse)
        self.errors.bind('<Button-1>', self.on_errors_mouse)
        # self.errors.bind('<Configure>', self.on_errors)

    def place_widgets(self):
        padW = dict(sticky=(tk.W,), padx="5", pady="5")
        padE = dict(sticky=(tk.E,), padx="5", pady="5")
        padWE = dict(sticky=(tk.W, tk.E), padx="5", pady="5")
        padNW = dict(sticky=(tk.W, tk.N), padx="5", pady="5")
        padAll = dict(sticky=(tk.N, tk.S, tk.W, tk.E), padx="5", pady="5")
        # self.header.grid(row=0, column=0, columnspan=5, **padAll)

        self.source_info.grid(row=0, column=0, **padW)
        self.pick_source_info.grid(row=0, column=1, **padW)
        self.pick_source.grid(row=0, column=2, **padW)
        self.source_undo.grid(row=0, column=3, **padE)
        self.source_clear.grid(row=0, column=4, **padE)

        self.source.grid(row=1, column=1, columnspan=4, **padAll)
        self.line_numbers.grid(row=1, column=0, **padAll)

        self.compile.grid(row=2, column=2, **padWE)

        self.options_label.grid(row=3, column=0, **padW)
        self.python_version_label.grid(row=3, column=1, **padE)
        self.python_version_selector.grid(row=3, column=2, **padW)
        self.render_anonymous_label.grid(row=3, column=3, **padE)
        self.render_anonymous_selector.grid(row=3, column=4, **padW)

        self.result_info.grid(row=4, column=0, **padW)
        self.target_label.grid(row=4, column=1, **padE)
        self.target_stage.grid(row=4, column=2, **padW)
        self.output_label.grid(row=4, column=3, **padE)
        self.output_choice.grid(row=4, column=4, **padW)

        self.result.grid(row=5, column=0, columnspan=5, **padAll)

        self.errors_info.grid(row=6, column=0, **padW)
        self.export_config.grid(row=6, column=1, **padW)
        self.save_result.grid(row=6, column=2, **padWE)
        self.export_test.grid(row=6, column=3, **padE)

        self.errors.grid(row=7, column=0, columnspan=5, **padAll)

        # self.progressbar.grid(row=8, column=0, columnspan=5, **padWE)
        self.cancel.grid(row=8, column=4, **padE)

        self.message.grid(row=9, column=0, columnspan=4, **padWE)
        self.exit.grid(row=9, column=4, **padE)

        self.rowconfigure(1, weight=1)
        self.rowconfigure(5, weight=1)
        self.rowconfigure(7, weight=2)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.source.focus_set()

    def show_progressbar(self):
        padWE = dict(sticky=(tk.W, tk.E), padx="5", pady="5")
        self.progressbar.grid(row=8, column=0, columnspan=5, **padWE)

    def hide_progressbar(self):
        self.progressbar.grid_forget()

    def clear_result(self):
        with self.lock:
            self.errors.delete("1.0", tk.END)
            self.update()

    def log_callback(self, txt):
        self.result.insert(tk.END, txt + '\n')
        # self.errors.yview_moveto(1.0)
        self.num_compiled += 1
        self.progress.set(min(100, int(100 * self.num_compiled / self.num_sources)))
        self.update()

    def clear_message(self):
        def clear():
            self.message['text'] = ''
            self.message['style'] = 'Black.TLabel'
        self.message['style'] = 'Grey.TLabel'
        self.after(1500, clear)

    def poll_worker(self):
        self.update_idletasks()
        if self.worker and self.worker.is_alive():
            if self.cancel['state'] != tk.NORMAL \
                    and not self.cancel_event.is_set():
                self.cancel['state'] = tk.NORMAL
                self.show_progressbar()
            self.after(500, self.poll_worker)
        else:
            self.cancel['state'] = tk.DISABLED
            self.progressbar.stop()
            if self.cancel_event.is_set():
                self.errors.insert(tk.END, "Canceled\n")
                self.result.yview_moveto(1.0)
            elif self.compilation_units == 1:
                self.finish_single_unit()
                self.progressbar['mode'] = 'determinate'
                self.progress.set(0)
            else:
                self.finish_multiple_units()
            self.worker = None
            self.compilation_units = 0
            self.compilation_target = ""
            self.after(500, self.hide_progressbar)

    def on_pick_source(self):
        if not self.worker or self.on_cancel():
            self.progressbar.stop()
            self.progressbar['mode'] = 'determinate'
            self.progress.set(0)
            self.names = list(tk.filedialog.askopenfilenames(
                title="Chose files to parse/compile",
                filetypes=[('All', '*')]
            ))
            if self.names:
                self.all_results = {}
                self.error_list = []
                self.source.delete(1.0, tk.END)
                self.result.delete(1.0, tk.END)
                self.errors.delete(1.0, tk.END)
                self.export_test['state'] = tk.DISABLED
                self.save_result['state'] = tk.DISABLED
                self.file_menu.entryconfig("Save Python code...", state=tk.DISABLED)
                if len(self.names) == 1:
                    try:
                        with open(self.names[0], 'r', encoding='utf-8') as f:
                            snippet = f.read()
                            self.source.insert(tk.END, snippet)
                            self.export_test['state'] = tk.NORMAL
                    except (FileNotFoundError, PermissionError,
                            IsADirectoryError, IOError, UnicodeDecodeError) as e:
                        self.result.insert(tk.END, str(e))
                        tk.messagebox.showerror("IO Error", str(e))
                        self.message['text'] = 'IOError: ' + e.__class__.__name__
                        self.message['style'] = "Red.TLabel"
                        self.after(2500, self.clear_message)
                else:
                    self.cancel_event.clear()
                    self.num_sources = len(self.names)
                    self.num_compiled = 0
                    self.outdir = os.path.join(os.path.dirname(self.names[0]),
                                               'ts2python_output')
                    if not os.path.exists(self.outdir):  os.mkdir(self.outdir)
                    self.compilation_units = len(self.names)
                    self.worker = threading.Thread(
                        target = ts2pythonParser.batch_process,
                        args = (self.names, self.outdir),
                        kwargs = dict([('log_func', self.log_callback),
                                       ('cancel_func',
                                        self.cancel_event.is_set)]))
                    self.worker.start()
                    self.after(150, self.poll_worker)
                    self.compile['state'] = tk.DISABLED
                    self.progressbar['mode'] = "determinate"

    def on_clear_source(self):
        self.source.delete('1.0', tk.END)
        self.compile['state'] = tk.DISABLED
        self.source_clear['state'] = tk.DISABLED
        self.export_test['state'] = tk.DISABLED
        self.source_modified_sentinel = 2

    def adjust_button_status(self):
        txt = self.source.get('1.0', tk.END)
        if re.fullmatch(r'\s*', txt):
            self.compile['state'] = tk.DISABLED
            self.source_clear['state'] = tk.DISABLED
            self.export_test['state'] = tk.DISABLED
        else:
            self.compile['state'] = tk.NORMAL
            self.source_clear['state'] = tk.NORMAL
            self.export_test['state'] = tk.NORMAL

    def on_source_change(self, event):
        if self.source_modified_sentinel: # ignore call due to change of emit_modified
            self.source_modified_sentinel -= 1
            if self.source_modified_sentinel > 0:
                self.source.edit_modified(False)
            else:
                self.adjust_button_status()
                self.line_numbers.redraw()
                if self.all_results:
                    self.export_test['state'] = tk.DISABLED
        else:
            self.source_modified_sentinel = 1
            self.source.edit_modified(False)
            if self.source_paste:
                self.source_paste = False
                # Call compile, here, directly?

    def on_source_insert(self, event):
        self.source_paste = True

    def on_source_undo(self):
        try:
            self.source.edit_undo()
            self.source_modified_sentinel = 2
        except tk.TclError:
            pass  # nothing to undo-error

    def hilight_error_line(self, i):
        self.source.tag_delete("errorline")
        self.errors.tag_delete("currenterror")
        if 0 <= i < len(self.error_list):
            error = self.error_list[i]
            line, col = self.tk_error_pos(error)
            self.source.see(f"{line}.{col}")
            line_str = self.source.get(f'{line}.0', f'{line + 1}.0').strip('\n')
            self.source.tag_add("errorline", f"{line}.{0}", f"{line}.{col}")
            self.source.tag_add("errorline", f"{line}.{col + 1}", f"{line}.{len(line_str)}")
            self.source.tag_config("errorline", background="yellow")
            err_str = self.errors.get(f'{i + 1}.0', f'{i + 2}.0').strip('\n')
            self.errors.tag_add("currenterror", f"{i + 1}.{0}", f"{i + 1}.{len(err_str)}")
            self.errors.tag_config("currenterror", background="yellow")

    def show_if_error_at(self, location):
        tag_names = self.source.tag_names(location)
        l, c = map(int, location.split('.'))
        if 'error' in tag_names or 'warning' in tag_names:
            for i, e in enumerate(self.error_list):
                if e.line == l and abs(e.column - c) <= 2:
                    self.hilight_error_line(i)
        elif not any(e.line == l for e in self.error_list):
            self.hilight_error_line(-1)  # stop highlighting

    def on_source_key(self, event):
        self.show_if_error_at(self.source.index(tk.INSERT))
        # self.line_numbers.redraw()

    def on_source_mouse(self, event):
        self.show_if_error_at(self.source.index(f"@{event.x},{event.y}"))

    def tk_error_pos(self, error: Error) -> Tuple[int, int]:
        line = error.line
        col = error.column - 1
        line_str = self.source.get(f'{line}.0', f'{line + 1}.0').strip('\n')
        if 0 < col == len(line_str):  col -= 1
        return (line, col)

    def mark_error_pos(self, error):
        line, col = self.tk_error_pos(error)
        typ = 'error' if error.code >= ERROR else 'warning'
        self.source.tag_add(typ, f'{line}.{col}', f'{line}.{col + 1}')

    def compile_single_unit(self, source, target, parser):
        results = ts2pythonParser.pipeline(
            source, target, parser, cancel_query=self.cancel_event.is_set)
        if not self.cancel_event.is_set():
            self.all_results = results

    def on_compile(self):
        source = self.source.get("1.0", tk.END)
        if source.find('\n') < 0:
            if re.fullmatch(r'\s*', source):  return
            source += '\n'
        parser = self.root_parser
        self.compilation_target = self.target_name.get()
        self.compilation_units = 1
        # self.all_results = ts2pythonParser.pipeline(source, self.compilation_target, parser)
        # self.finish_single_unit()
        self.cancel_event.clear()
        self.worker = threading.Thread(
            target = self.compile_single_unit,
            args = (source, self.compilation_target, parser),
        )
        self.worker.start()
        self.progressbar['mode'] = 'indeterminate'
        self.progressbar.start()
        self.after(100, self.poll_worker)
        self.compile['state'] = tk.DISABLED
        self.save_result['state'] = tk.DISABLED
        self.export_test['state'] = tk.DISABLED
        self.file_menu.entryconfig("Save Python code...", state=tk.DISABLED)

    def finish_single_unit(self):
        self.source.tag_delete("error")
        self.source.tag_delete("errorline")
        self.errors.tag_delete("currenterror")
        self.errors.tag_delete("error")
        if self.preambel.strip():
            self.all_results['py'] = ('\n\n'.join((self.preambel,
                                                   self.all_results['py'][0])),
                                      self.all_results['py'][1])
        serialization_format = self.target_format.get()
        target = self.target_name.get()
        if target not in self.all_results:
            target = self.compilation_target
            self.target_name.set(target)
        try:
            result, self.error_list = self.all_results[target]
        except KeyError:
            result = ''
        self.compile['state'] = tk.DISABLED
        self.result.delete("1.0", tk.END)
        serialized = result.serialize(serialization_format) \
                     if isinstance(result, Node) else result
        self.result.insert("1.0", serialized)
        if not re.fullmatch(r'\s*', serialized):
            self.save_result['state'] = tk.NORMAL
            self.file_menu.entryconfig("Save Python code...", state=tk.NORMAL)
        self.export_test['state'] = tk.NORMAL
        self.errors.delete("1.0", tk.END)
        for i, e in enumerate(self.error_list):
            err_str = str(e) + '\n'
            self.errors.insert(f"{i + 1}.0", err_str)
            if e.code >= ERROR:
                self.errors.tag_add('error', f"{i + 1}.{0}",
                                    f"{i + 1}.{len(err_str)}")
        self.errors.tag_config('error', foreground='red')
        # self.errors.insert("1.0", '\n'.join(str(e) for e in self.error_list))
        for e in self.error_list:
            self.mark_error_pos(e)
        self.source.tag_config("error", background="orange red")
        self.source.tag_config("warning", background="thistle")

    def finish_multiple_units(self):
        assert self.compilation_units >= 2
        self.result.insert(tk.END, "Compilation finished.\n")
        self.result.insert(tk.END, f"Results written to {self.outdir}.\n")
        self.errors.insert(tk.END, f"Errors (if any) written to {self.outdir}.\n")
        if self.target_name.get().lower() == 'html':
            html_name = os.path.splitext(os.path.basename(self.names[0]))[0] + '.html'
            html_name = os.path.join(self.outdir, html_name)
            self.errors.insert(tk.END, html_name + "\n")
            webbrowser.open('file://' + os.path.abspath(html_name)
                            if sys.platform == "darwin" else html_name)
        else:
            webbrowser.open('file://' + os.path.abspath(self.outdir)
                            if sys.platform == "darwin" else self.outdir)

    def update_result(self, if_tree=False) -> bool:
        target = self.target_name.get()
        result = self.all_results.get(target, ("", []))
        result_txt = None
        if isinstance(result[0], Node):
            format = self.target_format.get()
            result_txt = cast(Node, result[0]).serialize(format)
        elif not if_tree:
            result_txt = result[0]
        if result_txt is not None:
            self.result.delete('1.0', tk.END)
            self.result.insert(tk.END, result_txt)
            if re.fullmatch(r'\s*', result_txt):
                self.save_result['state'] = tk.DISABLED
                self.file_menu.entryconfig("Save Python code...", state=tk.DISABLED)
            else:
                self.save_result['state'] = tk.NORMAL
                self.file_menu.entryconfig("Save Python code...", state=tk.NORMAL)
        return bool(result[0]) or bool(result[1])

    def set_presets(self, version=(3, 11)):
        access_presets()
        set_preset_value('ts2python.UsePostponedEvaluation', version < (3, 14), allow_new_key=True)
        set_preset_value('ts2python.UseLiteralType', version >= (3, 8), allow_new_key=True)
        set_preset_value('ts2python.UseTypeUnion', version >= (3, 10), allow_new_key=True)
        set_preset_value('ts2python.UseExplicitTypeAlias', version >= (3, 10), allow_new_key=True)
        set_preset_value('ts2python.UseVariadicGenerics', version >= (3, 11), allow_new_key=True)
        set_preset_value('ts2python.UseNotRequired', True, allow_new_key=True)
        set_preset_value('ts2python.UseTypeParameters', version >= (3, 12), allow_new_key=True)
        set_preset_value('ts2python.AllowReadOnly', True, allow_new_key=True)
        set_preset_value('ts2python.AssumeDeferredEvaluation', version >= (3, 14), allow_new_key=True)
        set_preset_value('ts2python.KeepMultilineComments', True, allow_new_key=True)
        finalize_presets()
        preambel = []
        t = 0
        if version < (3, 14):
            preambel.append('from __future__ import annotations')
            t = 1
        preambel.append('from typing import Union, Optional, Any, Generic, TypeVar, Callable \\\n'
                        '    List, Iterable, Iterator, Tuple, Dict, Awaitable')
        if version < (3, 13):
            if version >= (3, 12):
                preambel.append('type ReadOnly = Union')
            elif version >= (3, 10):
                preambel[t] += ', TypeAlias'
                preambel.append('ReadOnly: TypeAlias = Union')
            else:
                preambel.append('ReadOnly = Union')
        else:
            preambel[t] += ', ReadOnly'
        if version < (3, 11):
            if version >= (3, 10):
                preambel.append('NotRequired: TypeAlias = Optional')
            else:
                preambel.append('NotRequired = Optional')
        else:
            preambel[t] += ', NotRequired'
        self.preambel = '\n'.join(preambel)

    def on_version_selector(self, event):
        version_string = self.python_version.get().split(' ')[0]
        version = tuple(int(part) for part in version_string.split('.'))
        self.set_presets(version)
        self.compile['state'] = tk.NORMAL

    def on_anonymous_selector(self, event):
        method = self.render_anonymous_table[self.render_anonymous.get()]
        access_presets()
        set_preset_value('ts2python.RenderAnonymous', method, allow_new_key=True)
        finalize_presets()
        self.compile['state'] = tk.NORMAL
        if method == 'local':
            self.message['text'] = \
                "Type checkers will complain about local types inside TypedDicts!"
            self.message['style'] = "Red.TLabel"
            self.after(5000, self.clear_message)
        else:
            self.message['text'] = ""


    def on_target_stage(self, event):
        target = self.target_name.get()
        if target in ('AST', 'CST'):
            self.output_choice['state'] = tk.NORMAL
        elif isinstance(self.all_results.get(target, (EMPTY_NODE, []))[0], Node):
            self.output_choice['state'] = tk.DISABLED
        if not self.update_result():
            self.adjust_button_status()

    def on_output_choice(self, event):
        self.update_result(if_tree=True)

    def on_errors_key(self, event):
        i = int(self.errors.index(tk.INSERT).split('.')[0])
        self.hilight_error_line(i - 1)

    def on_errors_mouse(self, event):
        i = int(self.errors.index(f"@0,{event.y}").split('.')[0])
        self.hilight_error_line(i - 1)

    def on_save_result(self):
        target = self.target_name.get()
        if self.output_choice['state'] == tk.NORMAL:
            format = 'in format ' + self.target_format.get()
        else:
            format = ''
        file = tk.filedialog.asksaveasfile(
            title=f"Save {target}-results {format} as..",
            filetypes=[(target, '*.' + target), ('All', '*')]
        )
        if file:
            result = self.result.get("1.0", tk.END)
            try:
                file.write(result)
                self.message['text'] =  f'"{file.name}" written to disk.'
                self.message['style'] = "Green.TLabel"
                self.after(3500, self.clear_message)
            except (PermissionError, IOError) as e:
                tk.messagebox.showerror("IO Error", str(e))
            finally:
                file.close()

    def read_config_or_test_file(self, path: str) \
            -> Tuple[object, str, str, str, str, bool]:
        """-> (ConfigParser-object, fname, fpath, ftype, fdata, failure)"""
        import configparser
        fpath, fname = os.path.split(path)
        ftype = 'config' if fname.lower().endswith('config.ini') \
                            and not fname.lower().find('test_') >= 0 \
            else 'test'
        failure = not bool(path)
        config = configparser.ConfigParser()
        config.optionxform = lambda optionstr: optionstr
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    fdata = f.read()
                if fdata:
                    config.optionxform = lambda option: option
                    config.read_string(fdata)
                    if ftype != 'test' and any(s.find(':') >= 0
                                               for s in config.sections()):
                        ftype = 'test'
                elif ftype == 'test':
                    ftype = 'empty'
            except (PermissionError, IOError, IsADirectoryError,
                    UnicodeDecodeError) as e:
                tk.messagebox.showerror("IO Error", str(e))
                failure = True
            except configparser.Error as e:
                tk.messagebox.showerror(
                    "File-format Error",
                    f"Error in file {fname}+\n\n" + str(e))
                failure = True
        else:
            fdata = ''
            if ftype == 'test':  ftype = 'empty'
        return (config, fname, fpath, ftype, fdata, failure)

    def write_or_update_config_file(self, path, config) -> bool:
        fname = os.path.basename(path)
        empty = len(config.sections()) == 0
        ts2p_new = 'ts2python' not in config.sections()
        if ts2p_new:
            config['ts2python'] = {}
        cfg = get_config_values('ts2python.*')
        i = len('ts2python.')
        cfg = {k[i:]: str(v) for k, v in cfg.items()}
        config['ts2python'].update(cfg)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                config.write(f)
            if empty:
                self.message['text'] = f'Configuration written to "{fname}".'
            else:
                if ts2p_new:
                    self.message['text'] = f'Configuration added to "{fname}".'
                else:
                    self.message['text'] = f'Configuration updated in "{fname}".'
        except (FileNotFoundError, PermissionError,
                IsADirectoryError, IOError) as e:
            tk.messagebox.showerror("IO Error", str(e))
            return False
        return True

    def on_export_config(self):
        path = tk.filedialog.asksaveasfilename(
            title=f"Save configuration to project directory",
            initialfile='ts2pythonConfig',
            filetypes=[('.ini', '*.ini'), ('All', '*')]
        )
        if path:
            config, fname, fpath, ftype, fdata, failure = \
                self.read_config_or_test_file(path)
            if failure:
                return
            if ftype not in  ('config', 'empty'):
                tk.messagebox.showerror(
                    "File-format Error",
                    f"File {fname} is not a confiuguration file, "
                    f"but a {ftype}-file")
                return
            if self.write_or_update_config_file(path, config):
                self.message['style'] = "Green.TLabel"
                self.after(2500, self.clear_message)

    def on_export_test(self):
        from DHParser.testing import unit_to_config, unit_from_config, \
            UNIT_STAGES
        path = tk.filedialog.asksaveasfilename(
            title=f"Save or add case to test-ini-file..",
            filetypes=[('Test', '.ini'), ('All', '*')]
        )
        config, fname, fpath, ftype, fdata, failure = \
            self.read_config_or_test_file(path)
        if failure:  return
        if ftype == 'config':
            self.write_or_update_config_file(path, config)
        else:
            if ftype == 'test':
                stages = (UNIT_STAGES
                    | frozenset(j.dst for j in ts2pythonParser.junctions))
                suite = unit_from_config(fdata, fname, allowed_stages=stages)
                if 'config__' in suite:
                    cfg = get_config_values('ts2python.*')
                    for k, v in suite['config__'].items():
                        if k not in cfg or cfg[k] != eval(v):
                            empty = '""'
                            tk.messagebox.showerror(
                                "Configuration mismatch",
                                f'Configuration in file "{fname}" '
                                "does not match current configuration, "
                                f'e.g.\n{k}="{v}" instead of '
                                f'"{cfg.get(k, empty)}"')
                            return
                    del suite['config__']
            else:
                suite = {}
            source = self.source.get("1.0", tk.END)
            parser = self.root_parser
            if self.error_list:
                error_level = max(e.code for e in self.error_list)
            else:
                error_level = 0
            cases = { 'M1': source.replace('\t', '    ') }
            tests = { 'match': cases }
            if error_level < ERROR:
                for stage, result in self.all_results.items():
                    if stage.upper() == 'CST':  continue
                    cases = { 'M1': result[0].serialize()
                                    if isinstance(result[0], Node)
                                    else result[0] }
                    tests[stage] = cases
            unit = { parser: tests }
            cfg_data = dump_config_data('ts2python.*', use_headings=False)
            suite = merge_test_units(suite, unit)
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    if cfg_data:
                        f.write('[config]\n')
                        f.write(cfg_data)
                        f.write('\n')
                    f.write(unit_to_config(suite))
                if ftype == "empty":
                    self.message['text'] = f'Test-file "{fname}" written to disk.'
                elif ftype == "test":
                    self.message['text'] = f'Test-case added to file "{fname}".'
            except (FileNotFoundError, PermissionError,
                    IsADirectoryError, IOError) as e:
                tk.messagebox.showerror("IO Error", str(e))
                return
        self.message['style'] = "Green.TLabel"
        self.after(2500, self.clear_message)

    def on_cancel(self) -> bool:
        if self.worker:
            if tk.messagebox.askyesno(
                title="Cancel?",
                message="A parsing/compilation-process is still under way!\n"
                        "Cancel running process?"):
                self.update()
                self.update_idletasks()
                if self.worker:
                    self.cancel_event.set()
                    self.errors.insert(tk.END, "Canceling reaming tasks...\n")
                    self.update()
                    self.update_idletasks()
                    self.worker.join(5.0)
                    if not self.worker.is_alive():
                        self.message['text'] = "Parsing/Compilation canceled"
                        self.message['style'] = "Red.TLabel"
                        self.after(2500, self.clear_message)
                    self.errors.yview_moveto(1.0)
                    self.adjust_button_status()
                    return True
                else:
                    return False
        return True

    def open_docs(self):
        import webbrowser
        webbrowser.open('https://ts2python.readthedocs.io/')

    def open_github(self):
        import webbrowser
        webbrowser.open('https://github.com/jecki/ts2python/')

    def open_license(self):
        import webbrowser
        webbrowser.open('https://github.com/jecki/ts2python/blob/master/LICENSE')

    def on_about(self):
        import random
        slogans = ("'cause it is the machines that bring order to life!",
                   "We work hard to make your job expendable!",
                   "We program pig systems that make your life difficult!",
                   "8 bit can do it all!",
                   "The apparatus is always right!",
                   "Everyone is replaceable and should be!")
        tk.messagebox.showinfo(
            title="About ts2python",
            message=("ts2python was brought to you by:\n\n"
                     "SLAVES TO THE MACHINE SOFTWARE\n\n"
                     + slogans[random.randint(0, len(slogans) - 1)] + '\n\n')
        )

    def on_close(self):
        if self.on_cancel():
            if self.worker and self.worker.is_alive():
                self.errors.insert(tk.END, "Killing still running processes!\n")
                self.errors.yview_moveto(1.0)
            self.mc_manager.shutdown()
            self.destroy()
            self.quit()


def main():
    read_local_config(os.path.join(scriptdir, 'ts2pythonConfig.ini'))
    if not ts2pythonParser.main(called_from_app=True):
        app = ts2pythonApp()
        app.mainloop()

if __name__ == '__main__':
    if sys.version_info < (3, 14, 0):
        import multiprocessing
        multiprocessing.freeze_support()
    main()

