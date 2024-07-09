#!/usr/bin/env bash

echo "ts2python demo: Converts the current specifications of the lanugage server protocol to python"
python3.8 extract_ts_from_lsp_specs.py https://raw.githubusercontent.com/microsoft/language-server-protocol/gh-pages/_specifications/lsp/3.18/specification.md
python3 ../ts2pythonParser.py specification.ts
echo "Checking specification.py..."
export PYTHONPATH=../:$PYTHONPATH
python3 specification.py
echo "Now have a look at specification.py :-)"
