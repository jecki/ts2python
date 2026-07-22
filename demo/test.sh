#!/usr/bin/env bash

export PYTHONPATH=../:$PYTHONPATH


echo "Testing python3.14 compatibility"
python3.14 ../ts2pythonParser.py --compatibility 3.14 specification.ts
python3.14 specification.py

echo "Testing python3.13 compatibility"
rm specification.py
python3.13 ../ts2pythonParser.py --compatibility 3.13 specification.ts
python3.13 specification.py

echo "Testing python3.12 compatibility"
rm specification.py
python3.12 ../ts2pythonParser.py --compatibility 3.12 specification.ts
python3.12 specification.py

echo "Testing python3.11 compatibility"
rm specification.py
python3.11 ../ts2pythonParser.py --compatibility 3.11 specification.ts
python3.11 specification.py

echo "Testing python3.10 compatibility"
rm specification.py
python3.10 ../ts2pythonParser.py --compatibility 3.10 specification.ts
python3.10 specification.py

echo "Testing pypy3 (3.10) compatibility"
rm specification.py
pypy3 ../ts2pythonParser.py --compatibility 3.10 specification.ts
pypy3 specification.py

echo "Testing python3.9 compatibility"
rm specification.py
python3.9 ../ts2pythonParser.py --compatibility 3.9 specification.ts
python3.9 specification.py

echo "Testing python3.8 compatibility"
rm specification.py
python3.8 ../ts2pythonParser.py --compatibility 3.8 specification.ts
python3.8 specification.py

echo "Testing python3.7 compatibility"
rm specification.py
python3.8 ../ts2pythonParser.py --compatibility 3.7 specification.ts
python3.7 specification.py
