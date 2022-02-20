#!/usr/bin/env bash

echo "ts2python demo: Converts the current specifications of the lanugage server protocol to python"
python extract_ts_from_lsp_specs.py https://raw.githubusercontent.com/microsoft/language-server-protocol/gh-pages/_specifications/specification-current.md
python ../ts2pythonParser.py specification-current.ts
echo "Checking specification-current.py..."
python specification-current.py
echo "Now have a look at specification-current.py :-)"
