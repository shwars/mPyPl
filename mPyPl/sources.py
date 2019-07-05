# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

from .mdict import *
import csv

def csvsource(fn,sep=',',encoding=None):
    """
    Create a data source from CSV file
    :param fn: Filename
    :param sep: Separator to use. Defaults to ','
    :return: Sequence of mdict object representing CSV data. Field names are taken from first line
    """
    with open(fn, newline='',encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile,delimiter=sep)
        for row in reader:
            yield mdict(row)
