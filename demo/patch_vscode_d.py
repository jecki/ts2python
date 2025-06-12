#!/usr/bin/env python3

"""Adds an empty PromiseLike-dummy class to vscode.d.py"""

import sys

def patch_vscode_d_py():
    with open("vscode.d.py", 'r', encoding='utf-8') as f:
        vscode_d = f.read()
    i = vscode_d.find('PromiseLike')
    i = vscode_d.rfind('\n', 0, i)
    if sys.version_info >= (3, 12):
        vscode_d = ''.join([vscode_d[:i], "\n\nclass PromiseLike[T]:\n    pass\n\n", vscode_d[i:]])
    else:
        vscode_d = ''.join([vscode_d[:i], "\n\nclass PromiseLike:\n    pass\n\n", vscode_d[i:]])
    with open("vscode.d.py", 'w', encoding='utf-8') as f:
        f.write(vscode_d)

if __name__ == '__main__':
    patch_vscode_d_py()
