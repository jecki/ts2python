#!/usr/bin/env python3

"""extract_ts_from_lsp.py - extracts the typescript parts from the
specification of the language server protocol:
https://github.com/microsoft/language-server-protocol/tree/gh-pages/_specifications
"""

LSP_SPEC_SOURCE = \
    "https://raw.githubusercontent.com/microsoft/language-server-protocol/" \
    "gh-pages/_specifications/specification-3-16.md"


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
                ts.append(l)
    with open(dest, 'w', encoding='utf-8') as f:
        f.write('\n'.join(ts))


def download_specs(url: str) -> str:
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
        if len(specs) < 255:
            url = url[: url.rfind('/') + 1] + specs.decode('utf-8').strip()
            max_indirections -= 1
        else:
            max_indirections = 0
    return specs.decode('utf-8')


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

