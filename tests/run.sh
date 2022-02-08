#!/usr/bin/sh

echo "Running unit-tests of ts2python"

python3.11 runner.py
python3.10 runner.py
python3.9 runner.py
python3.8 runner.py
python3.7 runner.py
python3.6 runner.py
pypy3 runner.py

echo "Running grammar tests of ts2python"

python3.11 ../tst_ts2python_grammar.py
python3.10 ../tst_ts2python_grammar.py
python3.9 ../tst_ts2python_grammar.py
python3.8 ../tst_ts2python_grammar.py
python3.7 ../tst_ts2python_grammar.py
python3.6 ../tst_ts2python_grammar.py
pypy3 ../tst_ts2python_grammar.py
