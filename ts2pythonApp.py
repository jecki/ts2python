#!/usr/bin/env python3

"""ts2pythonApp.py - a simple GUI for the compilation of ts2python-files"""

import sys
import os
import re
import threading
from typing import cast, Tuple

import tkinter as tk
import webbrowser
from tkinter import ttk
from tkinter import filedialog, messagebox, scrolledtext, font

from DHParser.error import Error, ERROR
from DHParser.nodetree import Node, EMPTY_NODE
from DHParser.pipeline import full_pipeline, PipelineResult

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
        self.text_widget = text_widget
        self.text_widget.bind('<KeyRelease>', self.redraw)
        self.text_widget.bind('<MouseWheel>', self.redraw)
        self.text_widget.bind('<Button-1>', self.redraw)
        self.text_widget.bind('<Configure>', self.redraw)
        self.redraw()

    def redraw(self, event=None):
        self.delete("all")
        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum)
            i = self.text_widget.index(f"{i}+1line")


class ts2pythonApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title('ts2python App')
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

        # widget-variables
        self.num_sources = 0
        self.num_compiled = 0
        self.progress = tk.IntVar()
        self.progress.set(0)

        self.source_modified_sentinel = 0
        self.source_paste = False
        grammar = ts2pythonParser.parsing.factory()
        self.parser_names = grammar.parser_names__[:]
        # self.parser_names.remove(grammar.root__.pname)
        self.parser_names.sort(key=lambda s: s.lower().lstrip('_'))
        # self.parser_names.insert(0, grammar.root__.pname)
        # self.root_name = tk.StringVar(value=grammar.root__.pname)
        self.root_name = tk.StringVar(value="document")

        self.all_results: PipelineResult = {}

        self.targets = [j.dst for j in ts2pythonParser.junctions]
        self.targets.sort(key=lambda s: s in ts2pythonParser.targets)
        self.target_name = tk.StringVar(value=list(ts2pythonParser.targets)[0])
        self.target_format = tk.StringVar(value="XML")
        self.error_list = []

        self.default_font = font.nametofont("TkDefaultFont")
        font_properties = self.default_font.actual()
        family, size = font_properties['family'], font_properties['size']
        self.bold_label = ttk.Style()
        self.bold_label.configure("Bold.TLabel", font=(family, size, "bold"))
        self.bold_button = ttk.Style()
        self.bold_button.configure("BoldRed.TButton", font=(family, size, "bold"),
                                   foreground="red")

        self.create_widgets()
        self.connect_events()
        self.place_widgets()

        self.lock = threading.Lock()
        self.worker = None
        self.compilation_units = 0
        self.cancel_flag = False

        self.outdir = ''
        self.names = []

        self.deiconify()

    def create_widgets(self):
        self.pick_source_info = ttk.Label(text="Paste source code below or...")
        self.pick_source = ttk.Button(text="Pick Source file(s)...",
                                      command=self.on_pick_source)
        self.source_info = ttk.Label(text='Source:', style="Bold.TLabel")
        self.source_undo = ttk.Button(text="Undo", command=self.on_source_undo)
        self.source_clear = ttk.Button(text="Clear source", command=self.on_clear_source)
        self.source_clear['state'] = tk.DISABLED
        self.source = scrolledtext.ScrolledText(undo=True)
        self.line_numbers = TextLineNumbers(self.source)
        self.root_parser = ttk.Combobox(self, values=self.parser_names, textvariable=self.root_name)
        self.compile = ttk.Button(text="Compile", style="BoldRed.TButton", command=self.on_compile)
        self.compile['state'] = tk.DISABLED
        self.target_stage = ttk.Combobox(self, values=self.targets, textvariable=self.target_name)
        self.target_choice = ttk.Combobox(
            self, values=['XML', 'SXML', 'sxpr', 'xast', 'ndst', 'tree'],
            textvariable=self.target_format)
        if self.target_name.get() not in ('AST', 'CST'):
            self.target_choice['state'] = tk.DISABLED
        self.result_info = ttk.Label(text='Result:', style="Bold.TLabel")
        self.result = scrolledtext.ScrolledText()
        # self.result['state'] = tk.DISABLED
        self.save_result = ttk.Button(text="Save result...", command=self.on_save_result)
        self.save_result['state'] = tk.DISABLED
        self.export_test = ttk.Button(text="Export as test case...", command=self.on_export_test)
        self.export_test['state'] = tk.DISABLED
        self.errors_info = ttk.Label(text='Errors:', style="Bold.TLabel")
        self.errors = scrolledtext.ScrolledText()
        # self.errors['state'] = tk.DISABLED
        self.progressbar = ttk.Progressbar(orient="horizontal", variable=self.progress)
        self.cancel = ttk.Button(text="Cancel", command=self.on_cancel)
        self.cancel['state'] = tk.DISABLED
        self.message = ttk.Label(text='')
        self.exit = ttk.Button(text="Quit", command=self.on_close)

    def connect_events(self):
        self.source.bind("<<Modified>>", self.on_source_change)
        self.source.bind("<Control-v>", self.on_source_insert)
        self.source.bind("<Command-v>", self.on_source_insert)
        self.source.bind("<KeyRelease>", self.on_source_key)
        self.source.bind("<Button-1>", self.on_source_mouse)
        self.target_stage.bind("<<ComboboxSelected>>", self.on_target_stage)
        self.target_choice.bind("<<ComboboxSelected>>", self.on_target_choice)
        self.root_parser.bind("<<ComboboxSelected>>", self.on_root_parser)
        self.errors.bind('<KeyRelease>', self.on_errors_key)
        # self.errors.bind('<MouseWheel>', self.on_errors_mouse)
        self.errors.bind('<Button-1>', self.on_errors_mouse)
        # self.errors.bind('<Configure>', self.on_errors)

    def place_widgets(self):
        padW = dict(sticky=(tk.W,), padx="5", pady="5")
        padE = dict(sticky=(tk.E,), padx="5", pady="5")
        padWE = dict(sticky=(tk.W, tk.E), padx="5", pady="5")
        padAll = dict(sticky=(tk.N, tk.S, tk.W, tk.E), padx="5", pady="5")
        padNW = dict(sticky=(tk.W, tk.N), padx="5", pady="5")
        self.pick_source_info.grid(row=0, column=2, **padW)
        self.pick_source.grid(row=0, column=3, **padW)
        self.source_info.grid(row=0, column=0, **padW)
        self.source_undo.grid(row=0, column=4, **padE)
        self.source_clear.grid(row=0, column=5, **padE)
        self.source.grid(row=1, column=1, columnspan=5, **padAll)
        self.line_numbers.grid(row=1, column=0, **padAll)
        self.root_parser.grid(row=2, column=2, **padE)
        self.compile.grid(row=2, column=3, **padWE)
        self.target_stage.grid(row=2, column=4, **padW)
        self.target_choice.grid(row=2, column=5, **padE)
        self.result_info.grid(row=2, column=0, **padW)
        self.result.grid(row=3, column=0, columnspan=6, **padAll)
        self.save_result.grid(row=4, column=3, **padWE)
        self.export_test.grid(row=4, column=4, **padWE)
        self.errors_info.grid(row=4, column=0, **padW)
        self.errors.grid(row=5, column=0, columnspan=6, **padAll)
        self.progressbar.grid(row=6, column=0, columnspan=5, **padWE)
        self.cancel.grid(row=6, column=5, **padE)
        self.message.grid(row=7, column=0, columnspan=5, **padWE)
        self.exit.grid(row=7, column=5, **padE)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, weight=2)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(4, weight=1)
        self.source.focus_set()

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

    def cancel_callback(self) -> bool:
        with self.lock:
            res = self.cancel_flag
        return res

    def poll_worker(self):
        self.update_idletasks()
        if self.worker and self.worker.is_alive():
            if self.cancel['stat'] != tk.NORMAL:
                self.cancel['stat'] = tk.NORMAL
            self.after(500, self.poll_worker)
        else:
            self.cancel['stat'] = tk.DISABLED
            if self.cancel_flag:
                self.result.yview_moveto(1.0)
                self.cancel_flag = False
            elif self.compilation_units == 1:
                self.finish_single_unit()
            else:
                self.finish_multiple_units()
            self.worker = None
            self.compilation_units = 0
            self.compilation_target = ""

    def on_pick_source(self):
        if not self.worker or self.on_cancel():
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
                if len(self.names) == 1:
                    try:
                        with open(self.names[0], 'r', encoding='utf-8') as f:
                            snippet = f.read()
                            self.source.insert(tk.END, snippet)
                    except (FileNotFoundError, PermissionError,
                            IsADirectoryError, IOError) as e:
                        self.result.insert(tk.END, str(e))
                else:
                    self.num_sources = len(self.names)
                    self.num_compiled = 0
                    self.outdir = os.path.join(os.path.dirname(self.names[0]),
                                               'ts2python_output')
                    if not os.path.exists(self.outdir):  os.mkdir(self.outdir)
                    with self.lock:  self.cancel_flag = False
                    self.compilation_units = len(self.names)
                    self.worker = threading.Thread(
                        target = ts2pythonParser.batch_process,
                        args = (self.names, self.outdir),
                        kwargs = dict([('log_func', self.log_callback),
                                       ('cancel_func', self.cancel_callback)]))
                    self.worker.start()
                    # self.cancel['stat'] = tk.NORMAL
                    self.after(100, self.poll_worker)

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

    def on_clear_source(self):
        self.source.delete('1.0', tk.END)
        self.compile['stat'] = tk.DISABLED
        self.source_clear['stat'] = tk.DISABLED
        self.source_modified_sentinel = 2

    def on_source_change(self, event):
        if self.source_modified_sentinel: # ignore call due to change of emit_modified
            self.source_modified_sentinel -= 1
            if self.source_modified_sentinel > 0:
                self.source.edit_modified(False)
            else:
                txt = self.source.get('1.0', tk.END)
                if re.fullmatch(r'\s*', txt):
                    self.compile['stat'] = tk.DISABLED
                    self.source_clear['stat'] = tk.DISABLED
                else:
                    self.compile['stat'] = tk.NORMAL
                    self.source_clear['stat'] = tk.NORMAL
        else:
            self.source_modified_sentinel = 1
            self.source.edit_modified(False)
            if self.source_paste:
                self.source_paste = False
                # Call compile here, directly

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
        results = ts2pythonParser.pipeline(source, target, parser)
        with self.lock:
            if not self.cancel_flag:
                self.all_results = results

    def on_compile(self):
        source = self.source.get("1.0", tk.END)
        if source.find('\n') < 0:
            if not source.strip():  return
            source += '\n'
        parser = self.root_name.get()
        self.compilation_target = self.target_name.get()
        self.compilation_units = 1
        # self.all_results = ts2pythonParser.pipeline(source, self.compilation_target, parser)
        # self.finish_single_unit()
        self.worker = threading.Thread(
            target = self.compile_single_unit,
            args = (source, self.compilation_target, parser)
        )
        self.worker.start()
        self.after(100, self.poll_worker)

    def finish_single_unit(self):
        self.source.tag_delete("error")
        self.source.tag_delete("errorline")
        self.errors.tag_delete("currenterror")
        self.errors.tag_delete("error")
        serialization_format = self.target_format.get()
        target = self.target_name.get()
        if target not in self.all_results:
            target = self.compilation_target
            self.target_name.set(target)
        result, self.error_list = self.all_results[target]
        self.compile['stat'] = tk.DISABLED
        self.result.delete("1.0", tk.END)
        self.result.insert("1.0", result.serialize(serialization_format)
                           if isinstance(result, Node) else result)
        self.errors.delete("1.0", tk.END)
        for i, e in enumerate(self.error_list):
            err_str = str(e) + '\n'
            self.errors.insert(f"{i + 1}.0", err_str)
            if e.code >= ERROR:
                self.errors.tag_add('error', f"{i + 1}.{0}", f"{i + 1}.{len(err_str)}")
        self.errors.tag_config('error', foreground='red')
        # self.errors.insert("1.0", '\n'.join(str(e) for e in self.error_list))
        for e in self.error_list:
            self.mark_error_pos(e)
        self.source.tag_config("error", background="orange red")
        self.source.tag_config("warning", background="thistle")

    def update_result(self, if_tree=False) -> bool:
        target = self.target_name.get()
        result = self.all_results.get(target, ("", []))
        if isinstance(result[0], Node):
            format = self.target_format.get()
            result_txt = cast(Node, result[0]).serialize(format)
            self.result.delete('1.0', tk.END)
            self.result.insert(tk.END, result_txt)
        elif not if_tree:
            self.result.delete('1.0', tk.END)
            self.result.insert(tk.END, result[0])
        return bool(result[0]) or bool(result[1])

    def on_target_stage(self, event):
        target = self.target_name.get()
        if target in ('AST', 'CST'):
            self.target_choice['state'] = tk.NORMAL
        elif isinstance(self.all_results.get(target, (EMPTY_NODE, []))[0], Node):
            self.target_choice['state'] = tk.DISABLED
        if not self.update_result():
            self.compile['stat'] = tk.NORMAL

    def on_target_choice(self, event):
        self.update_result(if_tree=True)

    def on_root_parser(self, event):
        self.update_result(if_tree=True)
        self.compile['stat'] = tk.NORMAL

    def on_errors_key(self, event):
        i = int(self.errors.index(tk.INSERT).split('.')[0])
        self.hilight_error_line(i - 1)

    def on_errors_mouse(self, event):
        i = int(self.errors.index(f"@0,{event.y}").split('.')[0])
        self.hilight_error_line(i - 1)

    def on_save_result(self):
        pass

    def on_export_test(self):
        pass

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

