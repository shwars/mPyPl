# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

import os
from pipe import *
import functools 

def readlines(fn):
    """
    Read all lines from a file into a list
    :param fn: filename
    :return: list of lines from the file
    """
    with open(fn) as f:
        content = f.readlines()
    return [x.strip() for x in content]

def writelines(fn,lst):
    """
    Writes all lines in a given list to a text file
    :param fn: filename
    :param lst: list of strings
    """
    with open(fn,'w') as f:
        for s in lst:
            f.write(s+'\n')

def read_dict_text(fn):
    """
    Read a dictionary with several sections from plain text format. Section is denoted by first character being '#'.
    Returns dictionary of lists
    :param fn: filename
    :return: Dictionary with a list of lines for each section
    """
    dict = {}
    lines = []
    prevsec = ""
    with open(fn) as f:
        for x in f.readlines():
            x = x.strip()
            if x[0]=='#': # section
                if len(lines)>0 and prevsec!="":
                    dict[prevsec] = lines
                    lines=[]
                    prevsec = x[1:]
            else:
                lines.append(x)
    if len(lines) > 0 and prevsec != "":
        dict[prevsec] = lines
    return dict

def write_dict_text(fn,dict):
    """
    Writes all lines in a section dictionary to a file. Each key in the dictionary should have a list of lines associated with it.
    :param fn: filename
    :param dict: dictionary of the form `{ "section 1" : [....], ...}`
    """
    with open(fn,'w') as f:
        for k,v in dict.items():
            f.write('#'+k+'\n')
            for x in v:
                f.write(x+'\n')


# Directory manipulations

def get_files(data_dir, ext=None):
    """
    Get a list of files from the given directory with specified extension
    """
    if ext is not None:
        return os.listdir(data_dir) \
            | where(lambda p: p.endswith(ext)) \
            | select( lambda p: os.path.join(data_dir,p))
    else:
        return os.listdir(data_dir) \
            | select( lambda p: os.path.join(data_dir,p))
