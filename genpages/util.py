#
# microtome - Tim Conkling, 2012

import re
from collections import namedtuple
import os

LineData = namedtuple("LineData", ["line_num", "col"])

def line_data_at_index (str, idx):
    '''returns the string's line number and line column number at the given index'''
    # count the number of newlines up to idx
    pattern = re.compile(r'\n')
    line_num = 0
    col = idx
    pos = 0
    while True:
        match = pattern.search(str, pos)
        if match is None or match.end() > idx:
            break
        pos = match.end()
        line_num += 1
        col = idx - pos

    return LineData(line_num = line_num, col = col)

def abspath (path):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(this_dir, path)

def strip_package (typename):
    '''com.microtome.Foo -> Foo'''
    idx = typename.rfind(".")
    return typename[idx+1:] if idx >= 0 else typename

def get_package (typename):
    '''com.microtome.Foo -> com.microtome'''
    idx = typename.rfind(".")
    return typename[:idx] if idx >= 0 else ""

def qualified_name (namespace, typename):
    '''appends a namespace to a typename'''
    return namespace + "." + typename if len(namespace) > 0 else typename

