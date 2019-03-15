# Different XML stream functions
import json
from .mdict import *

def jsonstream(fn):
    with open(fn,'r') as f:
        res = json.load(f)
    for x in res:
        yield mdict.to_mdict(x)
