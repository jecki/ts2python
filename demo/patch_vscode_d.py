#!/usr/bin/env python3

"""Adds an empty PromiseLike-dummy class to vscode.d.py"""

import sys

def patch_vscode_d_py():
    with open("vscode.d.py", 'r', encoding='utf-8') as f:
        vscode_d = f.read()
    i = vscode_d.find("import sys")
    i = vscode_d.find("\n", i) + 1
    vscode_d = ''.join([vscode_d[:i], "import os\nsys.path.append(os.path.abspath('..'))\n", vscode_d[i:]])
    i = vscode_d.find('PromiseLike')
    i = vscode_d.rfind('\n', 0, i)
    vscode_d = ''.join([vscode_d[:i],
                        "\n\nPromiseLike = List  # just a hack, won't appear in production code ;-) \n",
                        vscode_d[i:]])
    with open("vscode.d.py", 'w', encoding='utf-8') as f:
        f.write(vscode_d)

if __name__ == '__main__':
    patch_vscode_d_py()
