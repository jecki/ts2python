#!/usr/bin/env bash

echo "ts2python demo: Converts the current specifications of the lanugage server protocol to python"
python extract_ts_from_lsp_specs.py https://raw.githubusercontent.com/microsoft/language-server-protocol/gh-pages/_specifications/specification-3-16.md
python ../ts2pythonParser.py specification-3-16.ts
echo "Checking specification-3-16.py..."
python specification-3-16.py
echo "Now have a look at specification-3-16.py :-)"
