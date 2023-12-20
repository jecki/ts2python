#!/usr/bin/env python3

"""extract_ts_from_lsp.py - extracts the typescript parts from the
specification of the language server protocol:
https://github.com/microsoft/language-server-protocol/tree/gh-pages/_specifications
"""

import re


LSP_SPEC_SOURCE = \
    "https://raw.githubusercontent.com/microsoft/language-server-protocol/" \
    "gh-pages/_specifications/lsp/3.18/specification.md"


def no_declaration(l):
    if l[0:1] in ("{", "["):
        return True
    if re.match(r'\w+(?:\.\w+)*\(', l):
        return True
    return False


def extract(specs, dest):
    lines = specs.split('\n')
    ts = []
    copy_flag = False
    for l in lines:
        if l.strip() == '```typescript':
            copy_flag = True
        elif l.strip() == '```':
            copy_flag = False
            ts.append('')
        else:
            if copy_flag:
                if no_declaration(l):
                    copy_flag = False
                elif l[0:2] != "//":
                    ts.append(l)
    with open(dest, 'w', encoding='utf-8') as f:
        f.write('\n'.join(ts))


def download_specfile(url: str) -> str:
    import urllib.request
    max_indirections = 2
    while max_indirections > 0:
        if url.startswith('http:') or url.startswith('https:'):
            print('fetching: ' + url)
            with urllib.request.urlopen(url) as f:
                specs = f.read()
        else:
            with open(url, 'rb') as f:
                specs = f.read()
        if len(specs) < 255 and specs.find(b'\n') < 0:
            url = url[: url.rfind('/') + 1] + specs.decode('utf-8').strip()
            max_indirections -= 1
        else:
            max_indirections = 0
    return specs.decode('utf-8')


RX_INCLUDE = re.compile(r'{%\s*include_relative\s*(?P<relative>[A-Za-z0-9/.]+?\.md)\s*%}|{%\s*include\s*(?P<absolute>[A-Za-z0-9/.]+?\.md)\s*%}')


def download_specs(url: str) -> str:
    specfile = download_specfile(url)
    relurl_path = url[:url.rfind('/') + 1]
    absurl_path = url[:url.find('_specifications/')] + '_includes/'
    parts = []
    e = 0
    for m in RX_INCLUDE.finditer(specfile):
        s = m.start()
        parts.append(specfile[e:s])
        if m.group('relative') is not None:
            incpath = m.group('relative')
            incl_url = relurl_path + incpath
        else:
            assert m.group('absolute') is not None
            incpath = m.group('absolute')
            incl_url = absurl_path + incpath
        parts.append(f'\n```typescript\n\n/* source file: "{incpath}" */\n```\n')
        include = download_specs(incl_url)
        parts.append(include)
        e = m.end()
    parts.append(specfile[e:])
    specs = ''.join(parts)
    return specs


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
        if url.startswith('www.'):  url = 'https://' + url
    else:
        url = LSP_SPEC_SOURCE
    name = url[url.rfind('/') + 1:]
    i = name.rfind('.')
    if i < 0: i = len(name)
    destname = name[:i] + '.ts'
    specs = download_specs(url)
    extract(specs, destname)

