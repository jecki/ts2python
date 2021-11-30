"""__init__.py - package definition module for ts2python

Copyright 2021  by Eckhart Arnold (arnold@badw.de)
                Bavarian Academy of Sciences an Humanities (badw.de)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied.  See the License for the specific language governing
permissions and limitations under the License.
"""

import sys
assert sys.version_info >= (3, 6, 0), "ts2python requires at least Python-Version 3.6!"

__title__ = "ts2python"
__version__ = "0.5"
__version_info__ = tuple(int(part) for part in __version__.split('.'))
__description__ = "Python-Interoperability for Typescript-Interfaces"
__author__ = "Eckhart Arnold"
__email__ = "eckhart.arnold@posteo.de"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__copyright__ = "Copyright (C) Eckhart Arnold 2021"

