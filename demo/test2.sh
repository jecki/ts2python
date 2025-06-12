#!/usr/bin/env bash

export PYTHONPATH=../:$PYTHONPATH


echo "Testing python3.14 compatibility"
python3.14 ../ts2pythonParser.py --compatibility 3.14 vscode.d.ts
python3.14 patch_vscode_d.py
python3.14 vscode.d.py

echo "Testing python3.13 compatibility"
python3.13 ../ts2pythonParser.py --compatibility 3.13 vscode.d.ts
python3.13 patch_vscode_d.py
python3.13 vscode.d.py

echo "Testing python3.12 compatibility"
python3.12 ../ts2pythonParser.py --compatibility 3.12 vscode.d.ts
python3.12 patch_vscode_d.py
python3.12 vscode.d.py

echo "Testing python3.11 compatibility"
python3.11 ../ts2pythonParser.py --compatibility 3.11 vscode.d.ts
python3.11 patch_vscode_d.py
python3.11 vscode.d.py

echo "Testing python3.10 compatibility"
python3.10 ../ts2pythonParser.py --compatibility 3.10 vscode.d.ts
python3.10 patch_vscode_d.py
python3.10 vscode.d.py

echo "Testing pypy3 (3.10) compatibility"
pypy3 ../ts2pythonParser.py --compatibility 3.10 vscode.d.ts
pypy3 patch_vscode_d.py
pypy3 vscode.d.py

echo "Testing python3.9 compatibility"
python3.9 ../ts2pythonParser.py --compatibility 3.9 vscode.d.ts
python3.9 patch_vscode_d.py
python3.9 vscode.d.py

echo "Testing python3.8 compatibility"
python3.8 ../ts2pythonParser.py --compatibility 3.8 vscode.d.ts
python3.8 patch_vscode_d.py
python3.8 vscode.d.py

echo "Testing python3.7 compatibility"
python3.7 ../ts2pythonParser.py --compatibility 3.7 vscode.d.ts
python3.7 patch_vscode_d.py
python3.7 vscode.d.py
